# Number storage & manipulation
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


pd.set_option("display.float_format", lambda x: "{:.2f}".format(x))


class Calculations:
    def __init__(
        self,
        income_statement: pd.DataFrame,
        balance_sheet: pd.DataFrame,
        cash_flow: pd.DataFrame,
        ratios: pd.DataFrame,
    ) -> None:
        self.income_statement = income_statement
        self.balance_sheet = balance_sheet
        self.cash_flow = cash_flow
        self.ratios = ratios
        self.linear = LinearRegression()

    def calc_altman_z(self) -> pd.DataFrame:
        """
        wc (float): Working Capital
        re (float): Retained Earnings
        ebit (float): Earnings Before Interest and Taxes (EBIT)
        mve (float): Market Value of Equity
        sales (float): Sales
        ta (float): Total Assets
        """

        total_assets = self.balance_sheet.loc["Total Assets"]

        mve = (
            self.income_statement.loc["EPS (Basic)"].astype(float)
            * self.ratios.loc["PE Ratio"].astype(float)
        ).drop("Current", axis=0)

        A = self.balance_sheet.loc["Working Capital"] / total_assets
        B = self.balance_sheet.loc["Retained Earnings"] / total_assets
        C = self.income_statement.loc["EBIT"] / total_assets
        D = mve / (total_assets - mve)
        E = self.income_statement.loc["Revenue"] / total_assets

        Z = (1.2 * A) + (1.4 * B) + (3.3 * C) + (0.6 * D) + (1.0 * E)
        df = pd.DataFrame(columns=["Score", "Label"])
        df["Score"] = Z
        df["Label"] = df["Score"].apply(self.label_altman_score)
        return df

    """
    Peripheral Functions 
    """

    def calc_dcf(
        self,
        ref_years: int = 5,
        forecast_years: int = 5,
        discount_rate: float = 0.1,
        growth_rate: float = 0.06,
    ):
        """
        :param ref_years: Years to reference.
        :param forecast_years: Years to forecast.
        :param discount_rate: WACC


        Attempts to create a discounted cash flow analysis.

        *NOTE* Keep an eye on interest expense.
        """

        # Revenue
        forcasted_revenue = self.forecast_revenue(
            period=ref_years, num_years_forecast=forecast_years
        )
        years = self.income_statement.columns.to_list()

        if len(years) > ref_years:
            years = years[-ref_years:]

        # Operating Margin
        operating_margin = (
            self.income_statement.loc["Operating Income"]
            / self.income_statement.loc["Revenue"]
        )
        avg_operating_margin = operating_margin.loc[years].mean()

        # Taxes
        try:
            tax_rate = self.income_statement.loc["Effective Tax Rate"]
        except KeyError:
            tax_rate = (
                self.income_statement.loc["Income Tax"]
                / self.income_statement.loc["Pretax Income"].abs()
            )

        avg_tax_rate = tax_rate.loc[years].mean()

        # Capital Expenditures
        capex = self.cash_flow.loc["Capital Expenditures"]

        avg_capex = capex.loc[years].mean()

        # Interest expense
        interest_expense = self.income_statement.loc["Interest Expense / Income"]

        avg_interest_expense = interest_expense.loc[years].mean()
        # Calcuate operating income using forecasted revenue.
        operating_income = [rev * operating_margin for rev in forcasted_revenue]
        # Calculate tax using forecasted operating income.
        tax = [oi * avg_tax_rate for oi in operating_income]
        FCF = [oi - tx + avg_capex for oi, tx in zip(operating_income, tax_rate)]

        # Calculate discounted cash flow.
        discount_factors = [(1 + discount_rate) ** i for i in range(1, len(FCF) + 1)]
        discounted_FCF = [fcf / df for fcf, df in zip(FCF, discount_factors)]

        # Calculate terminal value.
        # Calculate terminal value
        terminal_value = (FCF[-1] * (1 + growth_rate)) / (discount_rate - growth_rate)
        discounted_terminal_value = terminal_value / discount_factors[-1]
        # Calculate total enterprise value
        total_enterprise_value = sum(discounted_FCF) + discounted_terminal_value
        # Number of shares outstanding
        shares_outstanding = self.income_statement.loc["Shares Outstanding (Basic)"]
        mr_shares = shares_outstanding.loc[years[-1]]
        # Calculate fair value per share
        fair_value_per_share = total_enterprise_value / mr_shares
        # print(
        #     f"""
        #       Operating Margin: {avg_operating_margin}
        #       Tax Rage: {avg_tax_rate}
        #       CapEx: {avg_capex}
        #       Interest: {avg_interest_expense}"""
        # )

    def calculate_average_dilution(self, period: int = 5):
        years = self.income_statement.columns.to_list()
        share_change = self.income_statement.loc["Shares Change"]
        if len(years) > period:
            years = years[-period:]
        # Selects only the years within the period.
        share_change = share_change.loc[years]
        average_share_change = share_change.mean()
        return average_share_change


# X = np.concatenate(())


"""
# Assuming you have already forecasted revenue for future years and stored it in a variable named `forecasted_revenue_with_features`

# Calculate future cash flows (FCF) based on forecasted revenue
# For simplicity, let's assume FCF is equal to forecasted revenue
forecasted_FCF = forecasted_revenue_with_features

# Discount future cash flows to their present value
discount_rate = 0.1  # Example discount rate (WACC)
discounted_FCF = [fcf / ((1 + discount_rate) ** (year - 2021)) for year, fcf in zip(future_years.flatten(), forecasted_FCF)]

# Estimate terminal value (assuming perpetuity growth method)
terminal_growth_rate = 0.03  # Example perpetuity growth rate
terminal_value = forecasted_FCF[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)

# Sum present values
total_present_value = sum(discounted_FCF) + terminal_value

# Number of shares outstanding (example)
shares_outstanding = 1000000

# Calculate fair share price
fair_share_price = total_present_value / shares_outstanding

print(f"Fair share price: ${fair_share_price:.2f}")

"""
