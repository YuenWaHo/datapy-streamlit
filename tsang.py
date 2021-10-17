import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def tsang_fig(stock, time_period):
    stock = '^GSPC'
    ticker = yf.Ticker(stock)
    ticker_df = ticker.history(period=time_period)

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
    ticker_df['H1'] = ticker_df['TL'] + ticker_df['H_std'] * 3
    ticker_df['H2'] = ticker_df['TL'] + ticker_df['H_std'] * 1.5
    ticker_df['H3'] = ticker_df['TL'] - ticker_df['H_std'] * 1.5
    ticker_df['H4'] = ticker_df['TL'] - ticker_df['H_std'] * 3
    ax, fig = plt.subplots()
    # plt.figure(figsize=(16, 9))
    plt.plot(ticker_df['date'], y, color='black')
    plt.plot(ticker_df['date'], ticker_df['H1'], color = 'red')
    plt.plot(ticker_df['date'], ticker_df['H2'] , color = 'orange')
    plt.plot(ticker_df['date'], ticker_df['TL'] , color = 'blue')
    plt.plot(ticker_df['date'], ticker_df['H3'] , color = 'cyan')
    plt.plot(ticker_df['date'], ticker_df['H4'] , color = 'green')
    plt.title('Tsangs Channel on {} for the past 10 years'.format(stock))
    return fig

# tsang_fig('AAPL','20y')