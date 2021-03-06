# IEOR 4500: Applications Programming for FE


## Group Members

- Andrew Chen
- Asish Mahapatra
- Cathy Wang
- Samantha Lam
- Sebastian Ortega

## Assignment 1

### Problem Statement

> For this assignment you need to first install the Yahoo finance package and then use the Python script I provided to download the Russell 1000 closing prices for a six-month period (any six month period).
>
> Then, for each asset in the index, you should compute its daily return (one value per each day), the mean return and variance of return over the six-month period.
>
> Finally, compute the autocorrelation of returns (not prices) using a time window of 1 day, 5 days and 10 days.

### Usage

    python3 myprices.py russell_1000_ticker.txt
- Assumes the file with list of ticker labels exists in the same directory
- Modify the date ranges inside the program

    ```py
    89 for line in lines:
    90     ticker = line.strip()
    91     print(ticker,)
    92     if ticker:
    93         prices[ticker] = get_stats(ticker, '2010-01-01', '2010-07-01')
    94     count += 1
    ```

- Outputs `daily_returns.csv` which has the ticker labels as columns and dates as rows and contains the daily returns of the tickers.

    | Date  | A  | AA  | AAL  | ... |
    |-------|----------|----------|----------|-----|
    | 2010-06-30 | -0.00528 | -0.00099 | 0.00465 | ... |
    | 2010-06-29 | -0.02670 | -0.02708 | 0.00820 | ... |
    | ...   | ...      | ...      | ...      | ... |

- Outputs `ticker_statistics.csv` which has ticker labels as rows and statistics (mean, variance, 1-day/5-day/10-day autocorrelation as columns)

    | Ticker | Mean     | Variance | Autocorrelation_1 | Autocorrelation_5 | Autocorrelation_10 |
    |--------|----------|----------|-------------------|-------------------|--------------------|
    | A      | -0.00063 | 0.00038  | -0.06364          | -0.00812          | 0.06184            |
    | AA     | -0.00367 | 0.00072  | -0.12330          | -0.05315          | 0.05581            |
    | ...    | ...      | ...      | ...               | ...               | ...                |
