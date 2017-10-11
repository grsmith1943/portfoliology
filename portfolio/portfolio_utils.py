import re
import pandas as pd
from yahoo_finance import Share


def get_position_metrics(df):
    """Gets key metrics for tickers in input dataframe from Yahoo! Finance API"""

    # Placeholders for new columns
    df["Current Price"] = 0.
    df["Change"] = 0.

    # iterate through each position to populate with realtime (er, 15-minute delayed) data
    for row in df.itertuples():

        # get ticker data from Y! Finance API
        ticker = row.Symbol
        ticker_data = Share(ticker)

        # parse key metrics
        price = ticker_data.get_price() or '0'
        change = ticker_data.get_change() or '0'

        # string conversions, unit parsing, etc
        price = float(re.sub(r'[A-Z]', '', price))
        change = float(re.sub(r'[A-Z]', '', change))

        # assign to relevant columns
        df.loc[row.Index, "Current Price"] = price
        df.loc[row.Index, "Change"] = change

    # derived values needed before adding totals row
    df["Market Value"] = df["Shares"] * df["Current Price"]
    df["Day's Gain/Loss"] = df["Shares"] * df["Change"]

    # sort by largest position (b/c I like it that way)
    df.sort_values("Market Value", inplace=True, ascending=False)

    # create and append totals row
    totals_df = pd.DataFrame({
        "Name": "Totals",
        "Symbol": "",
        "Shares": "",
        "Cost basis": df["Cost basis"].sum(),
        "Current Price": "",
        "Change": df["Change"].sum(),
        "Market Value": df["Market Value"].sum(),
        "Day's Gain/Loss": df["Day's Gain/Loss"].sum(),
    }, index=[0])

    df = df.append(totals_df, ignore_index=True)

    # derived values needed after adding totals row
    df["Total Gain/Loss"] = df["Market Value"] - df["Cost basis"]
    df["Overall Return"] = (100. * df["Total Gain/Loss"] / df["Cost basis"]).round(2)
    df["Change"] = df["Change"].round(2)
    df["Market Value"] = df["Market Value"].round(2)
    df["Total Gain/Loss"] = df["Total Gain/Loss"].round(2)
    df["Day's Gain/Loss"] = df["Day's Gain/Loss"].round(2)

    # final column ordering
    cols = ["Name", "Symbol", "Current Price", "Change", "Shares", "Cost basis",
            "Market Value", "Total Gain/Loss", "Day's Gain/Loss", "Overall Return"]

    return df[cols]
