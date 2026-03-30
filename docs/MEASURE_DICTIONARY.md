# Measure Dictionary (Power BI)

Updated: 2026-02-22
Model: `power_bi/sales_dashboard.pbix`
Measure table: `Medidas`

## 03 Sales - Existing Core

| Measure | Formula (summary) | Purpose |
|---|---|---|
| `Sales Amount` | `SUM(fct_sales[SALES_AMOUNT])` | Total revenue in current filter context. |
| `Orders Count` | `DISTINCTCOUNT(fct_sales[ORDER_ID])` | Number of unique orders. |
| `Customers Count` | `DISTINCTCOUNT(fct_sales[CUSTOMER_ID])` | Number of unique customers. |
| `Products Count` | `DISTINCTCOUNT(fct_sales[PRODUCT_ID])` | Number of unique products sold. |
| `Average Ticket` | `DIVIDE([Sales Amount],[Orders Count])` | Average revenue per order. |
| `Total Quantity` | `SUM(fct_sales[QUANTITY])` | Total units sold. |

## 03 Sales - New Measures for Pending Pages

### Sales Overview

| Measure | Formula (summary) | Purpose |
|---|---|---|
| `Sales Amount Previous Period` | `DATEADD(ORDER_DATE,-1,MONTH)` over `[Sales Amount]` | Previous month sales benchmark. |
| `Sales Amount MoM %` | `(Current - Previous) / Previous` | Month-over-month sales growth. |
| `Orders Previous Period` | `DATEADD(ORDER_DATE,-1,MONTH)` over `[Orders Count]` | Previous month order benchmark. |
| `Orders MoM %` | `(Current - Previous) / Previous` | Month-over-month order growth. |
| `Average Items Per Order` | `DIVIDE([Total Quantity],[Orders Count])` | Basket size proxy. |

### Sales Overview (Current KPI Cards - 2026-02-22)

| Measure | Formula (summary) | Purpose |
|---|---|---|
| `Sales 30D` | Sales in last 30 days anchored at last date with data in filter context | Current rolling sales window. |
| `Sales Previous 30D` | Sales in 30 days before current rolling window | Baseline for short-term growth. |
| `Sales 30D Growth %` | `(Sales 30D - Sales Previous 30D) / Sales Previous 30D` | Stable growth KPI for cards (avoids blank on wide date slicers). |
| `Orders 30D` | Orders in last 30 days anchored at last date with data in filter context | Current rolling demand window. |
| `Orders Previous 30D` | Orders in previous 30-day window | Baseline for order growth. |
| `Orders 30D Growth %` | `(Orders 30D - Orders Previous 30D) / Orders Previous 30D` | Stable order growth KPI for cards. |

### Revenue Trends

| Measure | Formula (summary) | Purpose |
|---|---|---|
| `Sales Amount MTD` | `DATESMTD(ORDER_DATE)` over `[Sales Amount]` | Month-to-date revenue. |
| `Sales Amount QTD` | `DATESQTD(ORDER_DATE)` over `[Sales Amount]` | Quarter-to-date revenue. |
| `Sales Amount YTD` | `DATESYTD(ORDER_DATE)` over `[Sales Amount]` | Year-to-date revenue. |
| `Sales Amount Last 30 Days` | `DATESINPERIOD(...,-30,DAY)` | Rolling 30-day revenue. |
| `Sales Amount Last 90 Days` | `DATESINPERIOD(...,-90,DAY)` | Rolling 90-day revenue. |
| `Sales Amount 7D Moving Avg` | `AVERAGEX` over last 7 days | Smoothed short-term trend. |

### Customer Segmentation

| Measure | Formula (summary) | Purpose |
|---|---|---|
| `Customers Active Last 30D` | Distinct customers in last 30 days | Recent active base. |
| `Customers Active Last 90D` | Distinct customers in last 90 days | Broader active base. |
| `Repeat Customers Count` | Customers with more than 1 order | Loyalty/repeat behavior. |
| `Repeat Customer Rate %` | `Repeat / Total customers` | Repeat penetration ratio. |
| `New Customers Count` | First purchase date inside filter window | Acquisition in period. |
| `Returning Customers Count` | `Total - New` | Retention in period. |

### Product Performance

| Measure | Formula (summary) | Purpose |
|---|---|---|
| `Products Sold (Distinct)` | `DISTINCTCOUNT(fct_sales[PRODUCT_ID])` | Product breadth sold. |
| `Average Unit Price` | `DIVIDE([Sales Amount],[Total Quantity])` | Realized average selling price. |
| `Top Product Sales Amount` | `MAXX(VALUES(product), [Sales Amount])` | Revenue of leading product. |
| `Top Product Name` | `TOPN(1, product by revenue)` | Name of best-selling product. |
| `Top Category Sales Amount` | `MAXX(VALUES(category), [Sales Amount])` | Revenue of best category. |
| `Sales Share %` | `[Sales Amount] / CALCULATE([Sales Amount], ALL(dim_product))` | Product/category participation. |

## Usage Notes

- Current standard uses `dCalendar` as date dimension for time-intelligence.
- For robust visuals, prefer anchors based on "last date with data in current filter context" instead of max calendar date.
- Keep `YearMonth` sorted by `YearMonthSort` for monthly visuals.
- Keep `Display Folder` organization in Power BI Desktop:
  - `01 Ops KPIs`
  - `02 Data Quality`
  - `03 Sales`
