#!/usr/bin/env python3
import sys
from yahoo_finance import Share
import argparse
import dateutil.parser
import pandas as pd
from pathlib import Path
import threading
import time
from functools import wraps

#pd.np.seterr(invalid='raise')

def parse_path(ticker_path):
    """
    Returns a pathlib.Path object if the path
    is a file that exists

    Args:
        ticker_path (str): A path string

    Returns:
        pathlib.Path: Path object if the path string is a valid file

    """
    q = Path(ticker_path)
    if q.exists() and q.is_file():
        return q

    raise FileNotFoundError("The path does not exist or is not a file")

def read_tickers(ticker_file):
    """
    Reads the ticker_file and returns its contents

    Args:
        ticker_file (pathlib.Path): `pathlib.Path` object which is a valid file path

    Returns:
        list: Contents of the lines in the file

    """
    try:
        with ticker_file.open() as f:
            lines = f.read().split('\n')
    except IOError:
        raise IOError("Could not open file {}. Check if file exists or try again".format(ticker_file))

    return lines

def get_data(ticker, start, end):
    """
    Returns a pd.DataFrame with Date and Adj_Close data for the ticker history
    from start date to end Date

    Args:
        ticker (str): The ticker label
        start  (str): The starting date in format %Y-%m-%d (YYYY-mm-dd)
        end    (str): The ending date in format %Y-%m-%d (YYYY-mm-dd)

    Returns:
        pd.DataFrame: DataFrame with Adj_Close values from start to end dates

    Note: Will raise ValueError if there is no data for the ticker

    """
    if not ticker:
        raise ValueError("Empty string")
    ticker = ticker.strip()
    share = Share(ticker)
    data = share.get_historical(start, end)

    if not data:
        raise ValueError("No data found")

    data = pd.DataFrame(data)
    data = data.loc[:, ["Date", "Adj_Close"]]
    data.Date = pd.to_datetime(data.Date)
    data.Adj_Close = pd.to_numeric(data.Adj_Close)

    data['Returns'] = data.Adj_Close/data.Adj_Close.shift() - 1

    return data

def thread_get_data(ticker, start, end, data_dict, Lock):
    """
    Helper function to thread the `get_data` function

    Creates a key `ticker` in the `data_dict` dictionary and sets it's value
    to be a dictionary with key `data` and value to be the DataFrame

    Args:
        ticker (str): See `get_data`
        start  (str): See `get_data`
        end    (str): See `get_data`
        data_dict (dict): Dictionary that will contain all the data
        Lock (threading.Lock): threading.Lock() object for printing

    """

    try:
        data = get_data(ticker, start, end)
    except ValueError as e:
        with Lock:
            print(ticker, type(e).__name__, e)
    except Exception as e:
        with Lock:
            print(ticker, type(e).__name__, e)
    else:
        data_dict[ticker] = {'data': data}

def timer(f):
    """
    Function decorator to time functions
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.clock()
        data = f(*args, **kwargs)
        end = time.clock()
        print("\n{} took {} seconds".format(f.__name__, end-start))
        return data
    return wrapper

@timer
def threaded_get_data(ticker_list, start_date, end_date):
    """
    Runs multiple threads to return the data dictionary of all the tickers

    Args:
        ticker_list (list): List of ticker names
        start_date (str): Start date in the format %Y-%m-%d (YYYY-mm-dd)
        end_date (str): End date in the format %Y-%m-%d (YYYY-mm-dd)

    Returns:
        dict: Dictionary of DataFrames
        structure of dict
        {
            'AAPL': {
                        'data': pd.DataFrame
                    }
        }

    """
    data_dict = {}
    threads = []
    Lock = threading.Lock()
    for ticker in ticker_list:
        _thread = threading.Thread(target=thread_get_data, args=(ticker, start_date, end_date, data_dict, Lock))
        threads.append(_thread)
        _thread.start()

    for _thread in threads:
        _thread.join()

    return data_dict

@timer
def vanilla_get_data(ticker_list, start_date, end_date):
    """

    See documentation for `threaded_get_data`

    """
    data_dict = {}
    for ticker in ticker_list:
        ticker = ticker.strip().split()[0]
        try:
            data_dict[ticker] = {'data': get_data(ticker, start_date, end_date)}
        except ValueError as e:
            print(ticker, type(e).__name__, e)
        except Exception as e:
            print(ticker, type(e).__name__, e)
    return data_dict

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("ticker_path", help="File name or path to file with list of tickers")
    parser.add_argument('start_date', help="Start date in format yyyy-mm-dd")
    parser.add_argument('end_date', help="End date in format yyyy-mm-dd")
    parser.add_argument('-o', '--output_file', help="Output file name defaults to 'output.txt'",
                        nargs='?', default='output.txt')
    parser.add_argument('-m', '--method', nargs='?', default='threaded',
                        help='Method to extract data "vanilla" or "threaded"')
    args = parser.parse_args()

    ticker_list = read_tickers(parse_path(args.ticker_path))
    start_date = dateutil.parser.parse(args.start_date).strftime("%Y-%m-%d")
    end_date = dateutil.parser.parse(args.end_date).strftime("%Y-%m-%d")

    if args.method == 'threaded':
        data_dict = threaded_get_data(ticker_list, start_date, end_date)
    else:
        data_dict = vanilla_get_data(ticker_list, start_date, end_date)

    with open(args.output_file, "w") as outfile:
        outfile.write('Start Date: {} \t End Date: {}\n'.format(start_date, end_date))
        for stock, stock_dict in sorted(data_dict.items()):

            returns = stock_dict['data'].Returns

            stock_dict["mean"] = returns.mean()
            stock_dict["variance"] = returns.var()
            stock_dict["autocor_1"] = returns.autocorr(1)
            stock_dict["autocor_5"] = returns.autocorr(5)
            stock_dict["autocor_10"] = returns.autocorr(10)

            outfile.write("-------\n{}\nmean: {}\nvariance: {}\nautocorrelation (1-day): {}\n"
                  "autocorrelation (5-day): {}\nautocorrelation (10-day): {}\n".format(
                            stock, stock_dict['mean'], stock_dict['variance'],
                            stock_dict['autocor_1'], stock_dict['autocor_5'],
                            stock_dict['autocor_10']
                  ))
