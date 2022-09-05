import smtplib, ssl, config
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def send_email(subject, body, sender_email, receiver_email, password, sender_name=False, file=False):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_name if sender_name else sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))


    if file:
        # Open PDF file in binary mode
        with open(file, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        while file.find("/") != -1: # Removing directories
            file = file[file.find("/")+1:]
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)


    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


if __name__ == "__main__":
    subject = "An email with attachment from Python"
    body = "This is an email with attachment sent from Python"
    sender_email = config.sender
    receiver_email = config.receiver
    password = config.api_key
    sender_name = config.name
    file = "example.pdf" 
    
    send_email(subject, body, 
               sender_email, receiver_email, 
               password, sender_name, file)