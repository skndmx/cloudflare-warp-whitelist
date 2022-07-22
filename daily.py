from datetime import datetime
import pandas as pd
import numpy as np
import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(df,account):
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M")                  #date-time format 2022-07-07-16-30_
    subject = "[Daily Monitor]Cloudflare WARP whitelist for customer: "+account
    msg = MIMEMultipart()
    msg['From'] = config.mailFromAdress
    msg['To'] = ", ".join(config.mailToAdress)
    msg['Subject'] = subject
    
    html = """\
    <html>
      <head></head>
      <body>
        <p>Cloudflare WARP whitelist as of {1}</p>
        <p></p> 
        {0}
      </body>
    </html>
    """.format(df.to_html(), dt_string)

    part1 = MIMEText(html, 'html')
    msg.attach(part1)    
    message = msg.as_string()
    
    try:
        server = smtplib.SMTP(config.mailServer)
        server.starttls()
        server.login(config.mailFromAdress, config.mailFromPassword)

        server.sendmail(config.mailFromAdress, config.mailToAdress, message)
        server.quit()
        print("SUCCESS - Email sent")

    except Exception as e:
        print("FAILURE - Email not sent")
        print(e)

def main():
    account = "9d70d5364203a143af39dd8169ef8df7"   
    if os.path.isfile("{}.csv".format(account[-6:])):           #if file exists 
        df = pd.read_csv("{}.csv".format(account[-6:]), encoding='utf_8_sig', index_col=[0])   #read existing csv
        df = df.replace(np.nan, '', regex=True)               #replace nan with ""
        send_email(df,account)
    else:
        print("File doesn't exist")

if __name__ == "__main__":
    main()