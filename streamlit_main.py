import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import cufflinks as cf
import datetime
import pyrebase
import matplotlib.pyplot as plt

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
    st.markdown('''
    - App built by [DataPy](www.youtube.com/channel/UCI7auEnrAG2XAlGjdGN2Gsg)
    - Historic stock price volatility analysis
    
    If you are interested in using this stock volatility analysis in gaining consistent profit. 
    Please contact us for more details.'''
    
    ''' 
    ### Telegram - [stock_vol](https://t.me/) / WhatsApp: [Whatsapp](https://wa.me/)
    ''')
    st.write('---')
    
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
      in capturing the minimum positive increase in stock prices.

    ## *Example of this trading strategy*

    A stock investor planned to invest in Apple Inc. (Code: AAPL). The stock volatility strategy 
    calculated that during the period 2021-09-15 yo 2021-10-15, AAPL has a 87% chance of 2.98% 
    increase from 2021-10-01 (Low) to 2021-10-10 (High). On this date, the day low of AAPL was 
    $139.11. Therefore it is predicted that on or before 2021-10-15, the stock price of AAPL will 
    increase by $4.15 (2.98%). 
    '''
    
    st.image('AAPL_2021_10_01Example.png')
    st.write('---')
    # disclaimer_text = []
    st.markdown("""
    <style>
    .small-font {
        font-size:25px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('''
    Disclaimer
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
    ''')

def page_login():
    with st.form(key='my_form'):
        email = st.sidebar.text_input('Please enter your email address')
        password = st.sidebar.text_input('Please enter your password',type = 'password')

    login = st.sidebar.checkbox('Start')
    if login:
        # try:
            # user = auth.sign_in_with_email_and_password(email,password)
        st.sidebar.write("Login successful!")
        bio = st.sidebar.radio('Jump to',['Backtest Summary', 'Backtest Results'], key='loggedin')
        if bio == 'Backtest Summary':
            backtest_summary('success')
        elif bio =='Backtest Results':
            page_data('success')
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
    col1, col2, col3 = st.columns(3)

    col1.subheader('Winning Probability')
    win_rate_select = col1.slider('', min_value=70, max_value=100)
    col3.subheader('Rank by')
    sort_by_select = col3.selectbox('', ['Win Rate', 'Mean Volatility (%)', 'Win Rate Rank', 'Target Range Rank','Volume Rank','Total Score', 'EV'])
    col2.subheader('Expected Value')
    ev_select = col2.slider('', min_value=0, max_value=100)

    backtest_master_df = pd.read_csv('dataset/backtest_summary.csv')
    backtest_master_df['Win_Rate'] = backtest_master_df['Win_Rate'] * 100
    backtest_master_df = backtest_master_df[['stock', 'W','L','Min_vol', 'Win_Rate','Options Vol', 'WR_rank','TR_rank','Vol_rank','Total_score','EV']]
    backtest_master_df.columns = ['Stock', 'W','L','Mean Volatility (%)', 'Win Rate','Options Vol', 'Win Rate Rank','Target Range Rank','Volume Rank','Total Score','EV']
    display_df = backtest_master_df[(backtest_master_df['Win Rate']>=win_rate_select) & (backtest_master_df['EV']>=ev_select)].sort_values(sort_by_select, ascending=False)   
    st.table(display_df.assign(hack='').set_index('hack'))

def page_backtest_results(status):
    backtest_master_df = pd.read_csv('dataset/backtest_summary.csv').sort_values('stock', ascending=True)
    stock_list = backtest_master_df['stock'].unique()
    stock_selected = st.selectbox('Select', (stock_list), key='option_select')
    st.write('Stock select:', stock_selected)
    status == 'success'
    if status == 'success':
        st.write('**Backtest Volatility Results**')
        backtest_df = pd.read_csv('dataset/backtest_summary.csv')
        backtest_df = backtest_df[backtest_df['stock'] == (stock_selected)]
        backtest_df = backtest_df[['stock','W','L','Min_vol', 'Win_Rate','Options Vol','Imp Vol','WR_rank',
        'TR_rank','Vol_rank','Total_score','EV']]
        # selected = backtest_df['stock'].isin(stock_selected)
        # backtest_df = backtest_df[selected]
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
        
def page_data(status):
    # Retrieving tickers data
    if status == 'success':
        ticker_list = pd.read_csv('dataset/prediction_list.txt')
    elif status == 'failed':
        ticker_list = pd.read_csv('dataset/prediction_list_trial.txt')

    # ticker_list = pd.read_csv('prediction_list.txt')
    ticket_list = ticker_list.sort_values('Stock', ascending=True, axis=0, inplace=True)
    tickerSymbol = st.sidebar.selectbox('Stock Ticker Symbol', ticker_list['Stock']) # Select ticker symbol
    st.sidebar.write('Stock select:', tickerSymbol)
    # Sidebar
    st.sidebar.subheader('Query parameters')
    start_date = st.sidebar.date_input("Start date", datetime.date(2020, 1, 1))
    end_date = st.sidebar.date_input("End date", datetime.date(2021, 9, 21))
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

    # ------------------------------------
    # Volatility Backtest Result
    # ------------------------------------
    st.header('**Volatility Backtest Result**')
    vol_backtest_df = pd.read_csv('dataset/backtest_summary.csv')
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
    # status == 'success'
    if status == 'success':
        st.write('**Backtest Volatility Results**')
        backtest_df = pd.read_csv('dataset/backtest_summary.csv')
        backtest_df = backtest_df[backtest_df['stock'] == (tickerSymbol)]
        backtest_df = backtest_df[['stock','W','L','Min_vol', 'Win_Rate','Options Vol','Imp Vol','WR_rank','TR_rank','Vol_rank','Total_score','EV']]
        # st.dataframe(backtest_df)

        df = pd.read_csv('backtest_report/{}_20yr_pos_change_backtest.csv'.format(tickerSymbol))
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
    
    # Ticker data
    st.header('**Ticker data**')
    st.write(tickerDf.tail(5))

    st.header('**Stock Price**')
    qf=cf.QuantFig(tickerDf,title='Stock Price Figure',legend='top',name='GS')
    fig = qf.iplot(asFigure=True)
    st.plotly_chart(fig)

    string_summary = tickerData.info['longBusinessSummary']
    st.info(string_summary)
    st.write('---')

if __name__ == "__main__":
    main()