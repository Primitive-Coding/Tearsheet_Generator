import pandas as pd
import numpy as np
from Scraper.stock_analysis import StockAnalysis


class AssetCompare:
    def __init__(self, tickers: list, period: str = "A"):

        self.data = {}
        self.tickers = tickers
        for t in tickers:
            s = StockAnalysis(t.upper(), freq=period)
            self.data[t.upper()] = {
                "scraper": s,
                "income_statement": s.get_income_statement(),
                "balance_sheet": s.get_balance_sheet(),
                "cash_flow": s.get_cash_flow(),
                "ratios": s.get_ratios(),
            }

        self.comparisons = {
            "growth": {
                "eps": {
                    "statement": "income_statement",
                    "statement_label": "EPS Growth",
                },
                "net_income": {
                    "statement": "income_statement",
                    "statement_label": "Net Income Growth",
                },
                "revenue": {
                    "statement": "income_statement",
                    "statement_label": "Revenue Growth (YoY)",
                },
            },
            "ratios": {
                "current": {"statement": "ratios", "statement_label": "Current Ratio"},
                "debt/equity": {
                    "statement": "ratios",
                    "statement_label": "Debt / Equity Ratio",
                },
                "ev/fcf": {"statement": "ratios", "statement_label": "EV/FCF Ratio"},
                "ev/sales": {
                    "statement": "ratios",
                    "statement_label": "EV/Sales Ratio",
                },
                "payout": {"statement": "ratios", "statement_label": "Payout Ratio"},
                "p/b": {"statement": "ratios", "statement_label": "PB Ratio"},
                "p/e": {"statement": "ratios", "statement_label": "PE Ratio"},
                "p/fcf": {"statement": "ratios", "statement_label": "P/FCF Ratio"},
                "p/s": {"statement": "ratios", "statement_label": "PS Ratio"},
                "quick": {"statement": "ratios", "statement_label": "Quick Ratio"},
            },
            "yields": {
                "dividends": {
                    "statement": "ratios",
                    "statement_label": "Dividend Yield",
                },
                "earnings": {
                    "statement": "ratios",
                    "statement_label": "Earnings Yield",
                },
                "fcf": {
                    "statement": "ratios",
                    "statement_label": "FCF Yield",
                },
                "sbb": {
                    "statement": "ratios",
                    "statement_label": "Buyback Yield / Dilution",
                },
            },
        }

    def get_compare_types(self) -> list:
        compare_types = []
        for i in self.comparisons.items():
            compare_types.append(i[0])
        return compare_types

    def get_compare_options(self, compare_type: str) -> list:
        compare_options = []
        for i in self.comparisons[compare_type].items():
            compare_options.append(i[0])
        return compare_options

    def compare(self, compare_type: str = "yields", inner_type: str = "earnings"):
        compare_data = pd.DataFrame()
        comparisons = self.comparisons[compare_type]
        label = comparisons[inner_type]["statement_label"]
        table_type = comparisons[inner_type]["statement"]
        for i in self.data.items():
            ticker, i = i

            if table_type == "income_statement":
                df = i["income_statement"]
            elif table_type == "balance_sheet":
                df = i["balance_sheet"]
            elif table_type == "cash_flow":
                df = i["cash_flow"]
            elif table_type == "ratios":
                df = i["ratios"]
            compare_data[ticker] = self.add_formatting(compare_type, df, label)

        return compare_data

    def add_formatting(self, compare_type: str, df: pd.DataFrame, label: str):
        new_df = None
        try:
            if compare_type == "yields" or compare_type == "growth":
                new_df = (df.loc[label]) * 100
                new_df = self.add_percents(new_df)
                return new_df
            elif compare_type == "ratios":
                new_df = df.loc[label]
                return new_df
        except KeyError:
            df.loc[label] = 0
            return df

    def add_percents(self, data: pd.DataFrame) -> pd.DataFrame:
        add_percent = lambda x: "{:.2f}".format(x) + "%"
        try:
            data = data.apply(add_percent)
        except TypeError:
            pass
        return data
