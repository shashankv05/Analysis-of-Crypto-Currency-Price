import pandas as pd 
import matplotlib.pyplot as plt 
from bs4 import BeautifulSoup
import streamlit as st 
from PIL import Image
import requests
import json
import time

st.set_page_config(layout="wide")
image = Image.open('logo.jpg')
st.image(image, width= 500, align='center')

st.title('Crypto-Currency Price Analysis')
st.markdown("""
We are going to analyse the Price change of Top 100 Crypto-Currencies over a period of time
""")

# About
expand_bar = st.beta_expander("About")
expand_bar.markdown("""
* ** Python Libraries : streamlit, pandas, matplotlib, BeautifulSoup, Image, requests, json **
* ** Data Source : https://coinmarketcap.com/**
""")
# Page Layout
column1 = st.sidebar
column2, column3 = st.beta_columns((2,1))          # Page Content: column2 is 2 times column1 

column1.header('Selection Sidebar')
# currency_price_unit = column1.selectbox('',('USD', 'BTC', 'ETH'))

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
        coin_volume.append(i['quote']['USD']['volume_24h'])
        coin_percent_change_1h.append(i['quote']['USD']['percent_change_1h'])
        coin_percent_change_24h.append(i['quote']['USD']['percent_change_24h'])
        coin_percent_change_7d.append(i['quote']['USD']['percent_change_7d'])
        coin_market_cap.append(i['quote']['USD']['market_cap'])
    
    df = pd.DataFrame(columns = ['Coin_Name', 'Symbol', 'Price(in USD)', 'Volume_24h(in USD)', 'Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d', 'Market_Cap(in USD)'])    

    df.Coin_Name = coin_name
    df.Symbol = coin_symbol
    df['Price(in USD)'] = coin_price
    df['Volume_24h(in USD)'] = coin_volume
    df.Percent_change_1h = coin_percent_change_1h
    df.Percent_change_24h = coin_percent_change_24h
    df.Percent_change_7d = coin_percent_change_7d
    df['Market_Cap(in USD)'] = coin_market_cap
    return df

data = load_data()

# Sidebar

# Display Top 10 by Default
default_top_10 = data.Coin_Name[0:10]
selected_coins = default_top_10 
data_of_selected_coins = data[data.Coin_Name.isin(selected_coins)].loc[0:, ['Coin_Name', 'Symbol', 'Price(in USD)', 'Volume_24h(in USD)','Market_Cap(in USD)']]
num_coin = column1.slider('Display Top 100 Coins', 0, 100, data_of_selected_coins.shape[0])
# column2.write('Debugging -- ' + str(num_coin))

selected_coins = data.Coin_Name[:num_coin]
# column2.write('Debugging -- ' + str(selected_coins))

select_coins = sorted(data.Coin_Name)
selected_coins = column1.multiselect('Select Crypto-Currency', select_coins, selected_coins)
data_of_selected_coins = data[data.Coin_Name.isin(selected_coins)].loc[0:, ['Coin_Name', 'Symbol', 'Price(in USD)', 'Volume_24h(in USD)','Market_Cap(in USD)']]


percent_change_timeframe = column1.selectbox('Select time frame', ['1h', '24h', '7d'])
percent_change_dictionary = {'1h': 'Percent_change_1h', '24h': 'Percent_change_24h', '7d':'Percent_change_7d'}
selected_percent_timeframe = percent_change_dictionary[percent_change_timeframe]


column2.subheader('Details of Selected Crypto-Currency')
# column2.write('Data Dimension: ' + str(data_of_selected_coins.shape[0]) + ' Rows and ' + str(data_of_selected_coins.shape[1]) + ' Columns')
column2.dataframe(data_of_selected_coins)

column2.subheader('% Price Change')
data_change = data.loc[0:, ['Symbol','Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d']]
data_change.set_index('Symbol', inplace=True)
# column2.dataframe(data_change)      


column3.subheader('Bar Plot of % Price Change')
data_change['Positive_Percent_change_1h'] = data_change.Percent_change_1h > 0
data_change['Positive_Percent_change_24h'] = data_change.Percent_change_24h > 0
data_change['Positive_Percent_change_7d'] = data_change.Percent_change_7d > 0

def plot():
    global data_change

    if selected_percent_timeframe == 'Percent_change_1h':
        data_change = data_change.sort_values(by=['Percent_change_1h'])
        column3.write('* 1-hour Change')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top=1, bottom = 0)
        data_change['Percent_change_1h'].plot(kind='barh', color=data_change.Positive_Percent_change_1h.map({True:'g', False:'r'}))
        column3.pyplot(plt)
        column2.dataframe(data_change.sort_values(by=['Percent_change_1h'], ascending = False)[['Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d']])

    if selected_percent_timeframe == 'Percent_change_24h':
        data_change = data_change.sort_values(by=['Percent_change_24h'])
        column3.write('* 24-hours Change')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top=1, bottom = 0)
        data_change['Percent_change_24h'].plot(kind='barh', color=data_change.Positive_Percent_change_24h.map({True:'g', False:'r'}))
        column3.pyplot(plt)
        column2.dataframe(data_change.sort_values(by=['Percent_change_24h'], ascending = False)[['Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d']])

    if selected_percent_timeframe == 'Percent_change_7d':
        data_change = data_change.sort_values(by=['Percent_change_7d'])
        column3.write('* 7-Days Change')
        plt.figure(figsize=(5,25))
        plt.subplots_adjust(top=1, bottom = 0)
        data_change['Percent_change_7d'].plot(kind='barh', color=data_change.Positive_Percent_change_7d.map({True:'g', False:'r'}))
        column3.pyplot(plt)
        column2.dataframe(data_change.sort_values(by=['Percent_change_7d'], ascending = False)[['Percent_change_1h', 'Percent_change_24h', 'Percent_change_7d']])
plot()