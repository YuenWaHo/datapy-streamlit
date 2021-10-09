import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime

def main():
    pages = {
        "Home": page_home,
        "Settings": page_settings,
    }

    if "page" not in st.session_state:
        st.session_state.update({
            # Default page
            "page": "Home",

            # # Radio, selectbox and multiselect options
            # "options": ["Hello", "Everyone", "Happy", "Streamlit-ing"],

            # # Default widget values
            # "text": "",
            # "slider": 0,
            # "checkbox": False,
            # "radio": "Hello",
            # "selectbox": "Hello",
            # "multiselect": ["Hello", "Everyone"],
        })

    with st.sidebar:
        page = st.radio("Select your page", tuple(pages.keys()))

    pages[page]()


def page_home():
    st.markdown('''
    # Stock Price Volatility Backtesting
    We provide stock price historical volatility backtesting based on pass 20 years of data.
    For example, during the period 2021-09-05 to 2021-09-16, AAPL has increased by 3.26% for the pass 20 years.
    There is a high probability that during this specified period, the stock price of AAPL will increase by 3.26%.
    We backtested this strategy based on 60 months of testing samples, giving rise to a winning probability (Win Rate). 

    我們根據過去 20 年的數據提供股票價格歷史波動回測。
    例如，2021-09-05 至 2021-09-16 期間，過去 20 年 AAPL 增長了 3.26%。
    在此特定時期內，AAPL 的股價大概率會上漲 3.26%。
    我們根據 60 個月的測試樣本對該策略進行了回測，得出了獲勝概率(Win Rate)。

    - App built by [DataPy]
    - Historic stock price volatility analysis
    ''')
    st.write('---')

    user_list = {
        'hoyuenwaderek@gmail.com':'abcd1234',
        'urania@gmail.com':'Uran1234'
    }
    
    with st.form(key='my_form'):
        user_name = st.text_input("User email", 'xxx@gmail.com')
        user_pw = st.text_input("Password", 'ABCD1234')
        submit_button = st.form_submit_button(label='Submit')

        # strip any whitespace from the ends of the input
    user_name, user_pw = user_name.strip(), user_pw.strip()
    # check username and password entered are correct
    global user_status
    if user_name in user_list and user_pw == user_list[user_name]:
        st.write('logged in')
        user_status = True
    else:
        st.write('your username is not registered. Would you like to register')
        user_status = False

    

def page_settings():
    # Sidebar
    st.sidebar.subheader('Query parameters')
    start_date = st.sidebar.date_input("Start date", datetime.date(2015, 1, 1))
    end_date = st.sidebar.date_input("End date", datetime.date(2021, 9, 21))

    # Retrieving tickers data
    if user_status == True:
        ticker_list = pd.read_csv('prediction_list.txt')
    else:
        ticker_list = pd.read_csv('prediction_list_trial.txt')
    ticket_list = ticker_list.sort_values('Stock', ascending=True, axis=0, inplace=True)
    tickerSymbol = st.sidebar.selectbox('Stock Ticker Symbol', ticker_list['Stock']) # Select ticker symbol
    tickerData = yf.Ticker(tickerSymbol) # Get ticker data
    tickerDf = tickerData.history(period='1d', start=start_date, end=end_date) #get the historical prices for this ticker

    # Ticker information
    col1, col2 = st.columns(2)

    string_name = tickerData.info['longName']
    string_industry = 'Industry: ' + tickerData.info['industry']
    string_sector =   'Sector  :' + tickerData.info['sector']
    col1.header('**%s**' % string_name)
    col1.markdown(string_industry)
    col1.markdown(string_sector)

    string_logo = '<img src=%s>' % tickerData.info['logo_url']
    col2.markdown(string_logo, unsafe_allow_html=True)

    string_summary = tickerData.info['longBusinessSummary']
    st.info(string_summary)
    st.write('---')
    # Volatility Prediction
    st.header('**Volatility Backtest Result**')
    vol_backtest_df = pd.read_csv('backtest_summary.csv')
    if ((vol_backtest_df['stock'] == tickerSymbol)).any():
        month_vol_df_filtered = vol_backtest_df[vol_backtest_df['stock'] == tickerSymbol]
        st.write(month_vol_df_filtered[['Win_Rate', 'Min_vol', 'TR_rank', 'Vol_rank', 'Total_score' ,'EV']])
    else:
        st.write('Historic backtest not available.')

    # Ticker data
    st.header('**Ticker data**')
    st.write(tickerDf.tail(5))

    st.header('**Stock Price**')
    qf=cf.QuantFig(tickerDf,title='Stock Price Figure',legend='top',name='GS')
    fig = qf.iplot(asFigure=True)
    st.plotly_chart(fig)

    # Volatility Prediction
    st.header('**Volatility Prediction (Monthly)**')
    month_vol_df = pd.read_csv('Monthly_prediction.csv')
    if ((month_vol_df['Stock'] == tickerSymbol)).any():
        month_vol_df_filtered = month_vol_df[month_vol_df['Stock'] == tickerSymbol]
        st.write(month_vol_df_filtered[['vol_day_start', 'vol_day_end', 'pos_change', 'Type', 'MDD_perc']])
    else:
        st.write('Historic volatility not available.')

    # Volatility Prediction
    st.header('**Volatility Prediction (Quaterly)**')
    quaterly_vol_df = pd.read_csv('Quaterly_prediction.csv')

    if ((quaterly_vol_df['Stock'] == tickerSymbol)).any():
        month_vol_df_filtered = quaterly_vol_df[quaterly_vol_df['Stock'] == tickerSymbol]
        st.write(month_vol_df_filtered[['vol_day_start', 'vol_day_end', 'pos_change', 'Type', 'MDD_perc']])
    else:
        st.write('Historic volatility not available.')

if __name__ == "__main__":
    main()