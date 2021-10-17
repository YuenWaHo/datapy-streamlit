import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import cufflinks as cf
import datetime
import pyrebase
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import plotly.express as px
from yfinance import ticker

st.set_page_config(
    page_title="DataPy - Stock Volatility App",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

def main():
    pages = {
        "Home": page_home,
        "Login": page_login,
    }

    if "page" not in st.session_state:
        st.session_state.update({
            "page": "Home",
        })

    with st.sidebar:
        page = st.radio("Select your page", tuple(pages.keys()), key='page_select')

    pages[page]()

# Configuration Key
firebaseConfig = {
  'apiKey': "AIzaSyA12g3rx8S-KQbCJlMQPVuGqAMC7OVUxjY",
  'authDomain': "datapy-stockvol.firebaseapp.com",
  'projectId': "datapy-stockvol",
  'storageBucket': "datapy-stockvol.appspot.com",
  'messagingSenderId': "320588079812",
  'appId': "1:320588079812:web:5396b281363526590c1f91",
  'measurementId': "G-9R9V43VH75",
  'databaseURL':'https://datapy-stockvol-default-rtdb.asia-southeast1.firebasedatabase.app/'
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def set_align_for_column(table, col, align="center"):
    cells = [key for key in table._cells if key[1] == col]
    for cell in cells:
        table._cells[cell]._loc = align

def render_mpl_table(data, col_width=0.8, row_height=0.5, font_size=10,
                     header_color='#48754b', row_colors=['#f1f1f2', 'w'], edge_color='k', ##40466e
                     bbox=[0, 0, 1, 1], header_columns=0, **kwargs):
    size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
    fig, ax = plt.subplots(figsize=size)
    ax.axis('off')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, cellLoc='center',
                         colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    set_align_for_column(mpl_table, col=0, align="center")
    set_align_for_column(mpl_table, col=1, align="center")

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
            cell._loc = 'center'
        else:
            cell.set_facecolor(row_colors[k[0] % len(row_colors)])
    return fig

def gen_backtest_report(df, m_month, perc_str):
    display_final = df.copy()
    sort_df = display_final.loc[display_final.Type.str.endswith(m_month,na=False)]
    sort_df2 = sort_df[sort_df['test_percentage'] == perc_str][['test_year', 'Type', 'WL', 'test_yr_vol', 'target_range']]
    sort_df2['Type'] = sort_df2['Type'].str[:-3].str[3:]

    sort_df2['test_year'] = sort_df2['test_year'].astype(str)
    sort_df2['test_yr_vol']  = sort_df2['test_yr_vol'].round(2)
    sort_df2['target_range']  = sort_df2['target_range'].round(2)
    sort_df3 = sort_df2.pivot(index='test_year', columns = 'Type', values = 'WL')
    sort_df4 = sort_df2.pivot(index='test_year', columns = 'Type', values = 'test_yr_vol')
    sort_df5 = sort_df2.pivot(index='test_year', columns = 'Type', values = 'target_range')
    sort_df3['test_year'] = sort_df3.index
    sort_df4['test_year'] = sort_df4.index
    sort_df5['test_year'] = sort_df5.index

    sort_df3 = sort_df3[['test_year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]
    sort_df4 = sort_df4[['test_year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]
    sort_df5 = sort_df5[['test_year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]
    sort_df3.columns = ['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sort_df4.columns = ['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sort_df5.columns = ['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig1 = render_mpl_table(sort_df3, header_columns=0, col_width=1.0)
    fig2 = render_mpl_table(sort_df4, header_columns=0, col_width=1.0)
    fig3 = render_mpl_table(sort_df5, header_columns=0, col_width=1.0)
    return fig1, fig2, fig3

def page_home():
    st.header('Stock Price Volatility Backtesting')
    # Stock Price Volatility Backtesting
    st.write('''
    - App built by [DataPy](https://www.youtube.com/channel/UCI7auEnrAG2XAlGjdGN2Gsg)
    - Historic stock price volatility analysis
    
    If you are interested in using this stock volatility analysis in gaining consistent profit. 
    Please contact us for more details.''')
    
    st.write('[Telegram](https://t.me/) [WhatsApp](https://wa.me/) [Instagram](https://www.instagram.com)')

    st.write('---')
    col1, col2 = st.columns(2)

    col1.markdown(
    '''
    This platform provides stock historical volatility analysis. The calculation is within a specified 
    period (typically the next Monday trailing the end date of the option expiry date to the next option 
    expiry date) and calculate the minimum increase in stock price in the past 20 years. The target 
    ranges of positive increase include the 100% range (minimum positive increase in all 20 years) 
    and the 90% range (minimum positive increase in 18 years). This trading strategy captures the 
    minimum positive increase in stock prices over the past 20 years, and assumed that this minimum 
    range of increase will occur again during the same period this year. 

    This trading strategy require huge computational time for screening stock prices. 305 out of 
    S&P500 stock (With over 25 years of historical data) were screened and calculated. This trading
    strategy has been backtested for 60 months from Jan-2016 to Dec-2020. Users can screen for high 
    winning probability stock based on the winning rate. A high winning rate stock represent a highly
    cyclical pattern during a specified period during the year, and hence providing high confidence
    in capturing the minimum positive increase in stock prices.''')

    col2.markdown('''
    本平台提供股票歷史波動率分析。計算在規定的期間內（通常是從期權到期日的下一個星期到下一個期權的到期日）計算過去
    20 年股價的最低漲幅。目標正增長的範圍包括 100% 範圍（所有 20 年的最小正增長）以及 90% 的範圍（18 年內的最低
    正增長）。該交易策略捕捉了過去 20 年股票價格的最小正增長，並假設這個最小值今年同期將再次出現上漲幅度。

    這種交易策略需要大量的計算時間來篩選股票價格。 標普500中的305隻股票（具有超過 25 年的歷史數據）。本次交易策略
    已經從 2016 年 1 月到 2020 年 12 月進行了 60 個月的回測。用戶可以篩選高基於中獎率的中獎概率股票。高贏率股票
    代表高一年中特定時期的周期性模式，因此提供高置信度捕捉股票價格的最小正增長。
    ''')

    st.markdown('''
    ## *Example of this trading strategy*
    A stock investor planned to invest in Apple Inc. (Code: AAPL). The stock volatility strategy
    calculated that during the period 2021-09-15 yo 2021-10-15, AAPL has a 87% chance of 2.98%
    increase from 2021-10-01 (Low) to 2021-10-10 (High). On this date, the day low of AAPL was
    $139.11. Therefore it is predicted that on or before 2021-10-15, the stock price of AAPL will
    increase by $4.15 (2.98%).
    ''')

    st.image('AAPL_2021_10_01Example.png')
    st.write('---')

    '''
    ## Disclaimer
    In connection with, and as a condition of, the individual’s participation and usage of data provided 
    by **Datapy-StockVolatility**, the individual confirms, acknowledges and agrees as follows:

    1. The research result and analytical data is purely an educational and referential target range 
    provided by **Datapy-StockVolatility**.   It is not intended as a forum for the promotion of any 
    particular products or investments and neither **Datapy-StockVolatility** nor any of its officers, 
    directors, employees or representatives, in any way recommends or endorses any product, investment 
    or business opportunity which may be discussed at the Event.

    2. You agree to hold **Datapy-StockVolatility** and its presenters completely free from any liability 
    resulting from your attempts to use the strategies that are presented.   The use of all concepts, 
    techniques, and tools presented in the Event should be based on your own due diligence when it comes 
    to making business decisions, verified and supported by guidance obtained separately from your business
    advisory professionals, which we are not.  You hereby agree to consult a licensed business advisor, 
    attorney, accountant, financial professional or any other advisor.

    3. Further, should the undersigned choose to **enter into any contractual relationships** with any of 
    the Presenters at or subsequent to the Event, the undersigned does so at their own risk, and acknowledges
    that **Datapy-StockVolatility has neither responsibility for, nor liability with regards to, any 
    contracts or relationships** entered into between the undersigned and any third party Presenters at the Event.
    '''

def page_login():
    with st.form(key='my_form'):
        email = st.sidebar.text_input('Please enter your email address')
        password = st.sidebar.text_input('Please enter your password',type = 'password')

    login = st.sidebar.checkbox('Start')
    if login:
        # try:
            # user = auth.sign_in_with_email_and_password(email,password)
        st.sidebar.write("Login successful!")
        bio = st.sidebar.radio('Jump to',['Backtest Summary 回測總結', 'Backtest Results 回測結果', 
        'Multiple stocks', 'Prediction 個股預測','Open Interest 期權資金流', 'Tsang Channel 曾氏通道'], key='loggedin')
        if bio == 'Backtest Summary 回測總結':
            backtest_summary('success')
        elif bio =='Backtest Results 回測結果':
            page_data('success')
        elif bio == 'Multiple stocks':
            page_select_stock('success')
        elif bio == 'Open Interest 期權資金流':
            open_interest('success')
        elif bio == 'Tsang Channel 曾氏通道':
            tsang_channel('success')
        elif bio == 'Prediction 個股預測':
            indv_stock_pred('success')
        #     page_backtest_results('success')
        # elif bio == 'Data':
        #     page_data('success')
        # except:
        #     st.sidebar.write('Invalid UserID/password - Visitor Mode')
        #     bio = st.sidebar.radio('Jump to',['Backtest Results','Data'])
        #     if bio =='Backtest Results':
        #         page_backtest_results('failed')
        #     elif bio == 'Data':
        #         page_data('failed')

def backtest_summary(status):
    range_select = st.sidebar.selectbox('Range', ['100%', '90%'], key='range_select')

    col1, col2, col3 = st.columns(3)

    col1.subheader('Winning Probability')
    win_rate_select = col1.slider('', min_value=0, max_value=100, key='win_rate_select')
    col3.subheader('Rank by')
    sort_by_select = col3.selectbox('', ['Win Rate', 'Mean Volatility (%)', 'Win Rate Rank','Options Vol', 'Target Range Rank','Volume Rank','Total Score', 'EV'])
    col2.subheader('Expected Value')
    ev_select = col2.slider('', min_value=0, max_value=100)

    opt_volume_box = st.checkbox("Option Volume not zero")

    backtest_master_df = pd.read_csv('dataset/backtest_summary_{}.csv'.format(range_select))
    backtest_master_df['Win_Rate'] = backtest_master_df['Win_Rate'] * 100
    backtest_master_df = backtest_master_df[['stock', 'W','L','Min_vol', 'Win_Rate','Options Vol', 'WR_rank','TR_rank','Vol_rank','Total_score','EV']]
    backtest_master_df.columns = ['Stock', 'W','L','Mean Volatility (%)', 'Win Rate','Options Vol', 'Win Rate Rank','Target Range Rank','Volume Rank','Total Score','EV']
    display_df = backtest_master_df[(backtest_master_df['Win Rate']>=win_rate_select) & (backtest_master_df['EV']>=ev_select)].sort_values(sort_by_select, ascending=False)   
    if opt_volume_box:
        st.table(display_df[display_df['Options Vol']>0].assign(hack='').set_index('hack'))
    else:
        st.table(display_df.assign(hack='').set_index('hack'))

def page_data(status):
    # Retrieving tickers data
    if status == 'success':
        ticker_list = pd.read_csv('dataset/prediction_list.txt')
    elif status == 'failed':
        ticker_list = pd.read_csv('dataset/prediction_list_trial.txt')

    # Sidebar
    st.sidebar.subheader('Query parameters')
    ticket_list = ticker_list.sort_values('Stock', ascending=True, axis=0, inplace=True)
    tickerSymbol = st.sidebar.selectbox('Stock Ticker Symbol', ticker_list['Stock']) # Select ticker symbol
    st.sidebar.write('Stock select:', tickerSymbol)
    range_select = st.sidebar.selectbox('Range', ['100%', '90%'], key='range_select')
    start_date = st.sidebar.date_input("Start date", datetime.date(2020, 1, 1))
    end_date = st.sidebar.date_input("End date", datetime.date(2021, 9, 21))
    tickerData = yf.Ticker(tickerSymbol) # Get ticker data
    tickerDf = tickerData.history(period='1d', start=start_date, end=end_date) #get the historical prices for this ticker

    # Ticker information
    col1, col2 = st.columns(2)

    if tickerSymbol.startswith('^'):
        st.write(tickerSymbol)
    else:
        string_name = tickerData.info['longName']
        string_industry = 'Industry: ' + tickerData.info['industry']
        string_sector =   'Sector  :' + tickerData.info['sector']
        col1.header('**%s**' % string_name)
        col1.markdown(string_industry)
        col1.markdown(string_sector)

        string_logo = '<img src=%s>' % tickerData.info['logo_url']
        col2.markdown(string_logo, unsafe_allow_html=True)

    # ------------------------------------
    # Volatility Backtest Result
    # ------------------------------------
    st.header('**Volatility Backtest Result**')
    vol_backtest_df = pd.read_csv('dataset/backtest_summary_{}.csv'.format(range_select))
    if ((vol_backtest_df['stock'] == tickerSymbol)).any():
        month_vol_df_filtered = vol_backtest_df[vol_backtest_df['stock'] == tickerSymbol]
        st.write(month_vol_df_filtered[['Win_Rate', 'Min_vol', 'TR_rank', 'Vol_rank', 'Total_score' ,'EV']])
    else:
        st.write('Historic backtest not available.')
    # ------------------------------------
    # Volatility Prediction (Monthly)
    # ------------------------------------
    st.header('**Volatility Prediction (Monthly)**')
    month_vol_df = pd.read_csv('dataset/Monthly_prediction.csv')
    if ((month_vol_df['Stock'] == tickerSymbol)).any():
        month_vol_df_filtered = month_vol_df[month_vol_df['Stock'] == tickerSymbol]
        st.write(month_vol_df_filtered[['vol_day_start', 'vol_day_end', 'pos_change', 'Type', 'MDD_perc']])
    else:
        st.write('Historic volatility not available.')
    # ------------------------------------
    # Volatility Prediction
    # ------------------------------------
    st.header('**Volatility Prediction (Quaterly)**')
    quaterly_vol_df = pd.read_csv('dataset/Quaterly_prediction.csv')

    if ((quaterly_vol_df['Stock'] == tickerSymbol)).any():
        month_vol_df_filtered = quaterly_vol_df[quaterly_vol_df['Stock'] == tickerSymbol]
        st.write(month_vol_df_filtered[['vol_day_start', 'vol_day_end', 'pos_change', 'Type', 'MDD_perc']])
    else:
        st.write('Historic volatility not available.')
    # ------------------------------------
    # Print Previous Result
    # ------------------------------------
    if status == 'success':
        st.write('**Backtest Volatility Results**')
        backtest_df = pd.read_csv('dataset/backtest_summary.csv')
        backtest_df = backtest_df[backtest_df['stock'] == (tickerSymbol)]
        backtest_df = backtest_df[['stock','W','L','Min_vol', 'Win_Rate','Options Vol','Imp Vol','WR_rank','TR_rank','Vol_rank','Total_score','EV']]

        df = pd.read_csv('backtest_report/{}_20yr_pos_change_backtest.csv'.format(tickerSymbol))
        st.write('Target Volatility')
        gen_backtest_report(df, 'm1', range_select)[2]
        st.write('Month Volatility')
        gen_backtest_report(df, 'm1', range_select)[1]
        st.write('Backtest Result')
        gen_backtest_report(df, 'm1', range_select)[0]
    elif status == 'failed':
        st.write('**Backtest Volatility Results**')
        backtest_df = pd.read_csv('dataset/backtest_summary.csv')
        backtest_df = backtest_df[['stock','W','L','Min_vol', 'Win_Rate','Options Vol','Imp Vol','WR_rank',
        'TR_rank','Vol_rank','Total_score','EV']]
        backtest_df = backtest_df[backtest_df['stock'] == 'AMD']
        st.dataframe(backtest_df)
    
    # Ticker data
    st.header('**Ticker data**')
    st.write(tickerDf.tail(5))

    st.header('**Stock Price**')
    qf=cf.QuantFig(tickerDf,title='Stock Price Figure',legend='top',name='GS')
    fig = qf.iplot(asFigure=True)
    st.plotly_chart(fig)

    if tickerSymbol.startswith('^'):
        pass
    else:
        string_summary = tickerData.info['longBusinessSummary']
        st.info(string_summary)
        st.write('---')

def page_backtest_results(status):
    backtest_master_df = pd.read_csv('dataset/backtest_summary.csv').sort_values('stock', ascending=True)
    stock_list = backtest_master_df['stock'].unique()
    stock_selected = st.selectbox('Select', (stock_list), key='option_select')

    st.write('Stock select:', stock_selected)
    status == 'success'
    if status == 'success':
        st.write('**Backtest Volatility Results**')
        backtest_df = pd.read_csv('dataset/backtest_summary_{}.csv'.format(range_select))
        backtest_df = backtest_df[backtest_df['stock'] == (stock_selected)]
        backtest_df = backtest_df[['stock','W','L','Min_vol', 'Win_Rate','Options Vol','Imp Vol','WR_rank', 'TR_rank','Vol_rank','Total_score','EV']]
        st.dataframe(backtest_df)

        df = pd.read_csv('backtest_report/{}_20yr_pos_change_backtest.csv'.format(stock_selected))
        st.write('Target Volatility')
        gen_backtest_report(df, 'm1', '100%')[2]
        st.write('Month Volatility')
        gen_backtest_report(df, 'm1', '100%')[1]
        st.write('Backtest Result')
        gen_backtest_report(df, 'm1', '100%')[0]
    elif status == 'failed':
        st.write('**Backtest Volatility Results**')
        backtest_df = pd.read_csv('dataset/backtest_summary.csv')
        backtest_df = backtest_df[['stock','W','L','Min_vol', 'Win_Rate','Options Vol','Imp Vol','WR_rank',
        'TR_rank','Vol_rank','Total_score','EV']]
        backtest_df = backtest_df[backtest_df['stock'] == 'AMD']
        st.dataframe(backtest_df)

def indv_stock_pred(status):
    # Retrieving tickers data
    if status == 'success':
        ticker_list = pd.read_csv('dataset/prediction_list.txt')
    elif status == 'failed':
        ticker_list = pd.read_csv('dataset/prediction_list_trial.txt')
    # Sidebar
    st.sidebar.subheader('Query parameters')
    # ticker_list = pd.read_csv('prediction_list.txt')
    ticket_list = ticker_list.sort_values('Stock', ascending=True, axis=0, inplace=True)
    tickerSymbol = st.sidebar.selectbox('Stock Ticker Symbol', ticker_list['Stock']) # Select ticker symbol
    st.sidebar.write('Stock select:', tickerSymbol)
    month_vol_df = pd.read_csv('dataset/Monthly_prediction.csv')
    month_vol_df['Type'] = month_vol_df['Type'].str.replace(r'_m1', '')
    month_query_list = month_vol_df['Type'].unique()
    month_query = st.sidebar.selectbox('Select', (month_query_list), key='month_query_select')

    tickerData = yf.Ticker(tickerSymbol) # Get ticker data

    if tickerSymbol.startswith('^'):
        st.write(tickerSymbol)
    else:
        col1, col2 = st.columns(2)
        string_name = tickerData.info['longName']
        string_industry = 'Industry: ' + tickerData.info['industry']
        string_sector =   'Sector  :' + tickerData.info['sector']
        col1.header('**%s**' % string_name)
        col1.write(string_industry)
        col1.write(string_sector)

    # ------------------------------------
    # Volatility Backtest Result
    # ------------------------------------
    st.header('**Volatility Backtest Result**')
    vol_backtest_df = pd.read_csv('dataset/backtest_summary_100%.csv')
    if ((vol_backtest_df['stock'] == tickerSymbol)).any():
        backtest_vol_df_filtered = vol_backtest_df[vol_backtest_df['stock'] == tickerSymbol]
        st.write(backtest_vol_df_filtered[['Win_Rate', 'Min_vol', 'TR_rank', 'Vol_rank', 'Total_score' ,'EV']])
    else:
        st.write('Historic backtest not available.')
    # ------------------------------------
    # Volatility Prediction (Monthly)
    # ------------------------------------
    month_query = month_query + '_m1'
    st.header('**Volatility Prediction (Monthly)**')
    month_vol_df = pd.read_csv('dataset/Monthly_prediction.csv')
    if ((month_vol_df['Stock'] == tickerSymbol)).any():
        month_vol_df_filtered = month_vol_df[(month_vol_df['Stock'] == tickerSymbol) & (month_vol_df['Type'] == month_query)]
        col1, col2 = st.columns(2)
        col1.markdown('''
        [ {} from {} to {} ] \n
        Winning rate of {} is {:.2f}%. \n
        Based on volatility backtest with 20 years of data \n
        Will increase {:.2f}% from {} (Low). \n
        There was a maximum draw down of {:.2f}%.
        '''.format(tickerSymbol, month_vol_df_filtered.iloc[0]['vol_day_start'], month_vol_df_filtered.iloc[0]['vol_day_end'], 
        tickerSymbol, backtest_vol_df_filtered.iloc[0]['Win_Rate']*100,
        month_vol_df_filtered.iloc[0]['pos_change'], month_vol_df_filtered.iloc[0]['vol_day_start'],
        month_vol_df_filtered.iloc[0]['MDD_perc']))

        col2.markdown('''
        [ {} {} to {} ] \n
        以16-20年60個月回測的結果: 勝率為 {:.2f}%. \n
        {} 將會由 {} 低位上升 {:.2f}%. \n
        過去10年此段期間之最大回撤率為 {:.2f}%.
        '''.format(tickerSymbol, month_vol_df_filtered.iloc[0]['vol_day_start'], month_vol_df_filtered.iloc[0]['vol_day_end'], 
        backtest_vol_df_filtered.iloc[0]['Win_Rate']*100,
        tickerSymbol, month_vol_df_filtered.iloc[0]['vol_day_start'], month_vol_df_filtered.iloc[0]['pos_change'], 
        month_vol_df_filtered.iloc[0]['MDD_perc']))
    else:
        st.write('Historic volatility not available.')
    # ------------------------------------
    # Volatility Prediction
    # ------------------------------------
    st.header('**Volatility Prediction (Quaterly)**')
    quaterly_vol_df = pd.read_csv('dataset/Quaterly_prediction.csv')

    if ((quaterly_vol_df['Stock'] == tickerSymbol)).any():
        month_vol_df_filtered = quaterly_vol_df[quaterly_vol_df['Stock'] == tickerSymbol]
        st.write(month_vol_df_filtered[['vol_day_start', 'vol_day_end', 'pos_change', 'Type', 'MDD_perc']])
    else:
        st.write('Historic volatility not available.')

def page_select_stock(status):
    # st.write('Page under construction')
    col1, col2, col3 = st.columns(3)
    start_date = col1.text_input('Start Date', '10-15')
    end_date = col2.text_input('End Date', '10-24')
    sort_by_metric = col3.selectbox('Rank by', ['pos_change','Win Rate','Win Rate Rank', 'Target Range Rank','Volume Rank','Total Score', 'EV'])
    opt_volume_box = st.checkbox("Option Volume not zero")

    month_vol_df = pd.read_csv('dataset/Monthly_prediction.csv')
    month_result = month_vol_df[(month_vol_df['vol_day_start']>=start_date) & (month_vol_df['vol_day_start']<=end_date)]
    diplay_df1 = month_result[['Stock', 'vol_day_start', 'vol_day_end', 'pos_change']]
    backtest_master_df = pd.read_csv('dataset/backtest_summary.csv')
    backtest_master_df['Win_Rate'] = backtest_master_df['Win_Rate'] * 100
    backtest_master_df = backtest_master_df[['stock', 'Win_Rate','Options Vol', 'WR_rank','TR_rank','Vol_rank','Total_score','EV']]
    backtest_master_df.columns = ['Stock', 'Win Rate','Options Vol', 'Win Rate Rank','Target Range Rank','Volume Rank','Total Score','EV']

    display_df = pd.merge(diplay_df1, backtest_master_df, on='Stock')
    if opt_volume_box:
        st.table(display_df[display_df['Options Vol']>0].sort_values(sort_by_metric, ascending=False))
    else:
        st.table(display_df.sort_values(sort_by_metric, ascending=False))
    # st.dataframe(display_df[['Stock', 'vol_day_start', 'vol_day_end', 'pos_change']])

def open_interest(status):
    st.markdown('''
    # Open Interest 
    This page provide current open option interest for all avaialble stocks. Please input stock name.
    ''')
    col1, col2 = st.columns(2)
    stock = col1.text_input('Stock', 'AAPL')
    date = col2.selectbox('# Date', ['2021-11-19', '2021-12-17', '2022-01-21', '2022-02-18', '2022-03-18', '2022-04-14'])
    stock_value_df = yf.Ticker(stock)
    opt = stock_value_df.option_chain(date)

    ticker = yf.Ticker(stock)
    todays_data = ticker.history(period='1d')
    today_price = todays_data['Close'][0]

    fig, ax = plt.subplots(figsize=(12, 9), dpi=80)
    opt_final = pd.merge(opt.calls, opt.puts, on='strike')
    opt_final = opt_final[['strike', 'openInterest_x', 'openInterest_y']]
    opt_final.columns = ['strike', 'calls', 'puts']
    opt_final['total'] = opt_final['calls'] + opt_final['puts']
    opt_final['strike_dif'] = opt_final['strike'].diff()

    # opt_strike_diff = 5 if today_price > 500 else 2 if today_price > 100 else 0.5
    opt_final = opt_final[(opt_final['strike'] >= today_price *0.8) & (opt_final['strike'] <= today_price *1.2) ]
    x_lim_max = opt_final['calls'].max() if opt_final['calls'].max() > opt_final['puts'].max() else opt_final['puts'].max()
    plt.xlim(0, x_lim_max+500)
    bar_width = 2.5 if today_price > 500 else 0.5 if today_price > 100 else 0.25
    rects1 = plt.barh(opt_final.strike, opt_final.calls, bar_width, label='Calls')
    rects2 = plt.barh(opt_final.strike - bar_width, opt_final.puts, bar_width, label='Puts', alpha=0.5)

    plt.hlines(today_price, 0, opt_final.total.max()/2, colors='black', linestyles='dashed', linewidth=2.0, label='Current Price')
    plt.ylabel('Strike Price', size=15)
    plt.xlabel('Open Intesest', size=15)
    today_price_print = round(today_price, 0)
    strike_range_print = 100 if today_price > 500 else 30 if today_price > 100 else 20
    plt.ylim(today_price_print-strike_range_print,today_price_print+strike_range_print)
    plt.yticks(opt_final.strike)
    plt.legend(prop={'size': 13}, bbox_to_anchor=(1.0, 1), loc='best')
    ax.set_title(f'{stock} Option Open Interest for {date}', size=18)
    ax.tick_params(axis='both', which='major', labelsize=15)
    st.pyplot(fig)

def tsang_channel(status):
    stock = st.text_input('Stock', 'AAPL')
    period = st.selectbox('Period', ['5y', '2y', '1y', '20y', '10y'])
    # stock = stock
    ticker = yf.Ticker(stock)
    ticker_df = ticker.history(period=period)

    ticker_df['date'] = ticker_df.index
    ticker_df = ticker_df.reset_index()
    ticker_df['row_id'] = ticker_df.index

    x = ticker_df[['row_id']]
    y = ticker_df[['Close']]
    lr = LinearRegression().fit(x, y)
    ticker_df['intercept'] = float(lr.intercept_)
    ticker_df['slope'] = float(lr.coef_)
    ticker_df['TL'] = ticker_df['intercept'] + ticker_df['slope'] * ticker_df['row_id']
    ticker_df['H'] = ticker_df['Close'] - ticker_df['TL']
    ticker_df['H_std'] = ticker_df['H'].std()
    ticker_df['H1'] = ticker_df['TL'] + ticker_df['H_std'] * 2
    ticker_df['H2'] = ticker_df['TL'] + ticker_df['H_std'] * 1
    ticker_df['H3'] = ticker_df['TL'] - ticker_df['H_std'] * 1
    ticker_df['H4'] = ticker_df['TL'] - ticker_df['H_std'] * 2
    ax, fig = plt.subplots()
    plt.figure(figsize=(12, 5))
    # px.line(ticker_df['date'], y, color='black')
    # plt.plot(ticker_df['date'], y, color='black')
    # plt.plot(ticker_df['date'], ticker_df['H1'], color = 'red')
    # plt.plot(ticker_df['date'], ticker_df['H2'] , color = 'orange')
    # plt.plot(ticker_df['date'], ticker_df['TL'] , color = 'blue')
    # plt.plot(ticker_df['date'], ticker_df['H3'] , color = 'cyan')
    # plt.plot(ticker_df['date'], ticker_df['H4'] , color = 'green')
    # plt.title('Tsangs Channel on {} for the past 10 years'.format(stock))
    # st.pyplot(fig=plt)
    import plotly.io as pio
    pio.templates.default = "plotly_dark"
    fig = px.line(ticker_df, x="date", y=["Close", 'H1' ,'H2', 'TL', 'H3', 'H4'], width=1200, height=800)
    # fig.update_layout(margin=dict(l=10, r=10, t=50, b=50))
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
