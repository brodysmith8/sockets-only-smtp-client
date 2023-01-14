# To run, first ensure "credentials.txt" is present in the project folder.
# Next, open a terminal, navigate to project folder in the terminal, type "python3
# client.py" and run.

import socket
import ssl
import base64

msg = "\r\nI love computer networks!\r\n"
endmsg = "\r\n.\r\n"

# Choose a mail server (e.g. Google mail server) and call it mailserver
# Fill in start
hostname = "mail.gmx.com"

# me: technically the SMTP port for GMX is port 587, but SMTP-over-SSL is port 465. Port 25 (default SMTP port)
# is blocked by my ISP
port = 465
mailserver = (hostname, port)

# Fill in end


# Create socket called clientSocket and establish a TCP connection with mailserver
# Fill in start

# me: the "context" of an SSL session manages settings and certificates. create_default_context() uses TLSv1.3
# by default, and does most of the heavy SSL lifting for us
context = ssl.create_default_context()

# me: here, we create a socket and establish a connection to mailserver.
clientSocket = socket.create_connection(mailserver)

# me: then, we wrap the socket with SSL. We use the context object earlier to provide the SSL session with the
# requisite settings/certificates.
secureClientSocket = context.wrap_socket(clientSocket, server_hostname=hostname)

# Fill in end

# me: read the socket's buffer for the return to see if the server successfully connects and is ready to begin
recv = secureClientSocket.recv(1024).decode()
print(f"s: {recv}")

if recv[:3] != '220':
    print('220 reply not received from server.')


# Send HELO command and print server response.
# Fill in start

# me: using EHLO instead of HELO because EHLO shows the supported ESMTP (SMTP service extensions) options --
# useful for finding out how to authenticate
ehloCommand = 'EHLO mail.gmx.com\r\n'

# me: need to convert the string object to bytes to pass it to the socket's buffer
secureClientSocket.send(ehloCommand.encode())
recv1 = secureClientSocket.recv(1024).decode()
print(f"s: {recv1}")

# me: we expect a 250 OK message back to indicate the server received and is going to respond to our EHLO command
if recv1[:3] != '250':
    print('250 reply not received from server.')


''' me: EHLO response is this:
250-gmx.net Hello mail.gmx.com [request source ip]
250-8BITMIME
250-AUTH LOGIN PLAIN
250 SIZE 69920427

For AUTH PLAIN, we would need to supply it with a base64 encoded message that follows this format:
                base64(username+"\0"+password) (reference: https://stackoverflow.com/a/33398217)
For AUTH LOGIN, we need to supply server two messages. First is the username (username@mail.com), then after a 334
                response, we supply it with the password. Both username and password must be passed as base64-encoded
                messages, which we encode with the base64.b64encode() function. We are going to use AUTH LOGIN here.

Please note that the username and password are read from an external text file called "credentials.txt". This must be
in the same directory as the .py file, and the CLI command to execute this python file must be:
"python3 client.py".

I.e., running this file from VSCode run button will probably not work unless the calling terminal is cd'd into the
project directory.
'''

# me: Send AUTH LOGIN command and print server response.
authLoginCommand = "AUTH LOGIN\r\n"
print(f'c: {authLoginCommand.strip()}')
secureClientSocket.send(authLoginCommand.encode())
recv2 = secureClientSocket.recv(1024).decode()

# me: we expect a server response of code 334 "server challenge" (i.e., server needs more info for
# authentication) here, and it will be followed by a base64 encoded string that should say "Username:" when
# decoded from b64
if recv2[:3] != '334':
    print('334 reply not received from server.')
else:
    print("s: 334-\"" + (base64.b64decode(recv2[3:])).decode() + "\"")


# me: Get credentials
with open("./credentials.txt", 'r') as f:
    lines = f.readlines()


# me: strip the newline at the end of the string
username = lines[0].strip()

# me: Send username in base64
usernameEncoded = username.encode()
print('c: [base64-encoded username]')
secureClientSocket.send(base64.b64encode(usernameEncoded) + b'\r\n')
recv3 = secureClientSocket.recv(1024).decode()

if recv3[:3] != '334':
    print('334 reply not received from server.')
else:
    print("s: 334-\"" + (base64.b64decode(recv3[3:])).decode() + "\"")

# me: Send password in base64
# me: we expect a 235 response saying "authentication succeeded" here
password = lines[1].strip()
passwordEncoded = password.encode()
print('c: [base64-encoded password]')
secureClientSocket.send(base64.b64encode(passwordEncoded) + b'\r\n')
recv4 = secureClientSocket.recv(1024).decode()

if recv4[:3] != '235':
    print('235 reply not received from server.')
else:
    print(f"s: {recv4}")
# Fill in end

# Send MAIL FROM command and print server response.
# Fill in start
mailFromCommand = f'MAIL FROM:<{username}>\r\n'
print(f'c: {mailFromCommand.strip()}')
secureClientSocket.send(mailFromCommand.encode())
recv5 = secureClientSocket.recv(1024).decode()

if recv5[:3] != '250':
    print('250 reply not received from server.')
else:
    print(f"s: {recv5}")

# Fill in end

# Send RCPT TO command and print server response.

# Fill in start
recipient = "username@domain.com"
rcptToCommand = f'RCPT TO:<{recipient}>\r\n'
print(f'c: {rcptToCommand.strip()}')
secureClientSocket.send(rcptToCommand.encode())
recv6 = secureClientSocket.recv(1024).decode()

if recv6[:3] != '250':
    print('250 reply not received from server.')
else:
    print(f"s: {recv6}")

# Fill in end

# Send DATA command and print server response.

# Fill in start
dataCommand = 'DATA\r\n'
print(f'c: {dataCommand.strip()}')
secureClientSocket.send(dataCommand.encode())
recv7 = secureClientSocket.recv(1024).decode()

if recv7[:3] != '354':
    print('354 reply not received from server.')
else:
    print(f"s: {recv7}")

# Fill in end

# Send message data.
# Fill in start
subject = "This is from an SMTP client using only sockets"
print('c: [send message data]')
secureClientSocket.send(msg.encode())
# Fill in end

# Message ends with a single period.

# Fill in start
secureClientSocket.send(endmsg.encode())
recv8 = secureClientSocket.recv(1024).decode()
if recv8[:3] != "250":
    print("250 reply not received from server")
    print(recv8)
else:
    print(f"s: {recv8}")
# Fill in end

# Send QUIT command and get server response.
# Fill in start
quitCommand = "QUIT"
secureClientSocket.send(quitCommand.encode())
recv9 = secureClientSocket.recv(1024).decode()
if recv9[:3] != "221":
    print("221 reply not received from server.")
else:
    print(f"s: {recv9}")
    print("Server closed.")
# Fill in end
