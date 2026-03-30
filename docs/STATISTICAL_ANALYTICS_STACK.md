# Statistical Analytics Layer

This project now uses business-statistical analyses that are defensible with the current ecommerce model and do not require heavy external ML dependencies.

## Implemented in the dashboard

- `Sales`: Pareto analysis by category with cumulative share and ABC classification.
- `Products`: Pareto analysis by product with ABC classification.
- `Customers`: RFM segmentation for value and retention quality.
- `Revenue`: robust anomaly detection on the period trend using a trailing median/MAD baseline.

## Why these methods

These methods improve business reading without forcing black-box models:

- `Pareto / ABC`: isolates which categories or products drive most revenue and whether the business is overly dependent on a narrow set of items.
- `RFM`: separates high-value, loyal, at-risk and hibernating customers using recency, frequency and monetary contribution.
- `Robust anomaly detection`: flags statistically unusual periods without overfitting; useful for executive review and investigation.

## Libraries evaluated

These were reviewed as possible accelerators or future upgrades:

- `PyOD`: broad anomaly detection toolbox for richer outlier models.
  - https://github.com/yzhao062/pyod
- `ruptures`: change-point detection library for structural breaks in time series.
  - https://github.com/deepcharles/ruptures
- `lifetimes`: customer lifetime value and probabilistic retention modeling.
  - https://github.com/CamDavidsonPilon/lifetimes
- `scikit-learn IsolationForest`: useful when the project evolves into multivariate anomaly detection.
  - https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html

## Why they were not added now

The current dashboard only needs univariate and business-readable analyses. Adding heavier ML dependencies now would increase stack complexity without meaningfully improving the decision layer.

The implemented approach keeps the analytics explainable, testable and aligned with the portfolio goal.
