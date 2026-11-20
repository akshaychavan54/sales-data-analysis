# Sales Data Analysis (Python)

Analysis of about 10,600 retail sales orders (Jan 2024 - Dec 2025) using Python. I cleaned the raw file, worked out the main KPIs, and made 14 charts to understand which products, categories, regions and months drive sales and profit.

**Tools:** Python, Pandas, NumPy, Matplotlib, Seaborn

## About the data
The dataset is simulated. `generate_data.py` creates `data/sales_raw.csv` with 18 products in 4 categories, 8 Indian cities, festive-season spikes and weekend peaks. I made the file messy on purpose (duplicates, missing values, inconsistent text) so the cleaning step is a real part of the project. If you want to use a real dataset, replace `sales_raw.csv` with a file that has the same columns and the script will work as it is.

| Column | Meaning |
|---|---|
| order_id, order_date, customer_id | order details |
| city, region | where the order came from |
| category, product | what was sold |
| quantity, unit_price, discount | order values |
| sales, profit | amount after discount, and profit |

## What I did
1. **Inspected** the raw data: 10,720 rows, 120 duplicate rows, 151 missing regions, 100 missing discounts.
2. **Cleaned** it:
   - removed the 120 duplicate rows
   - fixed category text (` furniture ` -> `Furniture`)
   - filled missing regions using the city (each city belongs to one region)
   - recovered missing discounts from `sales = quantity x price x (1 - discount)`
   - checked that sales matched this formula on every row after cleaning
3. **Added columns**: year, month, quarter, day of week, profit margin.
4. **Analysed** sales, profit, products, categories, regions, time trends and discounts.
5. **Made 14 charts** (saved in `charts/`).

## Key findings
- Total sales were about **Rs 2.09 crore** with **Rs 71.6 lakh profit** (34.2% margin). Average order value was Rs 1,972.
- Sales grew **16.1%** from 2024 to 2025.
- **October and November** together bring 22% of all sales (festive season). Oct 2025 was the best month (Rs 13.3 lakh), May 2024 the weakest (Rs 6.4 lakh).
- Highest revenue products: **Office Chair, Bluetooth Headphones, Smart Watch**. Most units sold: **Gel Pen Box, Notebook Pack, Phone Case**. Cheap items sell in volume, expensive ones bring the revenue.
- **Electronics** is 46% of sales but only has a 33% margin. **Accessories** (46%) and **Office Supplies** (44%) have the best margins, and **Furniture** the lowest (25%).
- **Discounts hurt profit**: average margin falls from 47% (no discount) to 25% at a 30% discount, and a few orders at 30% off actually lose money.
- Weekends (2 of 7 days) bring about 33% of sales.
- **West** (39%) and **South** (34%) are the biggest regions. East is only 5% of sales and looks like a growth gap.

## Suggestions that come out of this
- Stock up on Electronics and Office Supplies before October.
- Avoid 20-30% discounts on Furniture and Electronics, where margins are already thin.
- Plan marketing around weekends and the festive months.

## Charts
| | |
|---|---|
| 01 Monthly sales trend | 08 Sales by region |
| 02 2024 vs 2025 by month | 09 Sales by city |
| 03 Top 10 products by revenue | 10 Quarterly sales by category |
| 04 Top 10 products by units | 11 Sales by day of week |
| 05 Sales by category | 12 Profit margin by discount |
| 06 Category share | 13 Order value distribution |
| 07 Profit by category | 14 Correlation heatmap |

## How to run
```bash
pip install -r requirements.txt
python generate_data.py      # creates data/sales_raw.csv
python sales_analysis.py     # cleans data, prints insights, saves charts/ and data/sales_clean.csv
```

## Folder structure
```
sales-data-analysis/
  data/            sales_raw.csv, sales_clean.csv
  charts/          14 charts (png)
  generate_data.py
  sales_analysis.py
  output_summary.txt   (console output of one run)
  requirements.txt
```
