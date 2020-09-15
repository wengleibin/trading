# Technical Indicator - MACD

# Import Libs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader as web
import os
from datetime import datetime, timedelta
from shutil import copyfile
import smtplib
from socket import gaierror
plt.style.use('fivethirtyeight')


# Define Path, Input and Output
InputPath = "J:/Projects/trading/"
InputFile = "Watchlist.csv"
OutputPath = "J:/Projects/trading/Strategies/MACD/Results/"

#Get Stocks from watchlist
get_stocks = pd.read_csv(InputPath + InputFile, encoding = "ISO-8859-1")

# Get Running Period
# Always get a period for an entire year
today = datetime.today()
begdate = today.replace(year = int(today.year) -1)

#period start
if int(begdate.month) < 10:
    if int(begdate.day) < 10:
        periodstart = str(begdate.year) + '-0' + str(begdate.month) + '-0' + str(begdate.day)
    else:
        periodstart = str(begdate.year) + '-0' + str(begdate.month) + '-' + str(begdate.day)
else:
    if int(begdate.day) < 10:
        periodstart = str(begdate.year) + '-' + str(begdate.month) + '-0' + str(begdate.day)
    else:
        periodstart = str(begdate.year) + '-' + str(begdate.month) + '-' + str(begdate.day)

# Period End
if int(today.month) < 10:
    if int(today.day) < 10:
        periodend = str(today.year) + '-0' + str(today.month) + '-0' + str(today.day)
    else:
        periodend = str(today.year) + '-0' + str(today.month) + '-' + str(today.day)
else:
    if int(today.day) < 10:
        periodend = str(today.year) + '-' + str(today.month) + '-0' + str(today.day)
    else:
        periodend = str(today.year) + '-' + str(today.month) + '-' + str(today.day)

# Create Daily Folder if not exist
if os.path.isdir(OutputPath + str(today.year)) == True:
    if os.path.isdir(OutputPath + str(today.year) + '/' + str(today.month)) == True:
        if os.path.isdir(OutputPath + str(today.year) + '/' + str(today.month) + '/' + periodend) == False:
            os.mkdir(OutputPath + str(today.year) + '/' + str(today.month) + '/' + periodend)
    else:
        os.mkdir(OutputPath + str(today.year) + '/' + str(today.month))
        os.mkdir(OutputPath + str(today.year) + '/' + str(today.month) + '/' + periodend)
else:
    os.mkdir(OutputPath + str(today.year))
    os.mkdir(OutputPath + str(today.year) + '/' + str(today.month))
    os.mkdir(OutputPath + str(today.year) + '/' + str(today.month) + '/' + periodend)
    
# Define Function to append Buy and Sell Price
def buy_sell(signal):
    buy = []
    sell = []
    flag = -1

    for i in range(0,len(signal)):
      if signal['MACD'][i] > signal['Signal Line'][i]:
        sell.append(np.nan)
        if flag != 1:
          buy.append(signal['Close'][i])
          flag = 1
        else:
          buy.append(np.nan)
      elif signal['MACD'][i] < signal['Signal Line'][i]:
        buy.append(np.nan)
        if flag != 0:
          sell.append(signal['Close'][i])
          flag = 0
        else:
          sell.append(np.nan)
      else:
        buy.append(np.nan)
        sell.append(np.nan)

    return(buy,sell)

to_print = ''
# MACD Indicator
for stock in get_stocks['Ticker']:
    # Get data from yahoo finance
    df = web.DataReader(stock, data_source='yahoo', start = periodstart, end = periodend)

    # Calculate for MACD and signal
    ShortEMA = df.Close.ewm(span=12,adjust = False).mean()
    LongEMA = df.Close.ewm(span = 26,adjust = False).mean()
    MACD = ShortEMA - LongEMA
    signal = MACD.ewm(span = 9,adjust = False).mean()

    #append columns for MACD and Signal
    df['MACD'] = MACD
    df['Signal Line'] = signal

    #Get Buy and sell signal price and append columns
    a = buy_sell(df)
    df['buy_signal_price'] = a[0]
    df['sell_signal_price'] = a[1]
    
    #print(np.isnan(df.iloc[-1]['buy_signal_price']))
    
    if np.isnan(df.iloc[-1]['buy_signal_price']) != True or  np.isnan(df.iloc[-1]['sell_signal_price'])!= True:
        #Get Figure
        plt.figure(figsize=(24,8))
        plt.scatter(df.index,df['buy_signal_price'],color ='green', label='buy', marker = '^',alpha = 1)
        plt.scatter(df.index,df['sell_signal_price'],color ='red', label='sell', marker = 'v',alpha = 1)
        plt.plot(df['Close'],label='Close Price',alpha = 0.35)
        plt.title('Close Price Buy & Sell Signals')
        #plt.xticks(rotation = 45)
        #plt.xlabel('Date')
        plt.ylabel('Close Price  USD (&)')
        plt.legend(loc = 'upper left')
        
        # Create Folder Based on Ticker
        if os.path.isdir(OutputPath + str(today.year) + '/' + str(today.month) + '/' + periodend + '/' + stock) == False:
            os.mkdir(OutputPath + str(today.year) + '/' + str(today.month) + '/' + periodend + '/' + stock)
        
        # Save figure to the folder
        plt.savefig(OutputPath + str(today.year) + '/' + str(today.month) + '/' + periodend + '/' + stock + '/' + stock +'.png')
        #print(df.iloc[-1]['buy_signal_price'])
        #print(df.iloc[-1]['sell_signal_price'])
        
        if np.isnan(df.iloc[-1]['buy_signal_price']) != True:
            to_print = to_print + stock + ' MACD indicator buy price ' + str(round(df.iloc[-1]['buy_signal_price'],2)) + '\n'
            #print(df.iloc[-1]['buy_signal_price'])
        else:
            to_print = to_print + stock + ' MACD indicator sell price ' + str(round(df.iloc[-1]['sell_signal_price'],2)) + '\n'
            #print(df.iloc[-1]['sell_signal_price'])


# now you can play with your code. Let’s define the SMTP server separately here:
port = 587 
smtp_server = "smtp-mail.outlook.com"
login = "wengleibin@hotmail.com" # paste your login generated by Mailtrap
password = "Onlybean1024@" # paste your password generated by Mailtrap

# specify the sender’s and receiver’s email addresses
sender = "wengleibin@hotmail.com"
receiver = "wengleibin@yahoo.com"


server = smtplib.SMTP(smtp_server, port)
server.connect(smtp_server, port)
server.ehlo()
server.starttls()
server.ehlo()
server.login(login, password)
subject = periodend + ' MACD Indicator'
message = 'Subject: {}\n\n{}'.format(subject, to_print)
server.sendmail(sender, receiver, message)
server.quit()
