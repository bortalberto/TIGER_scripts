import smtplib, ssl, sys
import base64

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()
def impacchetta_recievers(rcv_list):
    rcv_string=""
    for elem in rcv_list:
        rcv_string=rcv_string+elem+"; "
    return rcv_string
smtp_server = "smtp.office365.com"
port = 587  # For starttls
sender_email = "cgem_daq@outlook.com"
with open("conf"+sep+"read_me") as f: pss = f.readline()
password = (base64.b64decode(pss).decode("utf-8"))
receiver_email=[]
with open ("conf"+sep+"mailining_list") as f:
    for line in f.readlines():
        if line[0]!="#":
            receiver_email.append(line.strip())

message="""From: {}
To: {}
Subject:{}\n
{}
""".format(sender_email,impacchetta_recievers(receiver_email),sys.argv[1],sys.argv[2])

print (message)


context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    # server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    esito=server.sendmail(sender_email, to_addrs=receiver_email, msg=message)