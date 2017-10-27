import re
import pandas as pd
from yahoo_finance import Share


def get_position_metrics(df):
    """Gets key metrics for tickers in input dataframe from Yahoo! Finance API"""

    # Placeholders for new columns
    df["Last Price ($)"] = 0.
    df["Change ($)"] = 0.
    df["Day's Change (%)"] = 0.

    # iterate through each position to populate with realtime (er, 15-minute delayed) data
    for row in df.itertuples():

        # get ticker data from Y! Finance API
        ticker = row.Symbol
        ticker_data = Share(ticker)

        # parse key metrics
        price = ticker_data.get_price() or '0'
        change = ticker_data.get_change() or '0'
        pct_change = ticker_data.get_percent_change() or '0'

        # string conversions, unit parsing, etc
        price = float(re.sub(r'[A-Z]', '', price))
        change = float(re.sub(r'[A-Z]', '', change))
        pct_change = float(re.sub(r'[A-Z]', '', pct_change.replace("%", "")))

        # assign to relevant columns
        df.loc[row.Index, "Last Price ($)"] = price
        df.loc[row.Index, "Day's Change ($)"] = change
        df.loc[row.Index, "Day's Change (%)"] = pct_change

    # derived values needed before adding totals row
    df["Market Value ($)"] = df["Shares"] * df["Last Price ($)"]
    df["Day's Gain/Loss ($)"] = df["Shares"] * df["Day's Change ($)"]

    # sort by largest position (b/c I like it that way)
    df.sort_values("Market Value ($)", inplace=True, ascending=False)

    # create and append totals row
    totals_df = pd.DataFrame({
        "Name": "Totals",
        "Symbol": "",
        "Shares": "",
        "Cost Basis ($)": df["Cost Basis ($)"].sum(),
        "Last Price ($)": "",
        "Day's Change ($)": df["Day's Change ($)"].sum(),
        "Day's Change (%)": (100. * df["Day's Gain/Loss ($)"].sum() / df["Market Value ($)"].sum()),
        "Market Value ($)": df["Market Value ($)"].sum(),
        "Day's Gain/Loss ($)": df["Day's Gain/Loss ($)"].sum(),
        "Account": ""
    }, index=[0])

    df = df.append(totals_df, ignore_index=True)

    # derived values needed after adding totals row
    df["Total Gain/Loss ($)"] = df["Market Value ($)"] - df["Cost Basis ($)"]
    df["Overall Return (%)"] = (100. * df["Total Gain/Loss ($)"] / df["Cost Basis ($)"]).round(2)

    # rounding
    df["Day's Change ($)"] = df["Day's Change ($)"].round(2)
    df["Day's Change (%)"] = df["Day's Change (%)"].round(2)
    df["Market Value ($)"] = df["Market Value ($)"].round(2)
    df["Total Gain/Loss ($)"] = df["Total Gain/Loss ($)"].round(2)
    df["Day's Gain/Loss ($)"] = df["Day's Gain/Loss ($)"].round(2)

    # final column ordering
    cols = ["Name", "Symbol", "Shares", "Market Value ($)", "Last Price ($)", "Day's Change ($)", "Day's Change (%)",
            "Day's Gain/Loss ($)", "Cost Basis ($)", "Total Gain/Loss ($)", "Overall Return (%)", "Account"]

    return df[cols]
