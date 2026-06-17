import os
import warnings

import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss
import matplotlib.pyplot as plt



DATA_FILE = "data.xlsx"
SHEET_NAME = "returns data"
DATE_COL = "perf_date"
TARGET_COL = "Hedge Fund"
OUTPUT_FOLDER = "q2_outputs"
ROLLING_WINDOW = 36

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 0. load and clean data

print("\n" + "=" * 80)
print("0. LOAD AND CLEAN DATA")
print("=" * 80)

data = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME)

# find columns starting with "Factor -" 
factor_cols = [col for col in data.columns if str(col).startswith("Factor -")]

print(f"Target column: {TARGET_COL}")
print(f"Number of factor columns found: {len(factor_cols)}")

data[DATE_COL] = pd.to_datetime(data[DATE_COL])
data = data.sort_values(DATE_COL).reset_index(drop=True)

# drop missing data
model_cols = [TARGET_COL] + factor_cols
rows_before = len(data)
data = data.dropna(subset=model_cols).reset_index(drop=True)
rows_after = len(data)

print(f"Rows before cleaning: {rows_before}")
print(f"Rows after cleaning: {rows_after}")
print(f"Rows removed: {rows_before - rows_after}")

# correct extreme value
large_value_count = int((data[factor_cols].abs() > 1).sum().sum())
print(f"Extreme factor values found: {large_value_count}")

if large_value_count > 0:
    data.loc[:, factor_cols] = data[factor_cols].mask(
        data[factor_cols].abs() > 1,
        data[factor_cols] / 1_000_000,
    )
    print("Extreme values were corrected by dividing by 1,000,000.")

print("Data is ready")

# ============================================================
# Q2.1 fit a multilinear regression model and calculate alpha and betas

def fit_regression_model(data, factor_cols):
    print("\n" + "=" * 80)
    print("Q2.1: MULTILINEAR REGRESSION")
    print("=" * 80)

    y = data[TARGET_COL]

    X_all = sm.add_constant(data[factor_cols])
    full_model = sm.OLS(y, X_all).fit()

    print("\nFull model fitted using all factors.")
    print(f"Full model R-squared: {full_model.rsquared:.4f}")
    print(f"Full model adjusted R-squared: {full_model.rsquared_adj:.4f}")

    # keep factors that are statistically significant at the 10% level in the full model
    factor_pvalues = full_model.pvalues.drop("const")
    selected_factors = factor_pvalues[factor_pvalues < 0.10].index.tolist()

    # if no factor passes the threshold, keep all factors
    if len(selected_factors) == 0:
        selected_factors = factor_cols.copy()
        print("\nNo factor had p-value below 10%, so I kept all factors.")
    else:
        print("\nSelected factors with p-value below 10% in the full model:")
        for factor in selected_factors:
            print(f"  - {factor}, p-value = {factor_pvalues[factor]:.4f}")

    # refit the final model using selected factors
    X_final = sm.add_constant(data[selected_factors])
    final_model = sm.OLS(y, X_final).fit()

    monthly_alpha = final_model.params["const"]
    annual_alpha = monthly_alpha * 12

    print("\nFinal model alpha:")
    print(f"Monthly alpha: {monthly_alpha:.6f}")
    print(f"Annualised alpha: {annual_alpha:.2%}")

    beta_table = pd.DataFrame({
        "Beta": final_model.params[selected_factors],
        "p-value": final_model.pvalues[selected_factors],
    })

    print("\nFinal model betas:")
    print(beta_table.to_string(float_format=lambda x: f"{x:.6f}"))

    print("\nFinal model statistics:")
    print(f"R-squared: {final_model.rsquared:.4f}")
    print(f"Adjusted R-squared: {final_model.rsquared_adj:.4f}")
    print(f"AIC: {final_model.aic:.4f}")
    print(f"BIC: {final_model.bic:.4f}")

    return final_model, selected_factors, beta_table


final_model, selected_factors, beta_table = fit_regression_model(data, factor_cols)


# ============================================================
# Q2.2 evaluate the selected model

def evaluate_model(data, final_model):
    print("\n" + "=" * 80)
    print("Q2.2: MODEL EVALUATION")
    print("=" * 80)

    y = data[TARGET_COL]

    residuals = final_model.resid
    fitted_values = final_model.fittedvalues

    rmse = (residuals ** 2).mean() ** 0.5

    print("\nModel fit:")
    print(f"R-squared: {final_model.rsquared:.4f}")
    print(f"Adjusted R-squared: {final_model.rsquared_adj:.4f}")
    print(f"F-test p-value: {final_model.f_pvalue:.6f}")
    print(f"RMSE: {rmse:.6f}")

    # the coefficients and p-values from the selected OLS model
    coefficient_table = pd.DataFrame({
        "Coefficient": final_model.params,
        "p-value": final_model.pvalues,
    })

    print("\nCoefficient significance:")
    print(coefficient_table.to_string(float_format=lambda x: f"{x:.6f}"))

    # Simple residual diagnostics: Durbin-Watson & Jarque-Bera
    dw_stat = sm.stats.stattools.durbin_watson(residuals)
    jb_stat, jb_pvalue = stats.jarque_bera(residuals)

    print("\nResidual diagnostics:")
    print(f"Durbin-Watson statistic: {dw_stat:.4f}")
    print(f"Jarque-Bera p-value for residual normality: {jb_pvalue:.6f}")

    # Actual vs Fitted
    plt.figure(figsize=(10, 5))
    plt.plot(data[DATE_COL], y, label="Actual fund return")
    plt.plot(data[DATE_COL], fitted_values, label="Fitted return")
    plt.xlabel("Date")
    plt.ylabel("Monthly return")
    plt.title("Q2.2 Actual vs Fitted Returns")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, "q2_2_actual_vs_fitted.png"), dpi=300)
    plt.close()

    # residual plot
    plt.figure(figsize=(10, 5))
    plt.plot(data[DATE_COL], residuals)
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.xlabel("Date")
    plt.ylabel("Residual")
    plt.title("Q2.2 Residuals Over Time")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, "q2_2_residuals.png"), dpi=300)
    plt.close()

    print(f"\nQ2.2 plots saved in: {OUTPUT_FOLDER}")

    print("\nQ2.2 conclusion:")

    if final_model.f_pvalue < 0.05:
        print("The regression is statistically significant overall based on the F-test.")
    else:
        print("The regression is not statistically significant overall based on the F-test.")

    if 1.5 < dw_stat < 2.5:
        print("The Durbin-Watson statistic is close to 2, so there is no strong evidence of residual autocorrelation.")
    else:
        print("The Durbin-Watson statistic is far from 2, suggesting possible residual autocorrelation.")

    if jb_pvalue < 0.05:
        print("The Jarque-Bera test suggests that the residuals are not normally distributed.")
    else:
        print("The Jarque-Bera test does not show strong evidence against residual normality.")

    return residuals, fitted_values, coefficient_table


residuals, fitted_values, coefficient_table = evaluate_model(data, final_model)


# ============================================================
# Q2.3 compare fund return with factor portfolio return

def compare_profitability(data, final_model, selected_factors):
    print("\n" + "=" * 80)
    print("Q2.3: PROFITABILITY COMPARISON")
    print("=" * 80)

    # build the factor portfolio using the regression betas as weights
    beta_weights = final_model.params[selected_factors]
    factor_portfolio_returns = data[selected_factors].mul(beta_weights, axis=1).sum(axis=1)
    fund_returns = data[TARGET_COL]

    print("\nFactor portfolio weights:")
    for factor in selected_factors:
        print(f"{factor}: {beta_weights[factor]:.6f}")

    # Sharpe ratio
    fund_annual_return = fund_returns.mean() * 12
    factor_annual_return = factor_portfolio_returns.mean() * 12

    fund_sharpe = (fund_returns.mean() / fund_returns.std(ddof=1)) * (12 ** 0.5)
    factor_sharpe = (factor_portfolio_returns.mean() / factor_portfolio_returns.std(ddof=1)) * (12 ** 0.5)

    performance_table = pd.DataFrame({
        "Annualised Return": [fund_annual_return, factor_annual_return],
        "Sharpe Ratio": [fund_sharpe, factor_sharpe],
        "Cumulative Return": [
            (1 + fund_returns).prod() - 1,
            (1 + factor_portfolio_returns).prod() - 1
        ],
    }, index=["Hedge Fund", "Factor Portfolio"])

    print("\nPerformance comparison:")
    print(performance_table.to_string(float_format=lambda x: f"{x:.6f}"))

    print("\nQ2.3 conclusion:")
    if fund_annual_return > factor_annual_return:
        print("The hedge fund has the higher annualised return.")
    else:
        print("The factor portfolio has the higher annualised return.")

    if fund_sharpe > factor_sharpe:
        print("The hedge fund also has the higher Sharpe ratio.")
    else:
        print("The factor portfolio has the higher Sharpe ratio.")

    return fund_returns, factor_portfolio_returns, performance_table


fund_returns, factor_portfolio_returns, performance_table = compare_profitability(
    data,
    final_model,
    selected_factors
)


# ============================================================
# Q2.4 Compare the risk of the fund and factor portfolio

def compare_risk(fund_returns, factor_portfolio_returns):
    print("\n" + "=" * 80)
    print("Q2.4: RISK COMPARISON")
    print("=" * 80)

    risk_rows = []

    for name, returns in {
        "Hedge Fund": fund_returns,
        "Factor Portfolio": factor_portfolio_returns,
    }.items():
        annual_vol = returns.std(ddof=1) * (12 ** 0.5)

        wealth = (1 + returns).cumprod()
        peak = wealth.cummax()
        max_drawdown = (wealth / peak - 1).min()

        var_5 = -returns.quantile(0.05)
        es_5 = -returns[returns <= returns.quantile(0.05)].mean()

        risk_rows.append({
            "Strategy": name,
            "Annualised Volatility": annual_vol,
            "Maximum Drawdown": max_drawdown,
            "Monthly VaR 5%": var_5,
            "Monthly Expected Shortfall 5%": es_5,
        })

    risk_table = pd.DataFrame(risk_rows).set_index("Strategy")

    print("\nRisk comparison:")
    print(risk_table.to_string(float_format=lambda x: f"{x:.6f}"))

    print("\nQ2.4 conclusion:")
    print(f"Higher volatility: {risk_table['Annualised Volatility'].idxmax()}")
    print(f"Larger drawdown: {risk_table['Maximum Drawdown'].idxmin()}")
    print(f"Larger expected shortfall: {risk_table['Monthly Expected Shortfall 5%'].idxmax()}")

    return risk_table


risk_table = compare_risk(fund_returns, factor_portfolio_returns)

# ============================================================
# Q2.5 Test whether the betas are stationary

def test_beta_stationarity(data, selected_factors):
    print("\n" + "=" * 80)
    print("Q2.5: BETA STATIONARITY")
    print("=" * 80)

    # create rolling beta series using a 36-month rolling window
    rolling_rows = []

    for end in range(ROLLING_WINDOW, len(data) + 1):
        window_data = data.iloc[end - ROLLING_WINDOW:end]
        y_window = window_data[TARGET_COL]
        X_window = sm.add_constant(window_data[selected_factors])
        rolling_model = sm.OLS(y_window, X_window).fit()

        row = {DATE_COL: data.loc[end - 1, DATE_COL]}

        for factor in selected_factors:
            row[factor] = rolling_model.params[factor]

        rolling_rows.append(row)

    rolling_betas = pd.DataFrame(rolling_rows)

    # stationarity test
    stationarity_rows = []

    for factor in selected_factors:
        beta_series = rolling_betas[factor].dropna()

        adf_pvalue = adfuller(beta_series)[1]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kpss_pvalue = kpss(beta_series, regression="c", nlags="auto")[1]

        if adf_pvalue < 0.05 and kpss_pvalue >= 0.05:
            result = "Likely stationary"
        elif adf_pvalue >= 0.05 and kpss_pvalue < 0.05:
            result = "Likely non-stationary"
        else:
            result = "Mixed / inconclusive"

        stationarity_rows.append({
            "Factor": factor,
            "ADF p-value": adf_pvalue,
            "KPSS p-value": kpss_pvalue,
            "Conclusion": result,
        })

    stationarity_table = pd.DataFrame(stationarity_rows).set_index("Factor")

    print(f"\nRolling window: {ROLLING_WINDOW} months")
    print("\nStationarity test results:")
    print(stationarity_table.to_string(float_format=lambda x: f"{x:.6f}"))

    # plot rolling betas
    plt.figure(figsize=(10, 5))

    for factor in selected_factors:
        plt.plot(rolling_betas[DATE_COL], rolling_betas[factor], label=factor)

    plt.xlabel("Date")
    plt.ylabel("Rolling beta")
    plt.title("Q2.5 Rolling Betas")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_FOLDER, "q2_5_rolling_betas.png"), dpi=300)
    plt.close()

    print(f"\nQ2.5 rolling beta plot saved in: {OUTPUT_FOLDER}")

    print("\nQ2.5 conclusion:")

    if (stationarity_table["Conclusion"] == "Likely stationary").all():
        print(
            "The rolling beta tests suggest that the selected factor betas are reasonably stationary."
        )
    else:
        print(
            "At least one beta is not clearly stationary. "
            "The fund's factor exposures may change over time. "
            "A static beta model may therefore miss current risks, so rolling beta monitoring is useful."
        )

    return rolling_betas, stationarity_table


rolling_betas, stationarity_table = test_beta_stationarity(data, selected_factors)


# ============================================================
# Finish

print("\n" + "=" * 80)
print("QUESTION 2 COMPLETED")
print(f"Plots were saved in: {OUTPUT_FOLDER}")
