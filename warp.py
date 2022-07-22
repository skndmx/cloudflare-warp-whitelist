#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import pandas as pd
from ipdata import ipdata
from pprint import pprint
import numpy as np
import config
import tokens
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_email(df,account):
    body = "Hi fellows, this Email is sent from my Python Script"
    subject = "Cloudflare WARP whitelist for customer: "+account

    msg = MIMEMultipart()
    msg['From'] = config.mailFromAdress
    msg['To'] = ", ".join(config.mailToAdress)
    msg['Subject'] = subject

    html = """\
    <html>
      <head></head>
      <body>
        <p>Cloudflare WARP whitelist updated</p>
        <p></p>
        {0}
      </body>
    </html>
    """.format(df.to_html())

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

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    except TypeError as e:
        return False
    return True

def add_whois(df):
    whois = []              #empty list for a new column
    for i,j in df.iterrows():
        if pd.isnull(df.at[i,'address']):             #if address is NaN
            whois.append(" ")                           
        else:
            ip = ipdata.IPData(tokens.ipdata_token)      #ipdata API token
            removesubnet = df.at[i,'address'].split("/",1)[0]                       #remove /24 subnet mask from address
            response = ip.lookup(removesubnet)
            #pprint(response['asn']['name'])
            whois.append(response['asn']['name'])
    df['whois'] = whois                 #add a column named whois to the dataframe
    df1 = df.replace(np.nan, '', regex=True)             #replace all NaN with ""
    return df1

def main():
    account = "9d70d5364203a143af39dd8169ef8df7"        
    api_url = "https://api.cloudflare.com/client/v4/accounts/9d70d5364203a143af39dd8169ef8df7/devices/policy/include"
    api_token = {"Authorization": tokens.cf_token}
    result=requests.get(api_url, headers=api_token).json()
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d-%H-%M")                  #date-time format 2022-07-07-16-30_
    print("Date and time ={}\n".format(dt_string))
    #print(result['result'])
    #with open('{}_{}.json'.format(dt_string,account[-6:]), 'w') as f:   #format json file as "date_account(last 6 char).json"
    #    json.dump(result, f)
    json_object = json.dumps(result['result'])
    #print(is_json(json_object))
    df = pd.DataFrame.from_dict(result['result'])               #pandas dataframe from dictionary
    #pd.set_option('display.max_rows', df.shape[0]+1)
    
    df = add_whois(df)

    print(df)
    if os.path.isfile("{}.csv".format(account[-6:])):           #if file exists 
        df2 = pd.read_csv("{}.csv".format(account[-6:]), encoding='utf_8_sig', index_col=[0])   #read existing csv
        df2 = df2.replace(np.nan, '', regex=True)               #replace nan with ""
        if df2.equals(df):
            print("Whitelist same as before")
        else: 
            print("Whitelist changed")
            df.to_csv("{}.csv".format(account[-6:]), encoding='utf_8_sig')
            send_email(df,account)
    else:
        df.to_csv("{}.csv".format(account[-6:]), encoding='utf_8_sig')
        send_email(df,account)
        print("Whitelist created")

    #df.to_csv("{}.csv".format(account[-6:]), encoding='utf_8_sig')

    #send_email(df,account)


if __name__ == "__main__":
    main()