# datapy-streamlit
streamlit

This platform provides stock historical volatility analysis. The calculation is within a specified period (typically the next Monday trailing the end date of the option expiry date to the next option 
expiry date) and calculate the minimum increase in stock price in the past 20 years. The target ranges of positive increase include the 100% range (minimum positive increase in all 20 years) 
and the 90% range (minimum positive increase in 18 years). This trading strategy captures the minimum positive increase in stock prices over the past 20 years, and assumed that this minimum 
range of increase will occur again during the same period this year. 

This trading strategy require huge computational time for screening stock prices. 305 out of S&P500 stock (With over 25 years of historical data) were screened and calculated. This trading
strategy has been backtested for 60 months from Jan-2016 to Dec-2020. Users can screen for high winning probability stock based on the winning rate. A high winning rate stock represent a highly
 cyclical pattern during a specified period during the year, and hence providing high confidence in capturing the minimum positive increase in stock prices.
