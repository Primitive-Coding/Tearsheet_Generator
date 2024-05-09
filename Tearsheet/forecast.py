import numpy as np
import pandas as pd


from Tearsheet.calculations import Calculations
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA


class Forecast:
    def __init__(
        self, calc: Calculations, review_period: int = 5, forecast_period: int = 3
    ) -> None:
        self.review_period = review_period
        self.forecast_period = forecast_period

        # Financial Statements
        self.income_statement = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cash_flow = pd.DataFrame()
        self.ratios = pd.DataFrame()
        self.linear = LinearRegression()
        # Library for calculations
        self.calc = calc

    def set_all_statements(
        self,
        income_statement: pd.DataFrame,
        balance_sheet: pd.DataFrame,
        cash_flow: pd.DataFrame,
        ratios: pd.DataFrame,
    ):
        self.income_statement = income_statement
        self.balance_sheet = balance_sheet
        self.cash_flow = cash_flow
        self.ratios = ratios

    def forecast_revenue(self):
        """

        This model uses the last "review_period" years for the reference to revenue growth. (Default is 5)
        It uses this instead of the max years available because companies come out with new products
        that may shift the status of the company for better or worse.
        It uses the last 5 years to try and predict the next "forecast_period" years of revenue .

        """
        data = {
            "Year": self.income_statement.columns.to_list(),
            "Revenue": self.income_statement.loc["Revenue"],
        }

        forecast = pd.DataFrame(data)
        rev_growth = forecast["Revenue"].pct_change() * 100
        rev_growth.index = rev_growth.index.astype(
            int
        )  # Convert index from 'str' to 'int'

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
        y = forecast["Revenue"].values
        # Fit the model.
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecasted_revenue = self.linear.predict(future_X)

        # Get the most recent revenue.
        mr_revenue = forecast["Revenue"].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = rev_growth.loc[year:].mean()

        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_revenue * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forcasted_revenue_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            "forecast_revenue": forecasted_revenue.tolist(),
            "forecast_revenue_with_features": forcasted_revenue_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)

        return data

    def forecast_dilution(self):
        data = {
            "Year": self.income_statement.columns.to_list(),
            "Shares": self.income_statement.loc["Shares Outstanding (Basic)"],
        }
        forecast = pd.DataFrame(data)
        share_change = self.income_statement.loc["Shares Change"]
        share_change.index = share_change.index.astype(int)
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
        y = forecast["Shares"].values
        # Fit the model.
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecasted_dilution = self.linear.predict(future_X)

        # Get the most recent revenue.
        mr_shares = forecast["Shares"].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = share_change.loc[years].mean()
        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_shares * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forcasted_dilution_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            "forecast_dilution": forecasted_dilution.tolist(),
            "forecast_dilution_with_features": forcasted_dilution_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)
        return data

    def forecast_earnings(self):
        data = {
            "Year": self.income_statement.columns.to_list(),
            "Shares": self.income_statement.loc["Net Income"],
        }
        forecast = pd.DataFrame(data)
        share_change = self.income_statement.loc["Shares Change"]
        share_change.index = share_change.index.astype(int)
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
        y = forecast["Shares"].values
        # Fit the model.
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecasted_earnings = self.linear.predict(future_X)

        # Get the most recent revenue.
        mr_shares = forecast["Shares"].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = share_change.loc[years].mean()
        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_shares * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forcasted_earnings_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            "forecast_earnings": forecasted_earnings.tolist(),
            "forecast_earnings_with_features": forcasted_earnings_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)
        return data

    def forecast_equity(self):
        data = {
            "Year": self.balance_sheet.columns.to_list(),
            "Equity": self.balance_sheet.loc["Shareholders' Equity"],
        }
        forecast = pd.DataFrame(data)
        forecast = pd.DataFrame(data)
        equity_growth = forecast["Equity"].pct_change() * 100
        equity_growth.index = equity_growth.index.astype(
            int
        )  # Convert index from 'str' to 'int'

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
        y = forecast["Equity"].values
        # Fit the model.
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecasted_equity = self.linear.predict(future_X)

        # Get the most recent equity.
        mr_equity = forecast["Equity"].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = equity_growth.loc[years].mean()
        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_equity * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forcasted_equity_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            "forecast_equity": forecasted_equity.tolist(),
            "forecast_equity_with_features": forcasted_equity_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)
        return data

    """
    ==================================================
    Free Cash Flow
    ==================================================
    """

    def forecast_fcf(self):
        data = {
            "Year": self.balance_sheet.columns.to_list(),
            "FCF": self.cash_flow.loc["Free Cash Flow"],
        }
        forecast = pd.DataFrame(data)
        forecast = pd.DataFrame(data)
        fcf_growth = forecast["FCF"].pct_change() * 100
        fcf_growth.index = fcf_growth.index.astype(
            int
        )  # Convert index from 'str' to 'int'

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
        y = forecast["FCF"].values
        # Fit the model.
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecasted_fcf = self.linear.predict(future_X)

        # Get the most recent equity.
        mr_fcf = forecast["FCF"].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = fcf_growth.loc[years].mean()
        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_fcf * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forcasted_fcf_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            "forecast_fcf": forecasted_fcf.tolist(),
            "forecast_fcf_with_features": forcasted_fcf_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)
        return data

    """
    ==================================================
    Income Statement
    ==================================================
    """

    def forecast_income_statement_item(
        self, custom_label: str, statement_label: str
    ) -> pd.DataFrame:
        data = {
            "Year": self.income_statement.columns.to_list(),
            f"{custom_label}": self.income_statement.loc[statement_label],
        }

        forecast = pd.DataFrame(data)
        item_growth = forecast[custom_label].pct_change() * 100
        item_growth.index = item_growth.index.astype(
            int
        )  # Convert index from 'str' to 'int'

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
        y = forecast[custom_label].values
        # Fit the model.
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecasted_data = self.linear.predict(future_X)

        # Get the most recent revenue.
        mr_item = forecast[custom_label].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = item_growth.loc[year:].mean()

        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_item * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forcasted_data_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            f"forecast": forecasted_data.tolist(),
            f"forecast_with_features": forcasted_data_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)

        return data

    def forecast_balance_sheet_item(
        self, custom_label: str, statement_label: str
    ) -> pd.DataFrame:
        data = {
            "Year": self.balance_sheet.columns.to_list(),
            f"{custom_label}": self.balance_sheet.loc[statement_label],
        }

        forecast = pd.DataFrame(data)
        item_growth = forecast[custom_label].pct_change() * 100
        item_growth.index = item_growth.index.astype(
            int
        )  # Convert index from 'str' to 'int'

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
        forecast = forecast.dropna()
        X = forecast["Year"].values.reshape(-1, 1)
        X = np.concatenate((X, np.ones((X.shape[0], 1))), axis=1)  # Add intercept
        y = forecast[custom_label].values
        # Fit the model.   b
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecasted_data = self.linear.predict(future_X)

        # Get the most recent revenue.
        mr_item = forecast[custom_label].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = item_growth.loc[year:].mean()

        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_item * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forcasted_data_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            f"forecast": forecasted_data.tolist(),
            f"forecast_with_features": forcasted_data_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)

        return data

    def forecast_cash_flow_item(
        self, custom_label: str, statement_label: str
    ) -> pd.DataFrame:
        data = {
            "Year": self.cash_flow.columns.to_list(),
            f"{custom_label}": self.cash_flow.loc[statement_label],
        }

        forecast = pd.DataFrame(data)
        item_growth = forecast[custom_label].pct_change() * 100
        item_growth.index = item_growth.index.astype(
            int
        )  # Convert index from 'str' to 'int'

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
        y = forecast[custom_label].values
        # Fit the model.
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecasted_data = self.linear.predict(future_X)

        # Get the most recent revenue.
        mr_item = forecast[custom_label].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = item_growth.loc[year:].mean()

        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_item * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forcasted_data_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            f"forecast": forecasted_data.tolist(),
            f"forecast_with_features": forcasted_data_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)

        return data

    """
    ==================================================
    Ratios
    ==================================================
    """

    def forecast_ratio(self, ratio_label: str, statement_label: str) -> pd.DataFrame:

        ratios = self.ratios.drop("Current", axis=1)
        data = {
            "Year": ratios.columns.to_list(),
            f"{ratio_label}": ratios.loc[statement_label],
        }
        forecast = pd.DataFrame(data).dropna()
        print(f"Forecast: {forecast}")
        ratio_growth = forecast[ratio_label].pct_change() * 100
        ratio_growth.index = ratio_growth.index.astype(
            int
        )  # Convert index from 'str' to 'int'
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
        y = forecast[ratio_label].values
        [print(type(i)) for i in y]
        # Fit the model.
        self.linear.fit(X, y)

        # Forecast revenue for future years
        future_years_array = np.array(future_years).reshape(-1, 1)
        future_X = np.concatenate(
            (future_years_array, np.ones((future_years_array.shape[0], 1))), axis=1
        )  # Add intercept
        forecast_data = self.linear.predict(future_X)
        # Get the most recent equity.
        mr_data = forecast[ratio_label].iloc[-1]
        avg_growth = 0
        if len(years) <= self.review_period:
            year = years[0]
        # If company has more data than 'period' only use period.
        elif len(years) > self.review_period:
            year = years[-self.review_period]
        avg_growth = ratio_growth.loc[years].mean()
        # Incorporate additional features into the forecast
        for i, year in enumerate(future_years_array.flatten()):
            future_X[i, 0] = year
            future_X[i, 1] = mr_data * (1 + avg_growth) ** (
                year - 2021
            )  # Projected revenue based on average growth
        forecast_data_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            f"forecast_ratio": forecast_data.tolist(),
            f"forecast_ratio_with_features": forecast_data_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)
        return data

    def forecast_data(self, base_data: pd.Series, base_years: list, label: str):
        data = {
            "Year": base_years,  # List
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
        forecast_data_with_features = self.linear.predict(future_X)

        data = {
            "Year": future_years,
            f"forecast_ratio": forecast_data.tolist(),
            f"forecast_ratio_with_features": forecast_data_with_features.tolist(),
        }
        data = pd.DataFrame(data, index=data["Year"]).drop("Year", axis=1)
        return data

    def forecast_ARIMA(self, data: pd.Series):
        # Define ARIMA model parameters (p, d, q)
        p = 1  # Autoregressive (AR) order
        d = 0  # Differencing order
        q = 1  # Moving Average (MA) order
        n = self.review_period  # Forecast next 'n' steps.

        model = ARIMA(data, order=(p, d, q))
        result = model.fit()
        forecast = result.forecast(steps=n)
        return forecast
