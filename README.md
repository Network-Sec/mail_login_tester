# Email Login Tester
Pentesting Script, automating login tests. Multithreaded and preconfigured for top mail services, like gmail, hotmail, yahoo... trying IMAP, SMTP and POP3 login.

```bash
$ mail_login_tester.py -u /tmp/email -p /tmp/pwd

      __  __       _ _    _____         _                                                                                                                    
     |  \/  |     |_| |  |_   _|       | |                                                                                                                   
     | \  / | __ _ _| |    | | ___  ___| |_ ___  _ __                                                                                                        
     | |\/| |/ _` | | |    | |/ _ \/ __| __/ _ \| '__|                                                                                                       
     | |  | | (_| | | |    | |  __/\__ \ ||  __/  |                                                                                                          
     |_|  |_|\__,_|_|_|    |_|\___||___/\__\___/|_|                                                                                                          
                                                                                                                                                             
Email: test1@hotmail.com | Password: 1234567890 | IMAP: False | SMTP: False | POP3: False
Email: test123@gmail.com | Password: password12 | IMAP: False | SMTP: False | POP3: False
```

You can provide either single items or files with line separated items for both `Email` and `Password`. You can **mix** lists of full email addresses with usernames (without @gmail.com). If you provide usernames instead of email addresses, the script will try to use all configured mail services automatically. 

```bash
mail_login_tester.py -h

      __  __       _ _    _____         _                                                                                                                    
     |  \/  |     |_| |  |_   _|       | |                                                                                                                   
     | \  / | __ _ _| |    | | ___  ___| |_ ___  _ __                                                                                                        
     | |\/| |/ _` | | |    | |/ _ \/ __| __/ _ \| '__|                                                                                                       
     | |  | | (_| | | |   _| |  __/\__ \ ||  __/  |                                                                                                          
     |_|  |_|\__,_|_|_|    |_|\___||___/\__\___/|_|                                                                                                          
                                                                                                                                                             
usage: mail_login_tester.py [-h] -u USERNAME -p PASSWORD [-v] [-t THREADS]

Test email services for IMAP, SMTP, and POP3 login. If you input an email address, only that service will be tested. If you omit the service, all services
from the JSON config file will be tested. Lists can be mixed, username and email.

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username or file containing usernames (newline separated).
  -p PASSWORD, --password PASSWORD
                        Password or file containing passwords (newline separated).
  -v, --verbose         Enable verbose output.
  -t THREADS, --threads THREADS
                        Number of threads to use for testing
```

## Example Username list
```
test123@gmail.com               <====== Script will use ONLY this exact address for this item
test234                         <====== Script will generate all possible addresses for this item - use with extreme care!
test456
test123@hotmail.com
```
