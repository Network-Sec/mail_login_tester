#!/usr/bin/env python3

import argparse
import json
import imaplib
import smtplib
import poplib
import os
from termcolor import colored
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket

# Global configuration
TIMEOUT = 10  # seconds

# Load configuration from JSON file
def load_config(config_file='mail_services.json'):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, config_file)
    if verbose:
        print(f"[V] Script Dir: {script_dir} | Config Path: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

# Function to test IMAP login
def test_imap(email, password, config, verbose=False):
    if verbose: print(f"[V] Thread started for IMAP testing {email}")
    try:
        if verbose: print(f"[V] Testing IMAP for {email}")
        with imaplib.IMAP4_SSL(config['host'], config['port']) as mail:
            mail.socket().settimeout(TIMEOUT)
            mail.login(email, password)
            return True
    except (imaplib.IMAP4.error, socket.timeout) as e:
        if verbose: print(colored(f"[-] IMAP operation timed out or failed: {e}", "red"))
        return False
    except Exception as e:
        if verbose: print(f"IMAP error: {e}")
        return False

# Function to test SMTP login
def test_smtp(email, password, config, verbose=False):
    if verbose: print(f"[V] Thread started for SMTP testing {email}")
    try:
        if verbose: print(f"[V] Testing SMTP for {email}")
        if config['tls']:
            server = smtplib.SMTP(config['host'], config['port'], timeout=TIMEOUT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config['host'], config['port'], timeout=TIMEOUT)
        server.login(email, password)
        server.quit()
        return True
    except (smtplib.SMTPException, socket.timeout) as e:
        if verbose: print(colored(f"[-] SMTP operation timed out or failed: {e}", "red"))
        return False
    except Exception as e:
        if verbose: print(f"SMTP error: {e}")
        return False

# Function to test POP3 login
def test_pop3(email, password, config, verbose=False):
    if verbose: print(f"[V] Thread started for POP3 testing {email}")
    try:
        if verbose: print(f"[V] Testing POP3 for {email}")
        if config['tls']:
            mail = poplib.POP3_SSL(config['host'], config['port'], timeout=TIMEOUT)
        else:
            mail = poplib.POP3(config['host'], config['port'], timeout=TIMEOUT)
        mail.user(email)
        mail.pass_(password)
        mail.quit()
        return True
    except (poplib.error_proto, socket.timeout) as e:
        if verbose: print(colored(f"[-] POP3 operation timed out or failed: {e}", "red"))
        return False
    except Exception as e:
        if verbose: print(f"POP3 error: {e}")
        return False

# Function to load inputs from file or single value
def load_inputs(input_str):
    if os.path.isfile(input_str):
        with open(input_str, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    else:
        return [input_str]

# Function to construct email addresses based on username or domain
def construct_email_addresses(username, config):
    email_addresses = []
    if '@' in username:
        email_addresses.append(username)
    else:
        temp_addresses = []
        for service, details in config.items():
            for san in details.get("SANs", []):
                for tld in details.get("TLDs", []):
                    temp_addresses.append(f"{username}@{san}.{tld}")
        
        # Ensure maximum alternation - after GMX should not follow another GMX for rate limit
        service_dict = {}
        for email in temp_addresses:
            domain = email.split('@')[1].split('.')[0]
            if domain not in service_dict:
                service_dict[domain] = []
            service_dict[domain].append(email)
        
        sorted_services = sorted(service_dict.values(), key=len, reverse=True)
        address_cycle = cycle(sorted_services)

        while any(sorted_services):
            for addresses in address_cycle:
                if addresses:
                    email_addresses.append(addresses.pop(0))

    return email_addresses

# Function to test a single credential
def test_single_credential(email, password, config, verbose):
    service = get_service_from_email(email, config)
    if not service:
        if verbose:
            print(colored(f"[-] No service configuration found for email: {email}", "red"))
        return None
    if verbose:
        print(f"[V] Testing {email} with service {service}")
    imap_result = test_imap(email, password, config[service]['imap'], verbose)
    smtp_result = test_smtp(email, password, config[service]['smtp'], verbose)
    pop3_result = test_pop3(email, password, config[service]['pop3'], verbose)

    result = {
        "email": email,
        "password": password,
        "imap": imap_result,
        "smtp": smtp_result,
        "pop3": pop3_result
    }
    result_color = colored("Email: ", "yellow") + colored(email, "yellow") + \
                   colored(" | Password: ", "blue") + (colored(password, "green") if imap_result or smtp_result or pop3_result else colored(password, "red")) + \
                   colored(" | IMAP: ", "blue") + (colored("True", "green") if imap_result else colored("False", "red")) + \
                   colored(" | SMTP: ", "blue") + (colored("True", "green") if smtp_result else colored("False", "red")) + \
                   colored(" | POP3: ", "blue") + (colored("True", "green") if pop3_result else colored("False", "red"))
    print(result_color)
    return result

# Function to test credentials against all services using multithreading
def test_credentials(usernames, passwords, config, verbose, max_threads):
    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        for password in passwords:
            for username in usernames:
                email_addresses = construct_email_addresses(username, config)
                for email in email_addresses:
                    if verbose: print(f"[V] Submitting task for {email}")
                    futures.append(executor.submit(test_single_credential, email, password, config, verbose))
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                if verbose:
                    print(colored(f"[-] Error testing credential - {e}", "red"))
    return results

# Helper function to get service from email
def get_service_from_email(email, config):
    domain = email.split('@')[1]
    for service, details in config.items():
        if any(domain == f"{service}.{tld}" for tld in details.get("TLDs", [])) or domain in details.get("SANs", []):
            return service
    return None

# Main function
def main():
    print(colored("""
      __  __       _ _    _____         _             
     |  \/  |     |_| |  |_   _|       | |            
     | \  / | __ _ _| |    | | ___  ___| |_ ___  _ __ 
     | |\/| |/ _` | | |    | |/ _ \/ __| __/ _ \| '__|
     | |  | | (_| | | |   _| |  __/\__ \ ||  __/  |   
     |_|  |_|\__,_|_|_|    |_|\___||___/\__\___/|_|   
    """, "cyan"))

    parser = argparse.ArgumentParser(description="Test email services for IMAP, SMTP, and POP3 login. If you input an email address, only that service will be tested. If you omit the service, all services from the JSON config file will be tested. Lists can be mixed, username and email.")
    parser.add_argument('-u', '--username', required=True, help="Username or file containing usernames (newline separated).")
    parser.add_argument('-p', '--password', required=True, help="Password or file containing passwords (newline separated).")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output.")
    parser.add_argument('-t', '--threads', type=int, default=1, help="Number of threads to use for testing.")
    
    args = parser.parse_args()
    global verbose
    verbose = args.verbose
    
    config = load_config()
    
    usernames = load_inputs(args.username)
    passwords = load_inputs(args.password)
    
    results = test_credentials(usernames, passwords, config, verbose, args.threads)
    
    if verbose:
        print("Results:")
        for result in results:
            print(result)

if __name__ == '__main__':
    main()
