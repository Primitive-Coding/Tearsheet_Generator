import warnings

warnings.simplefilter("ignore")

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from prophet import Prophet
import matplotlib.pyplot as plt
from prophet.plot import plot_plotly
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from Scraper.stock_analysis import StockAnalysis

annual_params = ["A", "a", "Annual", "annual"]
quarterly_params = ["Q", "q", "Quarterly", "quarterly", "Quarter", "quarter"]


class ForecastModel:
    def __init__(
        self,
        ticker: str,
        freq: str,
        custom_cutoff: str = "",
        review_period: int = 5,
        forecast_period: int = 3,
        predict_ratio: bool = False,
        predict_shares: bool = False,
    ) -> None:
        self.ticker = ticker.upper()
        self.freq = freq
        if self.freq in quarterly_params:
            self.freq = "Q"
            self.folder = "Quarter"
        elif self.freq in annual_params:
            self.freq = "A"
            self.folder = "Annual"
        if custom_cutoff == "":
            self.cutoff = False
            self.custom_cutoff = custom_cutoff
        elif custom_cutoff != "":
            self.cutoff = True
            self.custom_cutoff = custom_cutoff

        self.review_period = review_period  # Number of years to use for calculations.
        self.forecast_period = (
            forecast_period  # Number of years to use for forecasting.
        )
        self.predict_ratio = predict_ratio
        self.predict_shares = predict_shares

        # Financial Statements
        self.income_statement = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cash_flow = pd.DataFrame()
        self.ratios = pd.DataFrame()

        self.linear = LinearRegression()

        self.path = f"D:\\STOCK_ANALYSIS_DATASET\\{self.ticker}\\{self.folder}\\"

        self.stock_analysis = StockAnalysis(self.ticker, freq=self.freq)

    def set_all_statements(self) -> None:

        self.income_statement = self.stock_analysis.get_income_statement()
        self.balance_sheet = self.stock_analysis.get_balance_sheet()
        self.cash_flow = self.stock_analysis.get_cash_flow()
        self.ratios = self.stock_analysis.get_ratios().drop("Current", axis=1)
        if self.cutoff:
            self.income_statement = self.income_statement.loc[:, : self.custom_cutoff]
            self.balance_sheet = self.balance_sheet.loc[:, : self.custom_cutoff]
            self.cash_flow = self.cash_flow.loc[:, : self.custom_cutoff]
            self.ratios = self.ratios.loc[:, : self.custom_cutoff]

    def create_forecast(
        self,
        base_data,
        plot: bool = False,
    ):

        if self.freq == "A":
            steps = 3
        elif self.freq == "Q":
            steps = 4

        p = 1  # No differencing needed for stationary.
        d = 1  # Data appears stationary.
        q = 1  # Seasonal component with period 1.

        base_data.index = pd.to_datetime(base_data.index)
        df = pd.DataFrame(base_data)
        col = df.columns.to_list()[0]

        # Fit the ARIMA model.
        model = ARIMA(df[col], order=(p, d, q))
        fit_model = model.fit()

        forecast = fit_model.forecast(steps=steps)

        # Check for stationarity using Augmented Dickey-Fuller test

        if plot:
            adf_result = adfuller(df[col])
            lags = 15
            # Plot ACF and PACF of the differenced series
            plt.figure(figsize=(12, 6))
            plt.subplot(211)
            plot_acf(df[col].diff().dropna(), ax=plt.gca(), lags=lags)
            plt.subplot(212)
            plot_pacf(df[col].diff().dropna(), ax=plt.gca(), lags=lags)
            plt.show()

        return forecast

    def create_forecast2(self, base_data):
        # Define ARIMA model parameters (p, d, q)
        p = 1  # Autoregressive (AR) order
        d = 0  # Differencing order
        q = 1  # Moving Average (MA) order
        n = self.review_period  # Forecast next 'n' steps.

        model = ARIMA(base_data, order=(p, d, q))
        result = model.fit()
        forecast = result.forecast(steps=n)
        print(f"ForecastARIMA: {forecast}")
        return forecast

    def create_forecast3(self, base_data):
        label = "Data"
        print(f"Base Data: {base_data}")
        data = {
            "Year": base_data.index.to_list(),  # List
            f"{label}": base_data,  # Pd.series
        }
        forecast = pd.DataFrame(data).dropna()
        growth = forecast[label].pct_change() * 100
        growth.index = growth.index.astype(int)  # Convert index from 'str' to 'int'
        # Get the number of years in the dataframe.
        years = forecast["Year"].astype(int).to_list()
        # Create list of years to forecast.
        future_years = []
        base_year = years[-1]
        for i in range(self.forecast_period):
            if i == 0:
                cur_year = base_year + 1
                future_years.append(cur_year)
            else:
                cur_year += 1
                future_years.append(cur_year)

        # Reshape for model
        X = forecast["Year"].values.reshape(-1, 1)
        X = np.concatenate((X, np.ones((X.shape[0], 1))), axis=1)  # Add intercept
        y = forecast[label].values
        # Fit the model.
        self.linear.fit(X, y)
        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        print(f"Future X: {future_X}")
        # Replace infinities with NaN
        future_X[np.isinf(future_X)] = np.nan
        future_X = future_X.astype(np.float64)
        forecast_data = self.linear.predict(future_X)
        # Get the most recent equity.
        mr_data = forecast[label].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = growth.loc[years].mean()
        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_data * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth

        try:
            forecast_data_with_features = self.linear.predict(future_X)
        except ValueError:
            forecast_data_with_features = np.array([np.nan] * len(forecast_data))

        data = {
            "Year": future_years,
            f"forecast": forecast_data.tolist(),
            f"forecast_with_features": forecast_data_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)
        return data

    def create_valuation(self, data_forecast, ratio_data, share_data):
        years = self.ratios.columns.to_list()
        base_year = int(years[-2]) + 1
        forecast_years = []
        i = 1
        # Use the range of "rev_forecast" to determine how many years have been forecasted.
        for i in range(len(data_forecast)):
            forecast_years.append(int(base_year) + i)
            i += 1

        # Fit data into DataFrame
        if self.predict_ratio and self.predict_shares:
            data = {
                "forecast_years": [],
                "forecast_ratio": ratio_data["forecast"].to_list(),
                "forecast": data_forecast["forecast"].to_list(),
                "shares_basic": share_data["forecast"].to_list(),
            }
        elif self.predict_ratio:
            data = {
                "forecast_years": [],
                "forecast_ratio": ratio_data["forecast"].to_list(),
                "forecast": data_forecast["forecast"].to_list(),
                "shares_basic": share_data,
            }
        elif self.predict_shares:
            data = {
                "forecast_years": [],
                "forecast_ratio": ratio_data,
                "forecast": data_forecast["forecast"].to_list(),
                "shares_basic": share_data["forecast"].to_list(),
            }
        else:
            data = {
                "forecast_years": [],
                "forecast_ratio": ratio_data,
                "forecast": data_forecast["forecast"].to_list(),
                "shares_basic": share_data,
            }
        index = 0
        for i in forecast_years:
            data["forecast_years"].append(i)
            index += 1
        data = pd.DataFrame(data, index=data["forecast_years"]).drop(
            "forecast_years", axis=1
        )
        # Calculate marketcap and share price projections.
        data["projected_marketcap"] = data["forecast_ratio"] * data["forecast"]
        data["projected_share_price"] = (
            data["projected_marketcap"] / data["shares_basic"]
        )

        data["projected_returns"] = data["projected_share_price"].pct_change() * 100
        data["projected_returns"] = data["projected_returns"].fillna(0)
        return data

    def get_income_statement_valuation_item(
        self, statement_label: str, ratio_label, review_period: str
    ):
        if str(review_period).lower() == "max":
            data = self.income_statement.loc[statement_label]
            ratio = self.ratios.loc[ratio_label]
            shares = self.income_statement.loc["Shares Outstanding (Basic)"]
        else:
            review_period = int(review_period)
            data = self.income_statement.loc[statement_label].iloc[-review_period:]
            ratio = self.ratios.loc[ratio_label].iloc[-review_period:]
            shares = self.income_statement.loc["Shares Outstanding (Basic)"].iloc[
                -review_period:
            ]
        # Create forecast for base data.
        data_forecast = self.create_forecast3(data)

        # Create a forecast for a ratio.
        if self.predict_ratio:
            ratio_forecast = self.create_forecast3(ratio)
        else:
            ratio_forecast = ratio.mean()

        # Create a forecast for shares.
        if self.predict_shares:
            shares_forecast = self.create_forecast3(shares)
        else:
            shares_forecast = shares.mean()

        val = self.create_valuation(
            data_forecast=data_forecast,
            ratio_data=ratio_forecast,
            share_data=shares_forecast,
        )

        return val

    def get_balance_sheet_valuation_item(
        self, statement_label: str, ratio_label, review_period: str
    ):
        if str(review_period).lower() == "max":
            data = self.balance_sheet.loc[statement_label]
            ratio = self.ratios.loc[ratio_label]
            shares = self.income_statement.loc["Shares Outstanding (Basic)"]
        else:
            review_period = int(review_period)
            data = self.balance_sheet.loc[statement_label].iloc[-review_period:]
            ratio = self.ratios.loc[ratio_label].iloc[-review_period:]
            shares = self.income_statement.loc["Shares Outstanding (Basic)"].iloc[
                -review_period:
            ]
        # Create forecast for base data.
        data_forecast = self.create_forecast3(data)

        # Create a forecast for a ratio.
        if self.predict_ratio:
            ratio_forecast = self.create_forecast3(ratio)
        else:
            ratio_forecast = ratio.mean()

        # Create a forecast for shares.
        if self.predict_shares:
            shares_forecast = self.create_forecast3(shares)
        else:
            shares_forecast = shares.mean()

        val = self.create_valuation(
            data_forecast=data_forecast,
            ratio_data=ratio_forecast,
            share_data=shares_forecast,
        )

        return val

    def get_cash_flow_valuation_item(
        self, statement_label: str, ratio_label, review_period: str
    ):
        if str(review_period).lower() == "max":
            data = self.cash_flow.loc[statement_label]
            ratio = self.ratios.loc[ratio_label]
            shares = self.income_statement.loc["Shares Outstanding (Basic)"]
        else:
            review_period = int(review_period)
            data = self.cash_flow.loc[statement_label].iloc[-review_period:]
            ratio = self.ratios.loc[ratio_label].iloc[-review_period:]
            shares = self.income_statement.loc["Shares Outstanding (Basic)"].iloc[
                -review_period:
            ]
        # Create forecast for base data.
        data_forecast = self.create_forecast3(data)

        # Create a forecast for a ratio.
        if self.predict_ratio:
            ratio_forecast = self.create_forecast3(ratio)
        else:
            ratio_forecast = ratio.mean()

        # Create a forecast for shares.
        if self.predict_shares:
            shares_forecast = self.create_forecast3(shares)
        else:
            shares_forecast = shares.mean()

        val = self.create_valuation(
            data_forecast=data_forecast,
            ratio_data=ratio_forecast,
            share_data=shares_forecast,
        )

        return val

    """
    Valuations
    """

    def get_revenue_valuation(
        self,
        review_period: str = "max",
    ):
        statement_label = "Revenue"
        ratio_label = "PS Ratio"

        val = self.get_income_statement_valuation_item(
            statement_label=statement_label,
            ratio_label=ratio_label,
            review_period=review_period,
        )

        return val

    def get_earnings_valuation(
        self,
        review_period: str = "max",
    ):
        statement_label = "Net Income"
        ratio_label = "PE Ratio"

        val = self.get_income_statement_valuation_item(
            statement_label=statement_label,
            ratio_label=ratio_label,
            review_period=review_period,
        )

        return val

    def get_equity_valuation(
        self,
        review_period: str = "max",
    ):
        statement_label = "Shareholders' Equity"
        ratio_label = "PB Ratio"

        val = self.get_balance_sheet_valuation_item(
            statement_label=statement_label,
            ratio_label=ratio_label,
            review_period=review_period,
        )

        return val

    def get_fcf_valuation(
        self,
        review_period: str = "max",
    ):
        statement_label = "Free Cash Flow"
        ratio_label = "P/FCF Ratio"

        val = self.get_cash_flow_valuation_item(
            statement_label=statement_label,
            ratio_label=ratio_label,
            review_period=review_period,
        )

        return val
