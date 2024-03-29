import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
  
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; \
    Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/113.0.0.0 Safari/537.36'}

stocks = ["FUTU", "JFU", "OPRT", "XP", "BILL", "OCFT", "HUIZ", "LPRO",
          "LMND", "NCNO", "BEKE", "LU", "UPST", "OPEN", "VII", "AFRM", 
          "HIPO", "PSFE", "ALKT", "FLYW", "PAY", "SOFI", "DLO","MQ", 
          "KPLT", "PAYO", "BLND", "OPFI", "RSKD", "HOOD", "DOMA", "TOST",
          "RELY", "ML", "NVEI", "AVDX", "ENFN", "NRDS", "EXFY", "FINW", 
          "NU","VCXA", "HKD", "JNVR", "SEZL", "KSPI", "QQEW", "RSP", "EDOW"]

urls = []
for s in stocks:
    url = f"http://finviz.com/quote.ashx?t={s}"
    urls.append(url)
    
url = "http://finviz.com/quote.ashx?t=FUTU"
response = requests.get(url,headers=headers)
html_content = response.content
soup = BeautifulSoup(html_content, "html.parser")

all=[]

def find_exact_price(element):
    return element.name == 'td' and element.text.strip() == "Price"

for i, url in enumerate(urls):
    page = requests.get(url,headers=headers)
    try:
        soup = BeautifulSoup(page.text, 
                             'html.parser')
        company = stocks[i]
        price_td = soup.find('td', string=re.compile('Prev Close'))
        price = price_td.find_next_sibling('td').text
        if price != '-':
            price = float(price)
        else:
            price = None
        ptos_td = soup.find('td', string=re.compile('P/S'))
        ptos = ptos_td.find_next_sibling('td').text
        if ptos != '-':
            ptos = float(ptos)
        else:
            ptos = None
        ptoe_td = soup.find('td', string=re.compile('P/E'))
        ptoe = ptoe_td.find_next_sibling('td').text
        if ptoe != '-':
            ptoe = float(ptoe)
        else:
            ptoe = None
        market_cap_td = soup.find('td', string=re.compile('Market Cap'))
        marketcap_temp = market_cap_td.find_next_sibling('td').text
        marketcap = re.findall('(\d+\.\d+)(?=B)|(\d+\.\d+)(?=M)', marketcap_temp)
        if marketcap:
            marketcap = marketcap[0][0] if marketcap[0][0] else marketcap[0][1]
            marketcap = float(marketcap)
        else:
            marketcap = None
        price2_td = soup.find(find_exact_price)
        price2 = price2_td.find_next_sibling('td').text
        if price2 != '-':
            price2 = float(price2)
        else:
            price2 = None
        x=[company,price,ptos,ptoe,marketcap,price2]
        all.append(x)
          
    except AttributeError:
      print("Change the Element id for:", stocks[i])
    
column_names = ["Company", "Price (Prev Close)", "P/S", "P/E", "Market Cap", "Price (today)"]
df = pd.DataFrame(columns=column_names)
for i in all:
    index = 0
    df.loc[index] = i
    df.index = df.index + 1
df = df.reset_index(drop=True)

try:
    # Attempt to save in the specified directory
    today = datetime.today().strftime('%m_%d_%Y')
    hour = datetime.today().hour
    time_suffix = "_am" if hour < 12 else "_pm"
    filename = f'stocks_{today}{time_suffix}.xlsx'
    path = 'metrics/'
    #path = '/home/runner/work/Scrap_IPO_FinTechs/metrics/'
    df.to_excel(f'{path}{filename}')
except Exception as e:
    print(f"An error occurred while saving in the specified directory: {str(e)}")
    
    # If saving in the specified directory fails, save in the working directory
    try:
        filename = f'stocks_{today}{time_suffix}.xlsx'
        df.to_excel(filename)
        print(f"Saved in the working directory as {filename}")
    except Exception as e:
        print(f"An error occurred while saving in the working directory: {str(e)}")

