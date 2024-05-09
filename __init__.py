import os
import shutil
import time
import pandas as pd
from Tearsheet.tearsheet import Tearsheet
from Scraper.stock_analysis import StockAnalysis
from AssetCompare.asset_compare import AssetCompare
from Tearsheet.forecast_model import ForecastModel


driver_path = "D:\\Chromedriver\\chromedriver.exe"


def write_list_to_str(l: list) -> str:
    index = 1
    new_str = ""
    for i in l:
        new_str += f"{index}. {i}\n"
        index += 1
    return new_str


def type_menu(l):

    print(f"\n\n[Choose Type] \n{write_list_to_str(l)}")


def option_menu(l):
    print(f"\n\n[Choose Option] \n{write_list_to_str(l)}")


if __name__ == "__main__":

    i = 0
    ticker = "RKLB"
    tickers = ["MSFT", "AAPL", "NVDA", "GOOGL", "META", "TSLA"]
    if i == 0:
        t = Tearsheet(ticker)
        t.create_tearsheet()
    elif i == 1:
        a = AssetCompare(tickers)
        f = a.compare("yields", "earnings")
        running = True
        while running:
            # Type Menu
            compare_types = a.get_compare_types()
            type_menu(compare_types)
            type_input = int(input("Choose a compare type: ")) - 1
            type_label = compare_types[type_input]

            # Option Menu
            options = a.get_compare_options(compare_type=type_label)
            option_menu(options)
            option_input = int(input("Choose a option: ")) - 1
            option_label = options[option_input]
            print(f"Type: {type_label}\nOption: {option_label}")
            df = a.compare(compare_type=type_label, inner_type=option_label)
            print(df)
    elif i == 2:
        t = Tearsheet(ticker, freq="A")
        inc = t.stock_analysis_scraper.get_income_statement()
        ratio = t.stock_analysis_scraper.get_ratios().drop("Current", axis=1)
        revenue = inc.loc["Revenue"]
        ps_ratio = ratio.loc["PS Ratio"]
        print(f"PS: {ps_ratio}")
        t.forecast_model.create_forecast(ps_ratio)
    elif i == 3:
        f = ForecastModel("MSFT", "A", "2020", predict_ratio=True, predict_shares=True)
        f.set_all_statements()
        f.get_revenue_valuation(review_period=10)
