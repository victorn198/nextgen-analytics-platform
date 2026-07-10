# Power BI report

`OpenSourceLandscape/` is a source-controlled PBIP project generated from the
report specification and PostgreSQL semantic model.

The report has three business-facing pages: `Executive Overview`, `Market
Demand` and `Opportunity Queue`. The lateral navigator is a native Power BI
page navigator, so it remains clickable when the PBIP is opened in Desktop.

```powershell
node ..\scripts\generate_pbip.mjs
powerbi-report-author validate OpenSourceLandscape\OpenSourceLandscape.Report
```

Open `OpenSourceLandscape/OpenSourceLandscape.pbip`, refresh the model and use
the local PostgreSQL credentials configured in the project `.env` file.
