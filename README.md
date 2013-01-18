This project is a simple web based chat client.

How it works:

udpchatserver.py must be running on the machine you want to connect to.
The udpchat.cgi and udpchat.html files must be hosted on a machine configured to host CGI scripts, etc.

Once done, you can navigate to the hosted udpchat.html page, and enter login details.  Currently the server
simply stores username/password pairs as a dictionary, no encryption.