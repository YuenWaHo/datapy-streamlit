import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]

def opt_int_graph(stock, date):
    stock = stock
    date = date
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
    plt.tight_layout()
    return fig