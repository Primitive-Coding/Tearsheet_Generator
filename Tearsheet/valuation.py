import numpy as np
import pandas as pd

from Tearsheet.calculations import Calculations
from Tearsheet.forecast import Forecast
from Tearsheet.forecast_model import ForecastModel


available_valuations = {
    "revenue": {
        "custom_label": "revenue",
        "statement_label": "Revenue",
    },
    "earnings": {
        "custom_label": "earnings",
        "statement_label": "Net Income",
    },
}


class Valuation:
    def __init__(
        self, freq: str, review_period: int = 5, forecast_period: int = 3
    ) -> None:
        self.freq = freq
        self.review_period = review_period
        self.forecast_period = forecast_period
        self.forecast_model = ForecastModel(self.freq)

        # Financial Statements
        self.income_statement = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cash_flow = pd.DataFrame()
        self.ratios = pd.DataFrame()

    def test(self):
        revenue = self.income_statement.loc["Revenue"]
        a = self.forecast.forecast_ARIMA(revenue)

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

        self.calc = Calculations(
            self.income_statement, self.balance_sheet, self.cash_flow, self.ratios
        )
        # self.forecast = Forecast(
        #     calc=self.calc,
        #     review_period=self.review_period,
        #     forecast_period=self.forecast_period,
        # )
        # self.forecast.set_all_statements(
        #     self.income_statement, self.balance_sheet, self.cash_flow, self.ratios
        # )

    """
    Revenue
    """

    def get_revenue_valuation(
        self, predict_ratio: bool = False, predict_shares: bool = False
    ):
        ratio_label = "p/s"
        statement_label = "PS Ratio"
        statement_forecast_label = "Revenue"
        forecast = self.forecast_model.create_forecast(
            self.income_statement.loc["Revenue"]
        )

        forecast = pd.DataFrame(forecast)
        forecast.rename(columns={"predicted_mean": "forecast"}, inplace=True)

        if predict_ratio:
            ratio_label = f"forecast_ratio"
        else:
            ratio_label = f"average_ratio"
        if predict_shares:
            shares_label = f"forecast_shares_basic"
        else:
            shares_label = f"average_shares_basic"
        prep = self.prep_valuation(
            ratio_label=ratio_label,
            statement_label=statement_label,
            predict_ratio=predict_ratio,
            predict_shares=predict_shares,
        )

        print(f"Prep: {prep}")
        df = self.create_valuation(forecast, prep["ratios"], prep["shares"])
        df.rename(
            columns={"average_ratio": ratio_label, "shares_basic": shares_label},
            inplace=True,
        )
        return df

    """
    Net Income
    """

    def get_earnings_valuation(
        self, predict_ratio: bool = False, predict_shares: bool = False
    ):
        """ """

        ratio_label = "p/e"
        statement_label = "PE Ratio"
        forecast_label = "earnings"
        statement_forecast_label = "Net Income"
        forecast = self.forecast.forecast_income_statement_item(
            forecast_label, statement_forecast_label
        )

        if predict_ratio:
            ratio_label = f"forecast_ratio"
        else:
            ratio_label = f"average_ratio"
        if predict_shares:
            shares_label = f"forecast_shares_basic"
        else:
            shares_label = f"average_shares_basic"
        prep = self.prep_valuation(
            ratio_label=ratio_label,
            statement_label=statement_label,
            predict_ratio=predict_ratio,
            predict_shares=predict_shares,
        )
        df = self.create_valuation(forecast, prep["ratios"], prep["shares"])
        df.rename(
            columns={"average_ratio": ratio_label, "shares_basic": shares_label},
            inplace=True,
        )
        return df

    def get_equity_valuation(
        self, predict_ratio: bool = False, predict_shares: bool = False
    ):
        """ """
        ratio_label = "p/b"
        statement_label = "PB Ratio"
        forecast_label = "equity"
        statement_forecast_label = "Shareholders' Equity"
        forecast = self.forecast.forecast_balance_sheet_item(
            forecast_label, statement_forecast_label
        )
        # Determine labels
        if predict_ratio:
            ratio_label = f"forecast_ratio"
        else:
            ratio_label = f"average_ratio"
        if predict_shares:
            shares_label = f"forecast_shares_basic"
        else:
            shares_label = f"average_shares_basic"

        prep = self.prep_valuation(
            ratio_label=ratio_label,
            statement_label=statement_label,
            predict_ratio=predict_ratio,
            predict_shares=predict_shares,
        )

        df = self.create_valuation(forecast, prep["ratios"], prep["shares"])

        df.rename(
            columns={"shares_basic": shares_label},
            inplace=True,
        )
        return df

    def get_fcf_valuation(
        self, predict_ratio: bool = False, predict_shares: bool = False
    ):
        """ """
        ratio_label = "p/fcf"
        statement_label = "P/FCF Ratio"
        forecast_label = "free-cash-flow"
        statement_forecast_label = "Free Cash Flow"
        forecast = self.forecast.forecast_cash_flow_item(
            forecast_label, statement_forecast_label
        )

        if predict_ratio:
            ratio_label = f"forecast_ratio"
        else:
            ratio_label = f"average_ratio"
        if predict_shares:
            shares_label = f"forecast_shares_basic"
        else:
            shares_label = f"average_shares_basic"
        prep = self.prep_valuation(
            ratio_label=ratio_label,
            statement_label=statement_label,
            predict_ratio=predict_ratio,
            predict_shares=predict_shares,
        )
        df = self.create_valuation(forecast, prep["ratios"], prep["shares"])
        df.rename(
            columns={"shares_basic": shares_label},
            inplace=True,
        )
        return df

    def get_ev_sales_valuation(
        self, predict_ratio: bool = False, predict_shares: bool = False
    ):
        """ """
        ratio_label = "ev/sales"
        statement_label = "EV/Sales Ratio"
        forecast_label = "revenue"
        statement_forecast_label = "Revenue"
        forecast = self.forecast.forecast_income_statement_item(
            forecast_label, statement_forecast_label
        )

        if predict_ratio:
            ratio_label = f"forecast_ratio"
        else:
            ratio_label = f"average_ratio"
        if predict_shares:
            shares_label = f"forecast_shares_basic"
        else:
            shares_label = f"average_shares_basic"
        prep = self.prep_valuation(
            ratio_label=ratio_label,
            statement_label=statement_label,
            predict_ratio=predict_ratio,
            predict_shares=predict_shares,
        )
        df = self.create_valuation(
            forecast,
            prep["ratios"],
            prep["shares"],
        )
        df.rename(
            columns={"shares_basic": shares_label},
            inplace=True,
        )
        return df

    def get_sales_current_debt_valuation(
        self, predict_ratio: bool = False, predict_shares: bool = False
    ):
        """ """
        ratio_label = "ev/sales"
        statement_label = "EV/Sales Ratio"
        forecast_label = "revenue"
        statement_forecast_label = "Revenue"
        forecast = self.forecast.forecast_income_statement_item(
            forecast_label, statement_forecast_label
        )

        sales = self.income_statement.loc["Revenue"]
        current_debt = self.balance_sheet.loc["Current Debt"]

        s_cd = sales / current_debt

        forecast_s_cd = self.forecast.forecast_data(
            s_cd, s_cd.index.to_list(), "sales/current_debt"
        )

        print(f"Forecast: {forecast_s_cd}")

        if predict_ratio:
            ratio_label = f"forecast_{ratio_label}"
        else:
            ratio_label = f"average_{ratio_label}"
        if predict_shares:
            shares_label = f"forecast_shares_basic"
        else:
            shares_label = f"average_shares_basic"
        prep = self.prep_valuation(
            ratio_label=ratio_label,
            statement_label=statement_label,
            predict_ratio=predict_ratio,
            predict_shares=predict_shares,
        )

        df = self.create_valuation(
            forecast, forecast_s_cd["forecast_sales/current_debt"], prep["shares"]
        )
        df.rename(
            columns={
                "shares_basic": shares_label,
            },
            inplace=True,
        )
        return df

    def prep_valuation(
        self,
        ratio_label: str,
        statement_label: str,
        predict_ratio: bool = False,
        predict_shares: bool = False,
    ):
        """

        :param ratio_label: Label for the ratio. Such as price-to-earnings (P/E).
        :param statement_label: Label for the item on the statement. (PE Ratio)
        :param predict_ratios:
        """

        ratios_table = self.ratios.drop("Current", axis=1)
        years = ratios_table.columns
        # Predict the financial ratio.
        if predict_ratio:
            ratios = self.forecast_model.create_forecast(
                ratios_table.loc[statement_label]
            )
            ratios = pd.DataFrame(ratios).rename(
                columns={"predicted_mean": "forecast_ratio"}
            )
            ratios = ratios[f"forecast_ratio"].to_list()
            ratio_label = f"forecast_ratio"
        elif not predict_ratio:
            ratio_label = f"average_ratio"
            ratios = self.ratios.loc[statement_label].to_list()

        # Predict the amount of share dilution
        if predict_shares:
            shares_basic = self.forecast.forecast_dilution()
            shares_basic = shares_basic["forecast_dilution"].to_list()
        elif not predict_shares:
            shares_basic = self.income_statement.loc[
                "Shares Outstanding (Basic)"
            ].to_list()

        # Store in local variable so changes made do not effect the class variable.
        review_period = self.review_period
        if len(years) > self.review_period:
            review_period += 1
            years = years[-review_period:]
            if not predict_ratio:
                ratios = ratios[-review_period:]
                average_ratio = 0
                for i in ratios:
                    average_ratio += i
                ratios = average_ratio / (len(years))
            if not predict_shares:
                shares_basic = shares_basic[-review_period:]

        return {"ratios": ratios, "shares": shares_basic}

    def create_valuation(self, forecast_data, ratio_data, share_data):
        years = self.ratios.columns.to_list()
        base_year = int(years[-2]) + 1
        forecast_years = []
        i = 1
        # Use the range of "rev_forecast" to determine how many years have been forecasted.
        for i in range(len(forecast_data)):
            forecast_years.append(int(base_year) + i)
            i += 1
        # Fit data into DataFrame
        data = {
            "forecast_years": [],
            "forecast_ratio": ratio_data,
            "forecast": forecast_data["forecast"].tolist(),
            "shares_basic": share_data[-self.forecast_period :],
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
