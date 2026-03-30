from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .analytics_helpers import safe_pct
from .models import BreakdownPoint, ScenarioMode, TrendPoint


@dataclass(slots=True)
class HoltForecastResult:
    alpha: float
    beta: float
    fitted: pd.Series
    forecast: pd.Series
    lower: pd.Series
    upper: pd.Series
    residual_std: float
    mape: float
    wape: float


@dataclass(slots=True)
class DriverForecast:
    label: str
    raw_label: str
    latest_actual: float
    forecast_next: float
    forecast_low: float
    forecast_high: float
    forecast_delta_pct: float
    share_pct: float
    latest_share_pct: float
    base_share_pct: float
    low_share_pct: float
    high_share_pct: float
    recent_growth_pct: float
    volatility_pct: float
    action: str


def build_monthly_sum_series(
    df: pd.DataFrame,
    value_col: str = "sales_amount",
    group_value: str | None = None,
    group_col: str | None = None,
) -> pd.Series:
    working = df.dropna(subset=["order_day"]).copy()
    if group_col and group_value is not None:
        working = working[working[group_col] == group_value]
    if working.empty or value_col not in working.columns:
        return pd.Series(dtype="float64")

    monthly = (
        working.assign(period=working["order_day"].dt.to_period("M").dt.to_timestamp())
        .groupby("period")[value_col]
        .sum()
        .sort_index()
        .astype(float)
    )
    if monthly.empty:
        return monthly
    full_index = pd.date_range(monthly.index.min(), monthly.index.max(), freq="MS")
    return monthly.reindex(full_index, fill_value=0.0).astype(float)


def build_monthly_grouped_sum_matrix(
    df: pd.DataFrame,
    group_col: str,
    value_col: str = "sales_amount",
) -> pd.DataFrame:
    working = df.dropna(subset=["order_day", group_col]).copy()
    if working.empty or value_col not in working.columns:
        return pd.DataFrame(dtype="float64")

    monthly = (
        working.assign(period=working["order_day"].dt.to_period("M").dt.to_timestamp())
        .groupby(["period", group_col])[value_col]
        .sum()
        .unstack(fill_value=0.0)
        .sort_index()
        .astype(float)
    )
    if monthly.empty:
        return monthly
    full_index = pd.date_range(monthly.index.min(), monthly.index.max(), freq="MS")
    monthly = monthly.reindex(full_index, fill_value=0.0).astype(float)
    monthly.columns = monthly.columns.map(str)
    return monthly


def build_monthly_distinct_series(
    df: pd.DataFrame,
    id_col: str,
    group_value: str | None = None,
    group_col: str | None = None,
) -> pd.Series:
    working = df.dropna(subset=["order_day", id_col]).copy()
    if group_col and group_value is not None:
        working = working[working[group_col] == group_value]
    if working.empty:
        return pd.Series(dtype="float64")

    monthly = (
        working.assign(period=working["order_day"].dt.to_period("M").dt.to_timestamp())
        .groupby("period")[id_col]
        .nunique()
        .sort_index()
        .astype(float)
    )
    if monthly.empty:
        return monthly
    full_index = pd.date_range(monthly.index.min(), monthly.index.max(), freq="MS")
    return monthly.reindex(full_index, fill_value=0.0).astype(float)


def _holt_core(values: np.ndarray, alpha: float, beta: float) -> tuple[np.ndarray, float, float, np.ndarray]:
    if values.size == 0:
        return np.array([], dtype=float), 0.0, 0.0, np.array([], dtype=float)
    if values.size == 1:
        return np.array([values[0]], dtype=float), float(values[0]), 0.0, np.array([], dtype=float)

    level = float(values[0])
    trend = float(values[1] - values[0])
    fitted = np.empty(values.size, dtype=float)
    fitted[0] = values[0]

    for idx in range(1, values.size):
        forecast = level + trend
        fitted[idx] = forecast
        actual = float(values[idx])
        previous_level = level
        level = alpha * actual + (1.0 - alpha) * forecast
        trend = beta * (level - previous_level) + (1.0 - beta) * trend

    residuals = values[1:] - fitted[1:]
    return fitted, level, trend, residuals


def _grid_values() -> np.ndarray:
    # Coarser search keeps forecast latency compatible with interactive BI.
    return np.linspace(0.15, 0.85, 5)


def fit_holt_linear(series: pd.Series, horizon: int = 3) -> HoltForecastResult:
    series = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if series.empty:
        empty_index = pd.DatetimeIndex([], freq="MS")
        empty_series = pd.Series(dtype="float64", index=empty_index)
        return HoltForecastResult(
            alpha=0.5,
            beta=0.1,
            fitted=empty_series,
            forecast=empty_series,
            lower=empty_series,
            upper=empty_series,
            residual_std=0.0,
            mape=0.0,
            wape=0.0,
        )

    if len(series) < 3:
        last_value = float(series.iloc[-1])
        slope = float(series.diff().dropna().iloc[-1]) if len(series) > 1 else 0.0
        fitted = series.copy()
        forecast_index = pd.date_range(series.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
        forecast_values = [max(last_value + slope * step, 0.0) for step in range(1, horizon + 1)]
        forecast = pd.Series(forecast_values, index=forecast_index, dtype="float64")
        lower = forecast.copy()
        upper = forecast.copy()
        return HoltForecastResult(
            alpha=0.5,
            beta=0.1,
            fitted=fitted,
            forecast=forecast,
            lower=lower,
            upper=upper,
            residual_std=0.0,
            mape=0.0,
            wape=0.0,
        )

    values = series.to_numpy(dtype=float)
    best_sse: float | None = None
    best_params = (0.4, 0.2)
    best_fitted = None
    best_level = 0.0
    best_trend = 0.0
    best_residuals = None

    for alpha in _grid_values():
        for beta in _grid_values():
            fitted, level, trend, residuals = _holt_core(values, float(alpha), float(beta))
            sse = float(np.square(residuals).sum())
            if best_sse is None or sse < best_sse:
                best_sse = sse
                best_params = (float(alpha), float(beta))
                best_fitted = fitted
                best_level = level
                best_trend = trend
                best_residuals = residuals

    fitted_series = pd.Series(best_fitted, index=series.index, dtype="float64")
    residual_std = float(np.std(best_residuals, ddof=1)) if best_residuals is not None and len(best_residuals) > 1 else 0.0
    forecast_index = pd.date_range(series.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    forecast_values = [max(best_level + best_trend * step, 0.0) for step in range(1, horizon + 1)]
    forecast = pd.Series(forecast_values, index=forecast_index, dtype="float64")
    if residual_std > 0:
        lower = pd.Series(
            [max(value - 1.96 * residual_std * np.sqrt(step), 0.0) for step, value in enumerate(forecast_values, start=1)],
            index=forecast_index,
            dtype="float64",
        )
        upper = pd.Series(
            [value + 1.96 * residual_std * np.sqrt(step) for step, value in enumerate(forecast_values, start=1)],
            index=forecast_index,
            dtype="float64",
        )
    else:
        lower = forecast.copy()
        upper = forecast.copy()

    actual_mask = series.iloc[1:] != 0
    if actual_mask.any() and best_residuals is not None and len(best_residuals) == len(series) - 1:
        actual_values = series.iloc[1:][actual_mask]
        fitted_values = fitted_series.iloc[1:][actual_mask]
        mape = float((np.abs((actual_values - fitted_values) / actual_values)).mean() * 100.0)
        denominator = float(actual_values.abs().sum())
        wape = float((np.abs(actual_values - fitted_values).sum() / denominator) * 100.0) if denominator else 0.0
    else:
        mape = 0.0
        wape = 0.0

    return HoltForecastResult(
        alpha=best_params[0],
        beta=best_params[1],
        fitted=fitted_series,
        forecast=forecast,
        lower=lower,
        upper=upper,
        residual_std=residual_std,
        mape=mape,
        wape=wape,
    )


def rolling_backtest_mape(series: pd.Series, minimum_train: int = 6) -> float:
    series = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if len(series) < minimum_train + 1:
        return 0.0

    errors: list[float] = []
    for cutoff in range(minimum_train, len(series)):
        train = series.iloc[:cutoff]
        actual = float(series.iloc[cutoff])
        if actual == 0:
            continue
        fit = fit_holt_linear(train, horizon=1)
        forecast_value = float(fit.forecast.iloc[0]) if not fit.forecast.empty else float(train.iloc[-1])
        errors.append(abs((actual - forecast_value) / actual) * 100.0)
    return float(np.mean(errors)) if errors else 0.0


def build_predictive_trend(series: pd.Series, horizon: int = 3) -> tuple[list[TrendPoint], HoltForecastResult]:
    fit = fit_holt_linear(series, horizon=horizon)
    trend: list[TrendPoint] = []
    last_actual = float(series.iloc[-1]) if not series.empty else 0.0

    for idx, (period, value) in enumerate(series.items()):
        fitted_value = float(fit.fitted.iloc[idx]) if idx < len(fit.fitted) else None
        trend.append(
            TrendPoint(
                period_key=str(pd.Period(period, freq="M")),
                period_label=pd.Timestamp(period).strftime("%b %Y"),
                current_value=float(value),
                previous_value=float(series.iloc[idx - 1]) if idx > 0 else None,
                delta_pct=safe_pct(float(value), float(series.iloc[idx - 1])) if idx > 0 else 0.0,
                baseline_value=fitted_value,
                is_projection=False,
            )
        )

    for step, (period, value) in enumerate(fit.forecast.items(), start=1):
        trend.append(
            TrendPoint(
                period_key=str(pd.Period(period, freq="M")),
                period_label=pd.Timestamp(period).strftime("%b %Y"),
                current_value=float(value),
                previous_value=None,
                delta_pct=safe_pct(float(value), last_actual),
                baseline_value=None,
                is_projection=True,
                lower_bound=float(fit.lower.iloc[step - 1]) if step - 1 < len(fit.lower) else None,
                upper_bound=float(fit.upper.iloc[step - 1]) if step - 1 < len(fit.upper) else None,
            )
        )

    return trend, fit


def _recent_growth_pct(series: pd.Series) -> float:
    if len(series) >= 6:
        recent = float(series.tail(3).mean())
        prior = float(series.iloc[-6:-3].mean())
        return safe_pct(recent, prior)
    if len(series) >= 2:
        return safe_pct(float(series.iloc[-1]), float(series.iloc[-2]))
    return 0.0


def _volatility_pct(series: pd.Series) -> float:
    changes = series.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    if changes.empty:
        return 0.0
    return float(changes.tail(6).std(ddof=0) * 100.0)


def recommend_driver_action(share_pct: float, forecast_delta_pct: float, recent_growth_pct: float, volatility_pct: float) -> str:
    if share_pct >= 35.0 and forecast_delta_pct < 0.0:
        return "Defend core demand"
    if share_pct >= 25.0 and forecast_delta_pct >= 4.0:
        return "Protect core and support supply"
    if forecast_delta_pct >= 8.0 and recent_growth_pct >= 4.0:
        return "Accelerate momentum"
    if forecast_delta_pct <= -8.0:
        return "Investigate softness"
    if volatility_pct >= 20.0:
        return "Monitor volatility"
    return "Maintain watch"


def build_driver_forecasts(
    current_df: pd.DataFrame,
    group_col: str = "category",
    horizon: int = 1,
    limit: int = 6,
) -> list[DriverForecast]:
    if current_df.empty or group_col not in current_df.columns:
        return []

    monthly_matrix = build_monthly_grouped_sum_matrix(current_df, group_col=group_col)
    if monthly_matrix.empty:
        return []

    grouped = monthly_matrix.sum(axis=0).sort_values(ascending=False)
    labels = [str(label) for label in grouped.head(limit).index.tolist()]
    if not labels:
        return []

    drivers: list[DriverForecast] = []
    total_forecast = 0.0
    for label in labels:
        series = monthly_matrix[label].astype(float)
        if series.empty:
            continue
        fit = fit_holt_linear(series, horizon=horizon)
        forecast_next = float(fit.forecast.iloc[0]) if not fit.forecast.empty else float(series.iloc[-1])
        latest_actual = float(series.iloc[-1])
        forecast_low = float(fit.lower.iloc[0]) if not fit.lower.empty else forecast_next
        forecast_high = float(fit.upper.iloc[0]) if not fit.upper.empty else forecast_next
        driver = DriverForecast(
            label=label,
            raw_label=label,
            latest_actual=latest_actual,
            forecast_next=forecast_next,
            forecast_low=forecast_low,
            forecast_high=forecast_high,
            forecast_delta_pct=safe_pct(forecast_next, latest_actual),
            share_pct=0.0,
            latest_share_pct=0.0,
            base_share_pct=0.0,
            low_share_pct=0.0,
            high_share_pct=0.0,
            recent_growth_pct=_recent_growth_pct(series),
            volatility_pct=_volatility_pct(series),
            action="",
        )
        total_forecast += forecast_next
        drivers.append(driver)

    total_latest = float(sum(driver.latest_actual for driver in drivers))
    total_low = float(sum(driver.forecast_low for driver in drivers))
    total_high = float(sum(driver.forecast_high for driver in drivers))

    for driver in drivers:
        driver.latest_share_pct = (driver.latest_actual / total_latest * 100.0) if total_latest else 0.0
        driver.base_share_pct = (driver.forecast_next / total_forecast * 100.0) if total_forecast else 0.0
        driver.low_share_pct = (driver.forecast_low / total_low * 100.0) if total_low else 0.0
        driver.high_share_pct = (driver.forecast_high / total_high * 100.0) if total_high else 0.0
        driver.share_pct = driver.base_share_pct
        driver.action = recommend_driver_action(
            share_pct=driver.share_pct,
            forecast_delta_pct=driver.forecast_delta_pct,
            recent_growth_pct=driver.recent_growth_pct,
            volatility_pct=driver.volatility_pct,
        )

    drivers.sort(key=lambda item: item.forecast_next, reverse=True)
    return drivers


def scenario_series_name(scenario_mode: ScenarioMode) -> str:
    if scenario_mode == "Conservative":
        return "Conservative Forecast"
    if scenario_mode == "Upside":
        return "Upside Forecast"
    return "Base Forecast"


def driver_scenario_value(driver: DriverForecast, scenario_mode: ScenarioMode) -> float:
    if scenario_mode == "Conservative":
        return float(driver.forecast_low)
    if scenario_mode == "Upside":
        return float(driver.forecast_high)
    return float(driver.forecast_next)


def driver_scenario_share(driver: DriverForecast, scenario_mode: ScenarioMode) -> float:
    if scenario_mode == "Conservative":
        return float(driver.low_share_pct)
    if scenario_mode == "Upside":
        return float(driver.high_share_pct)
    return float(driver.base_share_pct)


def driver_scenario_delta_pct(driver: DriverForecast, scenario_mode: ScenarioMode) -> float:
    return safe_pct(driver_scenario_value(driver, scenario_mode), float(driver.latest_actual))


def driver_share_shift_pct(driver: DriverForecast, scenario_mode: ScenarioMode) -> float:
    return driver_scenario_share(driver, scenario_mode) - float(driver.latest_share_pct)


def apply_scenario_to_trend(trend: list[TrendPoint], scenario_mode: ScenarioMode) -> list[TrendPoint]:
    if scenario_mode == "Base":
        return [point.model_copy(deep=True) for point in trend]

    adjusted: list[TrendPoint] = []
    last_actual = next((float(point.current_value) for point in reversed(trend) if not point.is_projection), 0.0)
    for point in trend:
        next_point = point.model_copy(deep=True)
        if next_point.is_projection:
            if scenario_mode == "Conservative" and next_point.lower_bound is not None:
                next_point.current_value = float(next_point.lower_bound)
            elif scenario_mode == "Upside" and next_point.upper_bound is not None:
                next_point.current_value = float(next_point.upper_bound)
            next_point.delta_pct = safe_pct(float(next_point.current_value), last_actual)
        adjusted.append(next_point)
    return adjusted


def build_driver_breakdown_points(
    drivers: list[DriverForecast],
    scenario_mode: ScenarioMode = "Base",
) -> list[BreakdownPoint]:
    return [
        BreakdownPoint(
            label=driver.label,
            raw_label=driver.raw_label,
            current_value=driver_scenario_value(driver, scenario_mode),
            previous_value=float(driver.latest_actual),
            delta_pct=driver_scenario_delta_pct(driver, scenario_mode),
            share_pct=driver_scenario_share(driver, scenario_mode),
            previous_share_pct=float(driver.latest_share_pct),
            share_shift_pct=driver_share_shift_pct(driver, scenario_mode),
        )
        for driver in drivers
    ]
