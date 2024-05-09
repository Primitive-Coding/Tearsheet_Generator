# Scraper for Stockanalysis.com
import os
import time

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time

# Number storage & manipulation
import pandas as pd
import numpy as np
from Processing.preprocess_data import Preprocess

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-popup-blocking")
# chrome_options.add_argument("--headless") NOTE: Running in headless will result in empty dataframes.
chrome_options.add_argument("--disable-gpu")


annual_params = ["A", "a", "Annual", "annual"]
quarterly_params = ["Q", "q", "Quarterly", "quarterly", "Quarter", "quarter"]


"""
WARNING!!!
Xpaths must be kept in this list order. 
---
Program logic assumes the "div[5]" xpath is in index 0, 
and "div[4]" xpath is in index 1. 
"""
xpaths = {
    "col": [
        "/html/body/div/div[1]/div[2]/main/div[5]/table/thead/tr/th[{}]",
        "/html/body/div/div[1]/div[2]/main/div[4]/table/thead/tr/th[{}]",
    ],
    "row": [
        "/html/body/div/div[1]/div[2]/main/div[5]/table/tbody/tr[{}]/td[1]",
        "/html/body/div/div[1]/div[2]/main/div[4]/table/tbody/tr[{}]/td[1]",
    ],
    "header": [
        "/html/body/div/div[1]/div[2]/main/div[5]/table/thead/tr/th[{}]",
        "/html/body/div/div[1]/div[2]/main/div[4]/table/thead/tr/th[{}]",
    ],
    "full": [
        "/html/body/div/div[1]/div[2]/main/div[5]/table/tbody/tr[{}]/td[{}]",
        "/html/body/div/div[1]/div[2]/main/div[4]/table/tbody/tr[{}]/td[{}]",
    ],
    "qtr_button": "/html/body/div/div[1]/div[2]/main/div[2]/nav[2]/ul/li[2]/button",
}

urls = {
    "income_statement": {
        "A": "https://stockanalysis.com/stocks/{}/financials/",
        "Q": "https://stockanalysis.com/stocks/{}/financials/?p=quarterly",
    },
    "balance_sheet": {
        "A": "https://stockanalysis.com/stocks/{}/financials/balance-sheet/",
        "Q": "https://stockanalysis.com/stocks/{}/financials/balance-sheet/?p=quarterly",
    },
    "cash_flow": {
        "A": "https://stockanalysis.com/stocks/{}/financials/cash-flow-statement/",
        "Q": "https://stockanalysis.com/stocks/{}/financials/cash-flow-statement/?p=quarterly",
    },
    "ratios": {
        "A": "https://stockanalysis.com/stocks/{}/financials/ratios/",
        "Q": "https://stockanalysis.com/stocks/{}/financials/ratios/?p=quarterly",
    },
}


class StockAnalysis:
    def __init__(
        self,
        ticker: str,
        driver_path: str = "D:\\Chromedriver\\chromedriver.exe",
        dataset_path: str = "D:\\STOCK_ANALYSIS_DATASET",
        freq: str = "A",
        halt_scrape: bool = False,
        wait_time: int = 5,
        log_data: bool = False,
    ) -> None:
        self.halt_scrape = (
            halt_scrape  # Determine if scraping is stopped if element is not found.
        )

        self.ticker = ticker.upper()
        self.dataset_path = dataset_path
        self.stock_data_path = f"{self.dataset_path}\\{self.ticker}"
        self.wait_time = wait_time
        self.log_data = log_data
        # Create local files for ticker.
        self.create_local_files()

        if freq in annual_params:
            self.folder = "Annual"
            self.freq = "A"
        elif freq in quarterly_params:
            self.folder = "Quarter"
            self.freq = "Q"

        self.chrome_driver = driver_path
        # Variables for financial statements.
        self.income_statement = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cash_flow = pd.DataFrame()
        self.ratios = pd.DataFrame()

        self.preprocess = Preprocess()

        self.quarter_params = ["Quarter", "quarter", "Quarterly", "quarterly", "Q", "q"]
        self.annual_params = ["Annual", "annual", "A", "a"]

    ################################################################### Browser Creation
    def create_browser(self, url=None):
        """
        :param url: The website to visit.
        :return: None
        """
        service = Service(executable_path=self.chrome_driver)
        self.browser = webdriver.Chrome(service=service, options=chrome_options)
        # Default browser route
        if url == None:
            self.browser.get(url=self.sec_quarterly_url)
        # External browser route
        else:
            self.browser.get(url=url)

    """
    Income Statement
    """

    def scrape_income_statement(self):
        self.create_browser(urls["income_statement"][self.freq].format(self.ticker))
        if self.freq == "Q":
            self.click_button(xpaths["qtr_button"], wait=True, wait_time=5)
        df = self.get_table_data()
        df = self.preprocess.fix_dataframe(df, freq=self.freq)
        self.browser.close()
        self.browser.quit()
        return df

    def set_income_statement(self) -> None:
        statement = "income_statement.csv"
        path = f"{self.dataset_path}\\{self.ticker}\\{self.folder}\\{self.ticker}_{statement}"
        try:
            df = pd.read_csv(path)
            df.rename(columns={"Unnamed: 0": "index"}, inplace=True)
            df.set_index("index", inplace=True)
        except FileNotFoundError:
            df = self.scrape_income_statement()
            df.to_csv(path)
        self.income_statement = df

    def get_income_statement(self) -> pd.DataFrame:
        if self.income_statement.empty:
            self.set_income_statement()
        return self.income_statement

    """
    Balance Sheet
    """

    def scrape_balance_sheet(self) -> pd.DataFrame:
        self.create_browser(urls["balance_sheet"][self.freq].format(self.ticker))
        if self.freq == "Q":
            self.click_button(xpaths["qtr_button"], wait=True, wait_time=5)
        df = self.get_table_data()
        df = self.preprocess.fix_dataframe(df, freq=self.freq)
        self.browser.close()
        self.browser.quit()
        return df

    def set_balance_sheet(self) -> None:
        statement = "balance_sheet.csv"
        path = f"{self.dataset_path}\\{self.ticker}\\{self.folder}\\{self.ticker}_{statement}"
        try:
            df = pd.read_csv(path)
            df.rename(columns={"Unnamed: 0": "index"}, inplace=True)
            df.set_index("index", inplace=True)
        except FileNotFoundError:
            df = self.scrape_balance_sheet()
            df.to_csv(path)
        self.balance_sheet = df

    def get_balance_sheet(self) -> pd.DataFrame:
        if self.balance_sheet.empty:
            self.set_balance_sheet()
        return self.balance_sheet

    """
    Cash Flow
    """

    def scrape_cash_flow(self) -> pd.DataFrame:
        self.create_browser(urls["cash_flow"][self.freq].format(self.ticker))
        if self.freq == "Q":
            self.click_button(xpaths["qtr_button"], wait=True, wait_time=5)
        df = self.get_table_data()
        df = self.preprocess.fix_dataframe(df, freq=self.freq)
        self.browser.close()
        self.browser.quit()
        return df

    def set_cash_flow(self) -> None:
        statement = "cash_flow.csv"
        path = f"{self.dataset_path}\\{self.ticker}\\{self.folder}\\{self.ticker}_{statement}"
        try:
            df = pd.read_csv(path)
            df.rename(columns={"Unnamed: 0": "index"}, inplace=True)
            df.set_index("index", inplace=True)
        except FileNotFoundError:
            df = self.scrape_cash_flow()
            df.to_csv(path)
        self.cash_flow = df

    def get_cash_flow(self) -> pd.DataFrame:
        if self.cash_flow.empty:
            self.set_cash_flow()
        return self.cash_flow

    """
    Ratios
    """

    def scrape_ratios(self) -> pd.DataFrame:
        self.create_browser(urls["ratios"][self.freq].format(self.ticker))
        if self.freq == "Q":
            self.click_button(xpaths["qtr_button"], wait=True, wait_time=5)
        df = self.get_table_data()
        df = self.preprocess.fix_dataframe(df, freq=self.freq)
        self.browser.close()
        self.browser.quit()
        return df

    def set_ratios(self) -> None:
        statement = "ratios.csv"
        path = f"{self.dataset_path}\\{self.ticker}\\{self.folder}\\{self.ticker}_{statement}"
        try:
            df = pd.read_csv(path)
            df.rename(columns={"Unnamed: 0": "index"}, inplace=True)
            df.set_index("index", inplace=True)
        except FileNotFoundError:
            df = self.scrape_ratios()
            df.to_csv(path)
        self.ratios = df

    def get_ratios(self) -> pd.DataFrame:
        if self.ratios.empty:
            self.set_ratios()
        return self.ratios

    """
    All Statements
    """

    def scrape_and_write_all(self) -> None:
        """
        Set each financials statement. Each set() function will write the data locally to avoid scraping next time.
        """
        self.set_income_statement()
        self.set_balance_sheet()
        self.set_cash_flow()
        self.set_ratios()

    """
    Table Utilities
    """

    def get_table_data(self):
        time.sleep(self.wait_time)
        dimensions = self.get_table_dimensions()
        working_index = dimensions["working_index"]
        row_count = dimensions["row"]
        col_count = dimensions["col"]
        base_xpath = xpaths["full"][working_index]
        header_xpath = xpaths["header"][working_index]
        row_labels = []
        table_data = {}
        for x in range(row_count):

            row_data = []
            for y in range(col_count):
                # Add 1 to adjust for xpath labels.
                xpath = base_xpath.format(x + 1, y + 1)
                try:
                    data = self.read_data(xpath, wait=True, wait_time=self.wait_time)
                    if self.log_data:
                        print(f"Data: {data}")
                except TimeoutException:
                    data = np.nan
                if y == 0:
                    row_labels.append(data)
                else:
                    row_data.append(data)
            table_data[row_labels[x]] = row_data
        table_headers = []
        # Collect table headers
        for i in range(col_count):
            xpath = header_xpath.format(i + 1)
            header_data = self.read_data(xpath, wait=True, wait_time=self.wait_time)
            if header_data == "Year" or header_data == "Quarter Ended":
                pass
            else:
                table_headers.append(header_data)
        table_data["Dates"] = table_headers
        df = pd.DataFrame(table_data)
        df.set_index("Dates", inplace=True)
        df = df.T
        df = df.iloc[:, ::-1]
        return df

    def get_table_dimensions(self):
        # Collect number of columns.
        col_count = self.count_columns(xpaths["header"][0])
        if col_count == 0:
            row_index = 1
            col_count = self.count_columns(xpaths["header"][1])
        else:
            # Since there are less columns than rows, the process can be sped up by seeing which xpaths work with the columns,
            # to use on the rows.
            row_index = 0
        # Collect number of rows.
        row_count = self.count_rows(
            xpaths["row"][row_index], xpaths["header"][row_index]
        )

        return {"row": row_count, "col": col_count, "working_index": row_index}

    def count_rows(self, base_xpath: str, header_path: str):
        row_running = True
        row_index = 1
        row_count = 0
        while row_running:

            if row_index == 1:
                x = header_path.format(1)
            else:
                x = header_path.format(1)
            try:
                row_data = self.read_data(
                    base_xpath.format(row_index), wait=True, wait_time=self.wait_time
                )
                row_count += 1
                row_index += 1
            except NoSuchElementException:
                row_running = False
            except TimeoutException:
                row_running = False
        if row_count == 0:
            print(f"[Warning] 0 rows collected")
        return row_count

    def count_columns(self, base_xpath: str):
        """
        Since the top of the table is the headers section, it is recommended to pass the headers xpath
        as the base_xpath.
        """
        col_running = True
        col_index = 1
        col_count = 0
        while col_running:
            try:
                col_data = self.read_data(
                    base_xpath.format(col_index), wait=True, wait_time=self.wait_time
                )
                col_count += 1
                col_index += 1
            except NoSuchElementException:
                col_running = False
            except TimeoutException:
                col_running = False
        if col_count == 0:
            print(f"[Warning] 0 columns collected")
        return col_count

    """-----------------------------------"""

    """-----------------------------------"""

    def read_data(self, xpath: str, wait: bool = False, wait_time: int = 5) -> str:
        """
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.
        :return: (str) Text of the element.
        """

        if wait:
            data = WebDriverWait(self.browser, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        else:
            data = self.browser.find_element("xpath", xpath)
        # Return the text of the element found.
        return data.text

    def read_html(self, css_class: str, wait_time: int = 5):
        data = WebDriverWait(self.browser, wait_time).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, css_class))
        )
        return data

    """-------------------------------"""

    def click_button(self, xpath: str, wait: bool = False, wait_time: int = 5) -> None:
        """
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.
        :return: None. Because this function clicks the button but does not return any information about the button or any related web elements.
        """

        if wait:
            element = WebDriverWait(self.browser, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        else:
            element = self.browser.find_element("xpath", xpath)
        element.click()

    """-------------------------------"""

    def halt_scrape(self, func: str):
        print(f"-- [Halted] -- Process stopped within function: {func}.")

    def create_local_files(self) -> None:
        # Create directory for ticker.
        os.makedirs(f"{self.dataset_path}\\{self.ticker}", exist_ok=True)
        os.makedirs(f"{self.dataset_path}\\{self.ticker}\\Annual", exist_ok=True)
        os.makedirs(f"{self.dataset_path}\\{self.ticker}\\Quarter", exist_ok=True)

    def clean_dataframe(self, df: pd.DataFrame):
        """
        After a new dataframe is scraped, this function should be called.
        """

    def clean_and_rewrite_dataframe(self):
        """
        This function is used for pre-existing dataframes that may have formatting issues.
        """
        annual_path = f"{self.stock_data_path}\\Annual"
        quarter_path = f"{self.stock_data_path}\\Quarter"

        statements = [
            "income_statement.csv",
            "balance_sheet.csv",
            "cash_flow.csv",
            "ratios.csv",
        ]

        for s in statements:
            path = f"{annual_path}\\{self.ticker}_{s}"
            print(f"Path: {path}")
            a = (
                pd.read_csv(path)
                .rename(columns={"Unnamed: 0": "index"})
                .set_index("index")
            )
            print(f"A: {a}")

            cols = a.columns
            col_to_delete = None
            drop = False
            for c in cols:
                if "-" in c:
                    col_to_delete = c
                    drop = True
            if drop:
                a.drop(col_to_delete, axis=1, inplace=True)
                a.to_csv(path)

        for s in statements:
            path = f"{quarter_path}\\{self.ticker}_{s}"
            q = (
                pd.read_csv(path)
                .rename(columns={"Unnamed: 0": "index"})
                .set_index("index")
            )

            cols = q.columns
            col_to_delete = None
            drop = False
            for c in cols:
                if "+" in c:
                    col_to_delete = c
                    drop = True
            if drop:
                q.drop(col_to_delete, axis=1, inplace=True)
                q.to_csv(path)
