import requests
import pandas as pd


def get_realtime_ticker_data(positions, cols):
    """Gets key metrics from IEX API for a list of Position objects"""

    df = pd.DataFrame(columns=cols)

    # iterate through each position to populate with realtime price data
    for i, position in enumerate(positions):

        ticker = position.symbol

        # make request
        response = requests.get("https://api.iextrading.com/1.0//stock/{}/quote".format(ticker))

        data = response.json()

        # parse price data
        price = data['latestPrice']
        change = data['change']
        pct_change = 100. * data['changePercent']

        # assign to relevant columns
        df.loc[i, "Name"] = position.name
        df.loc[i, "Symbol"] = ticker
        df.loc[i, "Shares"] = position.shares
        df.loc[i, "Cost Basis ($)"] = position.cost_basis
        df.loc[i, "Last Price ($)"] = price
        df.loc[i, "Day's Change ($)"] = change
        df.loc[i, "Day's Change (%)"] = pct_change
        df.loc[i, "Account"] = position.account.name

    return df


def get_totals(df):
    """Creates a totals row as a dataframe"""

    totals_df = pd.DataFrame({
        "Name": "Totals",
        "Cost Basis ($)": df["Cost Basis ($)"].sum(),
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
    df["Cost Basis ($)"] = df["Cost Basis ($)"].astype(float).round(2)

    # sort by largest position and fill null values with empty string (b/c I like it that way)
    df.sort_values("Market Value ($)", inplace=True, ascending=False)
    df.fillna("", inplace=True)

    return df


def get_position_summary(positions):
    """Builds and formats summary of positions for given Position object input"""

    # columns to return
    cols = ["Name", "Symbol", "Shares", "Market Value ($)", "Last Price ($)", "Day's Change ($)", "Day's Change (%)",
            "Day's Gain/Loss ($)", "Cost Basis ($)", "Total Gain/Loss ($)", "Overall Return (%)", "Account"]

    df = get_realtime_ticker_data(positions, cols)

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
