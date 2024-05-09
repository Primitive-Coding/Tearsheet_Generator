import pandas as pd
import numpy as np


class Preprocess:
    def __init__(self) -> None:
        pass

    def create_growth_pairs(self, df: pd.DataFrame):
        """
        Creates a pair of rows for different labels.
        Such as "Revenue" as the base, and "Revenue Growth (YoY)" in the row labels."""
        index = 0
        rows = df.index.to_list()
        pairs = []

        for r in rows:
            if "Growth" in r or "Change" == r.split(" ")[-1]:
                pairs.append({"base": rows[index - 1], "growth": r})
            index += 1

        return pairs

    def fix_dataframe(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        Summary
        ----------
        Foramts the dataframe to be used in further calculations.
        Parameters
        ----------
        df : pd.DataFrame
            Dataframe to be formatted.
        freq : str
            Frequency of the data. Dataframes at different frequencies have different formats which is why this distinction is necessary.

        Returns
        -------
        pd.DataFrame
            Returns the dataframe after formatting has been applied.
        """

        # Remove "-" values from dataframe.
        df = df.replace("-", 0)  # Replace blank cells with 0.
        df = df.replace("Upgrade", np.nan)
        df = self.fix_website_additions(
            df, freq=freq
        )  # Fix premium columns from website.
        df = self.fix_growth(df)  # Fix growth calculations.
        df = self.fix_margin_yield_rates(df)  # Fix margin, yield, and rate %.
        df = df.replace(
            ",", "", regex=True
        )  # Formats values so 53,069 = 53069. This is done so it can be converted to a int or float for further calculations.

        return df

    def fix_growth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Summary
        ----------
        Formats the percentages for the growth arguements
        ----------
        df : pd.DataFrame
            Dataframe to format.
        statement : str
            Financial statement being formatted. Since each dataframe has unique rows the statement
            must be passed to identify which rows to format.

        Returns
        -------
        pd.DataFrame
            Dataframe with formatted rows.
        """
        pairs = self.create_growth_pairs(df)
        if len(pairs) > 0:
            for p in pairs:
                try:
                    base = df.loc[p["base"]].str.replace(",", "").astype(float)
                    index = 0
                    growth_values = []
                    items = base.values.tolist()
                    for i in items:
                        if index == 0:
                            growth_values.append(np.nan)
                        else:
                            try:
                                calc = (i - items[index - 1]) / abs(items[index - 1])
                                growth_values.append(calc)
                            except ZeroDivisionError:
                                growth_values.append(0)
                        index += 1
                    df.loc[p["growth"]] = growth_values
                except AttributeError:
                    pass
            return df
        else:
            # Return dataframe passed in parameter since nothing has been formatted.
            return df

    def fix_margin_yield_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Summary
        ----------
        Converts margins, yields, and tax rates from a string percentage to a float.
        Ex:
        Before: Margin = 98%
        After: Margin = 0.98

        Parameters
        ----------
        df : pd.DataFrame
           Dataframe to format.

        Returns
        -------
        pd.DataFrame
            Dataframe with formatting applied.
        """
        # Get the row indexes of the dataframe.
        rows = df.index.to_list()
        # Other cases that can not be effectively caught with algo.
        edge_cases = [
            "Effective Tax Rate",
            "Payout Ratio",
            "Return on Equity (ROE)",
            "Return on Assets (ROA)",
            "Return on Capital (ROIC)",
        ]
        general_cases = ["Dilution", "Margin", "Return", "Yield"]
        for r in rows:
            last_word = r.split(" ")[-1]
            first_word = r.split(" ")[0]
            if last_word in general_cases or r in edge_cases:
                try:
                    df.loc[r] = df.loc[r].str.replace("%", "").astype(float) / 100
                except AttributeError:
                    pass
        return df

    def fix_website_additions(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        Summary
        ----------
        When scraped, the website "stockanalysis.com" will have extra columns that we are not interested in.
        Mainly columns that are reserved for premium members, which are left blank if user is only standard.
        This function will clear these extra columns for both quarterly and annual data.

        Parameters
        ----------
        df : pd.DataFrame
           Dataframe to format.

        Returns
        -------
        pd.DataFrame
            Dataframe with formatting applied.
        """

        # Logic to delete columns in quarterly dataframes.
        if freq == "Q":
            cols = df.columns
            col_to_delete = None
            drop = False
            for c in cols:
                if "+" in c:
                    col_to_delete = c
                    drop = True
            if drop:
                df.drop(col_to_delete, axis=1, inplace=True)
            return df

        # Logic to delete columns in annual dataframes.
        elif freq == "A":
            cols = df.columns
            col_to_delete = None
            drop = False
            for c in cols:
                if "-" in c:
                    col_to_delete = c
                    drop = True
            if drop:
                df.drop(col_to_delete, axis=1, inplace=True)
            return df
