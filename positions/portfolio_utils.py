import re
import pandas as pd
from yahoo_finance import Share


def get_totals(df):
    """Creates a totals row as a dataframe"""

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

    return totals_df


def format_positions_summary(df):
    """Formats report for final display"""

    # rounding
    df["Day's Change ($)"] = df["Day's Change ($)"].astype(float).round(2)
    df["Day's Change (%)"] = df["Day's Change (%)"].astype(float).round(2)
    df["Market Value ($)"] = df["Market Value ($)"].astype(float).round(2)
    df["Day's Gain/Loss ($)"] = df["Day's Gain/Loss ($)"].astype(float).round(2)

    # sort by largest position (b/c I like it that way)
    df.sort_values("Market Value ($)", inplace=True, ascending=False)

    return df


def get_position_summary(positions):
    """Gets key metrics from Yahoo! Finance API for a list of Position objects"""

    # columns to return
    cols = ["Name", "Symbol", "Shares", "Market Value ($)", "Last Price ($)", "Day's Change ($)", "Day's Change (%)",
            "Day's Gain/Loss ($)", "Cost Basis ($)", "Total Gain/Loss ($)", "Overall Return (%)", "Account"]

    df = pd.DataFrame(columns=cols)

    # iterate through each position to populate with realtime (er, 15-minute delayed) data
    for i, position in enumerate(positions):

        # get ticker data from Y! Finance API
        ticker = position.symbol
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
        df.loc[i, "Name"] = position.name
        df.loc[i, "Symbol"] = ticker
        df.loc[i, "Shares"] = position.shares
        df.loc[i, "Cost Basis ($)"] = position.cost_basis
        df.loc[i, "Last Price ($)"] = price
        df.loc[i, "Day's Change ($)"] = change
        df.loc[i, "Day's Change (%)"] = pct_change
        df.loc[i, "Account"] = position.account.name

    # derived values needed before adding totals row
    df["Market Value ($)"] = df["Shares"] * df["Last Price ($)"]
    df["Day's Gain/Loss ($)"] = df["Shares"] * df["Day's Change ($)"]

    # create and append totals row
    totals_df = get_totals(df)
    df = df.append(totals_df, ignore_index=True)

    # derived values needed after adding totals row
    df["Total Gain/Loss ($)"] = (df["Market Value ($)"] - df["Cost Basis ($)"]).astype(float).round(2)
    df["Overall Return (%)"] = (100. * df["Total Gain/Loss ($)"] / df["Cost Basis ($)"]).astype(float).round(2)

    # final formatting
    df = format_positions_summary(df.loc[:, cols])

    return df
