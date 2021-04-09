import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import re
import hashlib

def send_emails(df, mailparams, org):
    """
    Sends e-mails to individuals with an e-mail address

    :param df: (pd.DataFrame) individual data
    :param mailparams: (dict) e-mail sender characteristics
    :param org: (dict) organization characteristics
    :return: (pd.DataFrame) individual data with column "envoi"
    """
    with open('../input/email.txt', 'rt') as file:
        raw_msg = file.read()

    def valid_email(s):
        if type(s)==str:
            return(bool(re.search('.*@.*\..*', s)))
        else:
            return(False)

    # Only keep rows for which a valid email address is provided
    df = df[df.email.apply(valid_email)]
    df.reset_index(drop=True, inplace=True)

    # Only keep rows for which an e-mail has not yet been sent (if it failed previously)
    open('../output/log_sent.txt', 'a').close()
    with open('../output/log_sent.txt', 'rt') as file:
        sent_files = [z.strip() for z in file.readlines()]
    df = df.loc[df.path.isin(sent_files)==False]

    with smtplib.SMTP(mailparams['smtp_server'], int(mailparams['smtp_port'])) as server:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(mailparams['email'], mailparams['password'])

        for i in range(df.shape[0]):
            # Generate the message
            ind = df.loc[i].to_dict()
            msg = raw_msg.format(nom=ind['nom'], prenom=ind['prenom'], montant=ind['montant'], date=ind['date'].strftime('%d/%m/%Y'))
            body = MIMEText(msg, 'plain')
            message = MIMEMultipart('mixed')
            message['From'] = '{orgname} <{sender}>'.format(orgname=org['nom'], sender=mailparams['email'])
            message['To'] = df.email[i]
            message['Subject'] = 'Votre reçu fiscal'
            message.attach(body)
            # Attach PDF and send
            with open(ind['path'], 'rb') as attachment:
                p = MIMEApplication(attachment.read(),_subtype='pdf')
                p.add_header('Content-Disposition', 'attachment; filename= %s' % mailparams['pdfname'])
                message.attach(p)
                msg_full = message.as_string()
                server.sendmail(mailparams['email'], message['To'], msg_full)
            # Append to log file
            with open('../output/log_sent.txt', 'a') as file:
                file.write(ind['path'])
                print('Sent to {recipient}'.format(recipient=message['To']))
        server.quit()
    return()
