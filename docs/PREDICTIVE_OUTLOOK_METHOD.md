# Predictive Outlook Method

## Why this page exists

The predictive page is designed as a BI planning surface, not as a black-box machine learning demo.
It answers three questions:

1. What is the likely next-month revenue baseline?
2. Which categories are most likely to drive that result?
3. Where is current revenue already exposed to customer-risk signals?

## Forecasting choice

The implementation uses Holt linear exponential smoothing on monthly history.

Why:

- The selected dashboard window usually provides roughly 12 to 24 months of history.
- That is enough for a practical trend model, but too thin to justify heavy seasonal modeling with confidence.
- In BI, a transparent directional baseline is usually more defensible than a more complex model that is harder to explain.

The model therefore uses:

- monthly aggregation
- one-step fitted baseline
- next 3 months forecast
- approximate 95 percent interval derived from residual volatility
- expanding-window one-step MAPE for a simple accuracy read

## Business guidance layer

The page does not stop at forecast values.
It adds a driver watchlist with:

- latest closed month revenue
- next-month forecast
- forecast delta versus latest closed month
- forecast share
- recent growth
- volatility
- recommended action

Action labels are rule-based and intentionally simple:

- Defend core demand
- Protect core and support supply
- Accelerate momentum
- Investigate softness
- Monitor volatility
- Maintain watch

This keeps the page explainable and operational.

## References

- Forecasting: Principles and Practice, Hyndman and Athanasopoulos
  - https://otexts.com/fpp2/
- StatsForecast by Nixtla
  - https://github.com/Nixtla/statsforecast
- skforecast
  - https://github.com/skforecast/skforecast
- Darts
  - https://github.com/unit8co/darts

## Why those libraries were not added now

They are strong references, especially StatsForecast, but they are not necessary for the current dashboard stage.

Reasons:

- the project already has enough dependencies
- the BI requirement here is transparency and speed, not model breadth
- the selected Holt implementation is small, auditable, and fast enough for the current dataset

A future iteration can upgrade this page with:

- seasonal statistical models when history is longer
- change-point detection
- scenario planning by category
- customer lifetime value or churn probability inputs
