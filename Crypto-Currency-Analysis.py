import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
from bs4 import BeautifulSoup
import streamlit as st 
# from PIL import Image
import requests
import json
import time
import locale
plt.style.use('fivethirtyeight')
st.set_page_config(layout="wide")
# image = Image.open('logo.jpg')
# st.image(image, width= 500)

st.title('Crypto-Currency Price Analysis')

st.markdown(
        """
<style>
    .reportview-container .main .block-container{
        padding-top: 1.6rem;
        padding-left: 1rem;
        zoom:90%
    }

</style>
""",
        unsafe_allow_html=True,
    )

# About
expand_bar = st.beta_expander("About")
expand_bar.markdown("""
* ** Libraries used: streamlit, pandas, matplotlib, BeautifulSoup, Image, requests, json **
* ** Data Source : https://coinmarketcap.com/**
""")
# Page Layout

column1 = st.sidebar
column2, column3 = st.beta_columns((2,1))          # Page Content: column2 is 2 times column1 
# column1.header('Sidebar')
select_currency_price_unit = column1.selectbox('Selected Price Unit',('INR', 'USD'))

def currency_price_unit():
    url = "https://currency-converter5.p.rapidapi.com/currency/convert"
    querystring = {"format":"json","from":"USD","to":"INR","amount":"1"}
    headers = {
    'x-rapidapi-key': "YOUR API-KEY",
    'x-rapidapi-host': "currency-converter5.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    rate = float(response.json()['rates']['INR']['rate'])
    return rate

#Web Scrap Data
@st.cache             # Cache the data, so that for the subsequent request, it will not scrap the data again 
def load_data():
    page = requests.get('https://coinmarketcap.com/')
    soup = BeautifulSoup(page.content, 'html.parser')
    data = soup.find('script', id="__NEXT_DATA__", type="application/json")
    coins_data = json.loads(data.contents[0])
    listings = coins_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    coin_name = []
    coin_symbol = []
    coin_price = []
    coin_volume = []
    coin_percent_change_1h = []
    coin_percent_change_24h = []
    coin_percent_change_7d = []
    coin_market_cap = []

    for i in listings:
        coin_name.append(i['name'])
        coin_symbol.append(i['symbol'])
        coin_price.append(i['quote']['USD']['price'])
        coin_volume.append(i['quote']['USD']['volume24h'])
        coin_percent_change_1h.append(i['quote']['USD']['percentChange1h'])
        coin_percent_change_24h.append(i['quote']['USD']['percentChange24h'])
        coin_percent_change_7d.append(i['quote']['USD']['percentChange7d'])
        coin_market_cap.append(i['quote']['USD']['marketCap'])

    if select_currency_price_unit == 'USD':
        locale.setlocale(locale.LC_NUMERIC, 'en_US')
        df = pd.DataFrame(columns = ['Coin_Name', 'Symbol', 'Price(in USD)', 'Volume_24h', 'Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d', 'Market_Cap(in USD)'])    
        df.Coin_Name = coin_name
        df.Symbol = coin_symbol


        df['Price(in USD)'] = coin_price
        df['Price(in USD)'] =  df['Price(in USD)'].apply(lambda x : locale.format_string("%.2f", x , grouping=True))
        df['Volume_24h'] = coin_volume
        df.Percent_change_1h = coin_percent_change_1h
        df.Percent_change_24h = coin_percent_change_24h
        df.Percent_change_7d = coin_percent_change_7d
        df['Market_Cap(in USD)'] = coin_market_cap
        return df

    else:
        locale.setlocale(locale.LC_NUMERIC, 'hi_IN')
        rate = currency_price_unit()
        df = pd.DataFrame(columns = ['Coin_Name', 'Symbol', 'Price(in INR)', 'Volume_24h', 'Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d', 'Market_Cap(in INR)'])
        df.Coin_Name = coin_name
        df.Symbol = coin_symbol
        df['Price(in INR)'] = np.array(coin_price) * rate
        df['Price(in INR)'] = df['Price(in INR)'].apply(lambda x : locale.format_string("%.2f", x , grouping=True))
        df['Volume_24h'] = coin_volume
        df.Percent_change_1h = coin_percent_change_1h
        df.Percent_change_24h = coin_percent_change_24h
        df.Percent_change_7d = coin_percent_change_7d

        df['Market_Cap(in INR)'] = np.array(coin_market_cap) * rate
        return df


data = load_data()


# Display Top 10 by Default
default_top_10 = data.Coin_Name[0:7]
selected_coins = default_top_10 
# data_of_selected_coins = data[data.Coin_Name.isin(selected_coins)].loc[0:, ['Coin_Name', 'Symbol', 'Price(in USD)', 'Volume_24h','Percent_change_1h']]
data_of_selected_coins = data[data.Coin_Name.isin(selected_coins)].iloc[0:, 0:5]

#  Slider
num_coin = column1.slider('Display Top 100 Coins', 1, 100, data_of_selected_coins.shape[0])
# column2.write('Debugging -- ' + str(num_coin))
selected_coins = data.Coin_Name[:num_coin]
# column2.write('Debugging -- ' + str(selected_coins))

#  Multi-Select
select_coins = sorted(data.Coin_Name)
selected_coins = column1.multiselect('Selected Crypto-Currency', select_coins, selected_coins)
data_of_selected_coins = data[data.Coin_Name.isin(selected_coins)].iloc[0:, 0:5]

if len(data_of_selected_coins) > 0:
    suffix  = 'Currencies' if len(data_of_selected_coins) > 1 else 'Currency'
    column2.subheader(f'Price-Volume Actions of Selected {suffix}')
    column2.table(data_of_selected_coins.set_index("Symbol"))

else:
    column2.info("Select a Currency to know it's Current Price, Price Change and Volumes Traded")

# column2.write('Data Dimension: ' + str(data_of_selected_coins.shape[0]) + ' Rows and ' + str(data_of_selected_coins.shape[1]) + ' Columns')

percent_change_timeframe = column1.selectbox('Select Time frame', ['1h', '24h', '7d'])
percent_change_dictionary = {'1h': 'Percent_change_1h', '24h': 'Percent_change_24h', '7d':'Percent_change_7d'}
selected_percent_timeframe = percent_change_dictionary[percent_change_timeframe]

column2.subheader('% Price Change of Currencies within Specific Time frame (High to Low)')
data_change = data.loc[0:, ['Symbol','Coin_Name','Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d']]
data_change.set_index('Symbol', inplace=True)
# column2.dataframe(data_change)      



def plot(data_change=None):

    column3.subheader('Bar Plot of % Price Change')
    data_change['Positive_Percent_change_1h'] = data_change.Percent_change_1h > 0
    data_change['Positive_Percent_change_24h'] = data_change.Percent_change_24h > 0
    data_change['Positive_Percent_change_7d'] = data_change.Percent_change_7d > 0

    if selected_percent_timeframe == 'Percent_change_1h':
        
        column2.table(data_change.sort_values(by=['Percent_change_1h'], ascending = False)[['Coin_Name','Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d']])
        
        column3.write('* 1-hour Change')
        plt.figure(figsize=(5, 26))
        plt.subplots_adjust(top=2.85, bottom = 0)

        data_change = data_change.sort_values(by=['Percent_change_1h'])
        data_change['Percent_change_1h'].plot(kind='barh', color=data_change.Positive_Percent_change_1h.map({True:'g', False:'r'}))
        column3.pyplot(plt)


    if selected_percent_timeframe == 'Percent_change_24h':
        column2.table(data_change.sort_values(by=['Percent_change_24h'], ascending = False)[['Coin_Name','Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d']])
        
        column3.write('* 24-hours Change')
        plt.figure(figsize=(5,26))
        plt.subplots_adjust(top=2.85, bottom = 0)

        data_change = data_change.sort_values(by=['Percent_change_24h'])
        data_change['Percent_change_24h'].plot(kind='barh', color=data_change.Positive_Percent_change_24h.map({True:'g', False:'r'}))
        column3.pyplot(plt)

        

    if selected_percent_timeframe == 'Percent_change_7d':
        column2.table(data_change.sort_values(by=['Percent_change_7d'], ascending = False)[['Coin_Name','Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d']])
        
        column3.write('* 7-Days Change')
        plt.figure(figsize=(5,26))
        plt.subplots_adjust(top=2.85, bottom = 0)

        data_change = data_change.sort_values(by=['Percent_change_7d'])
        data_change['Percent_change_7d'].plot(kind='barh', color=data_change.Positive_Percent_change_7d.map({True:'g', False:'r'}))
        column3.pyplot(plt)


plot(data_change)
