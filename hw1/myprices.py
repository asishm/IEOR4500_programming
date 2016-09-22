#!/usr/bin/python3
import sys
from yahoo_finance import Share
from pprint import pprint
import time

def get_data(ticker, start, end):
    try:
        share = Share(ticker)
        ticker_data = share.get_historical(start, end)
    except Exception as e:
        time.sleep(0.1)
        print(ticker, e)
        return get_data(ticker, start, end)
    try:
        dates = [data['Date'] for data in ticker_data]
        adj_close = [float(data['Adj_Close']) for data in ticker_data]
        result = {'Date': dates, 'Adj_Close': adj_close}
    except Exception as e:
        print(ticker, type(e), type(e).__name__, e)
    else:
        return result

def mean(alist):
    try:
        _mean = sum(alist)/len(alist)
    except ZeroDivisionError:
        return "NaN"
    return _mean

def variance(alist, minus_1=True):
    if not alist:
        return "NaN"
    try:
        _mean = mean(alist)
        sum_var = sum((item - _mean)**2 for item in alist)
        _var = sum_var/(len(alist) - 1) if minus_1 else sum_var/len(alist)
    except (TypeError, ZeroDivisionError):
        return "NaN"
    return _var

def autocorr(alist, shift=1):
    shifted = alist[shift:]
    blist = alist[:-shift]
    if len(blist) != len(shifted) or len(alist) <= shift:
        return 'NaN'
    _mean, _var = mean(blist), variance(blist)
    shift_mean, shift_var = mean(shifted), variance(shifted)
    try:
        sum_cor = sum((a - _mean)*(b - shift_mean) for a,b in zip(blist, shifted))
        autocor = sum_cor/((len(shifted)-1)*_var**0.5 * shift_var**0.5)
    except (TypeError, ZeroDivisionError) as e:
        return "NaN"
    return autocor


def get_stats(ticker, start, end):
    data = get_data(ticker, start, end)
    date = data['Date']
    adj_close = data['Adj_Close']
    returns = [a/b - 1 for a,b in zip(adj_close, adj_close[1:])]
    _mean = mean(returns)
    _var = variance(returns)
    autocor_1 = autocorr(returns, 1)
    autocor_5 = autocorr(returns, 5)
    autocor_10 = autocorr(returns, 10)
    return {'Date': date[1:], 'Returns': returns, 'Mean': _mean, 'Variance': _var,
            'Autocor_1': autocor_1, 'Autocor_5': autocor_5, 'Autocor_10': autocor_10}

if len(sys.argv) != 2:  # the program name and the datafile
  # stop the program and print an error message
  sys.exit("usage: read1.py datafile ")

filename = sys.argv[1]

print("input", sys.argv[1])

try:
    with open(filename, 'r') as f:
        lines = list(filter(None,f.read().split('\n')))
except (IOError, FileNotFoundError):
    print ("Cannot open file {}".format(filename))
    sys.exit("bye")

count = 1
prices = {}
start = time.clock()

for line in lines:
    ticker = line.strip()
    print(ticker,)
    if ticker:
        prices[ticker] = get_stats(ticker, '2010-01-01', '2010-07-01')
    count += 1
    # if count == 10:
    #     break

dates = prices[max(prices, key = lambda x: len(prices[x]['Date']))]["Date"]
with open("daily_returns.csv", "w") as csvfile:
    csvfile.write("DATE,{}\n".format(','.join(ticker.strip() for ticker in sorted(prices.keys()))))
    for date in dates:
        s = [date]
        for ticker in sorted(prices.keys()):
            ticker = ticker.strip()
            try:
                date_index = prices[ticker]['Date'].index(date)
            except ValueError:
                s.append("N/A")
            else:
                s.append("{:.5f}".format(prices[ticker]['Returns'][date_index]))
        csvfile.write("{}\n".format(','.join(s)))

with open("ticker_statistics.csv", "w") as statfile:
    statfile.write("Ticker,Mean,Variance,Autocorrelation_1,Autocorrelation_5,Autocorrelation_10\n")
    #print(prices['FOXA'])
    for ticker in sorted(prices.keys()):
        stats = prices[ticker]
        s = ','.join("{:.5f}".format(stats[stat]) if isinstance(stats[stat], float) else stats[stat]
                        for stat in ['Mean', 'Variance', 'Autocor_1', 'Autocor_5', 'Autocor_10'])
        statfile.write("{},{}\n".format(ticker,s))
