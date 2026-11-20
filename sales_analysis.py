"""
Sales Data Analysis
Tools: Python, Pandas, NumPy, Matplotlib, Seaborn

Steps: load -> inspect -> clean -> feature engineering -> analysis + charts -> insights
Run:   python sales_analysis.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import seaborn as sns

os.makedirs("charts", exist_ok=True)
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams.update({"figure.dpi": 110, "axes.titleweight": "bold", "axes.titlesize": 13})

lakh = mtick.FuncFormatter(lambda x, _: f"₹{x / 1e5:,.0f}L")   # axis labels in lakhs


def save(name):
    plt.tight_layout()
    plt.savefig(f"charts/{name}.png", dpi=130)
    plt.close()


# ------------------------------------------------------------------ 1. LOAD
df = pd.read_csv("data/sales_raw.csv")
print("=== RAW DATA ===")
print("Shape:", df.shape)
print("Missing values:\n", df.isna().sum()[df.isna().sum() > 0])
print("Duplicate rows:", df.duplicated().sum())

# ---------------------------------------------------------------- 2. CLEAN
df = df.drop_duplicates()                                    # exact duplicate rows
df["category"] = df["category"].str.strip().str.title()      # ' furniture ' -> 'Furniture'

# region is missing for some rows, but city tells us the region
city_to_region = (df.dropna(subset=["region"])
                    .drop_duplicates("city").set_index("city")["region"])
df["region"] = df["region"].fillna(df["city"].map(city_to_region))

# missing discount -> work it back from the sales amount (sales = qty * price * (1 - discount))
implied = 1 - df["sales"] / (df["quantity"] * df["unit_price"])
df["discount"] = df["discount"].fillna(implied.round(2))

df["order_date"] = pd.to_datetime(df["order_date"])
df = df.sort_values("order_date").reset_index(drop=True)

# sanity check: sales should equal qty * price * (1 - discount)
expected = np.round(df["quantity"] * df["unit_price"] * (1 - df["discount"]), 2)
mismatch = (~np.isclose(df["sales"], expected)).sum()
print(f"\n=== AFTER CLEANING ===\nRows: {len(df):,} | Nulls left: {df.isna().sum().sum()} "
      f"| sales mismatches: {mismatch}")

# --------------------------------------------------- 3. FEATURE ENGINEERING
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month
df["month_name"] = df["order_date"].dt.strftime("%b")
df["quarter"] = df["order_date"].dt.quarter
df["day_name"] = df["order_date"].dt.day_name()
df["year_month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
df["profit_margin"] = np.where(df["sales"] > 0, df["profit"] / df["sales"] * 100, 0)
df.to_csv("data/sales_clean.csv", index=False)

# --------------------------------------------------------------- 4. KPIs
total_sales, total_profit = df["sales"].sum(), df["profit"].sum()
print("\n=== KPIs ===")
print(f"Total orders      : {len(df):,}")
print(f"Total sales       : ₹{total_sales:,.0f}")
print(f"Total profit      : ₹{total_profit:,.0f}  ({total_profit / total_sales:.1%} margin)")
print(f"Avg order value   : ₹{df['sales'].mean():,.0f}")
print(f"Loss-making orders: {(df['profit'] < 0).sum():,} ({(df['profit'] < 0).mean():.1%})")

# ------------------------------------------------------------ 5. CHARTS
# 1. Monthly sales trend
monthly = df.groupby("year_month")["sales"].sum()
plt.figure(figsize=(11, 4.5))
plt.plot(monthly.index, monthly.values, marker="o", lw=2)
plt.gca().yaxis.set_major_formatter(lakh)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.title("Monthly Sales Trend (2024-2025)"); plt.xlabel(""); plt.ylabel("Sales")
save("01_monthly_sales_trend")

# 2. Year-over-year comparison by month
mm = df.pivot_table(index="month", columns="year", values="sales", aggfunc="sum")
mm.index = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
mm.plot(kind="bar", figsize=(11, 4.5), width=.8)
plt.gca().yaxis.set_major_formatter(lakh)
plt.title("Month-wise Sales: 2024 vs 2025"); plt.xlabel(""); plt.ylabel("Sales"); plt.xticks(rotation=0)
save("02_yoy_monthly_comparison")

# 3. Top 10 products by revenue
top_rev = df.groupby("product")["sales"].sum().nlargest(10).sort_values()
plt.figure(figsize=(9, 5))
top_rev.plot(kind="barh", color=sns.color_palette("deep")[0])
plt.gca().xaxis.set_major_formatter(lakh)
plt.title("Top 10 Products by Revenue"); plt.xlabel("Sales"); plt.ylabel("")
save("03_top10_products_revenue")

# 4. Top 10 products by units sold
top_units = df.groupby("product")["quantity"].sum().nlargest(10).sort_values()
plt.figure(figsize=(9, 5))
top_units.plot(kind="barh", color=sns.color_palette("deep")[2])
plt.title("Top 10 Best-Selling Products (Units)"); plt.xlabel("Units sold"); plt.ylabel("")
save("04_top10_products_units")

# 5. Sales by category
cat_sales = df.groupby("category")["sales"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 4.5))
sns.barplot(x=cat_sales.index, y=cat_sales.values)
plt.gca().yaxis.set_major_formatter(lakh)
plt.title("Sales by Category"); plt.xlabel(""); plt.ylabel("Sales")
save("05_sales_by_category")

# 6. Category share (donut)
plt.figure(figsize=(6.5, 6.5))
plt.pie(cat_sales, labels=cat_sales.index, autopct="%1.1f%%", startangle=90,
        wedgeprops={"width": .45, "edgecolor": "white"})
plt.title("Revenue Share by Category")
save("06_category_share")

# 7. Profit by category
cat_profit = df.groupby("category")["profit"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 4.5))
sns.barplot(x=cat_profit.index, y=cat_profit.values)
plt.gca().yaxis.set_major_formatter(lakh)
plt.title("Profit by Category"); plt.xlabel(""); plt.ylabel("Profit")
save("07_profit_by_category")

# 8. Sales by region
reg = df.groupby("region")["sales"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 4.5))
sns.barplot(x=reg.index, y=reg.values)
plt.gca().yaxis.set_major_formatter(lakh)
plt.title("Sales by Region"); plt.xlabel(""); plt.ylabel("Sales")
save("08_sales_by_region")

# 9. Sales by city
city = df.groupby("city")["sales"].sum().sort_values()
plt.figure(figsize=(9, 5))
city.plot(kind="barh")
plt.gca().xaxis.set_major_formatter(lakh)
plt.title("Sales by City"); plt.xlabel("Sales"); plt.ylabel("")
save("09_sales_by_city")

# 10. Quarterly sales by category (stacked)
q = df.pivot_table(index=["year", "quarter"], columns="category", values="sales", aggfunc="sum")
q.index = [f"{y} Q{k}" for y, k in q.index]
q.plot(kind="bar", stacked=True, figsize=(11, 5))
plt.gca().yaxis.set_major_formatter(lakh)
plt.title("Quarterly Sales by Category"); plt.xlabel(""); plt.ylabel("Sales"); plt.xticks(rotation=30)
save("10_quarterly_sales_by_category")

# 11. Sales by day of week
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dow = df.groupby("day_name")["sales"].sum().reindex(order)
plt.figure(figsize=(9, 4.5))
sns.barplot(x=dow.index, y=dow.values)
plt.gca().yaxis.set_major_formatter(lakh)
plt.title("Sales by Day of Week"); plt.xlabel(""); plt.ylabel("Sales"); plt.xticks(rotation=20)
save("11_sales_by_weekday")

# 12. Discount vs profit margin
plt.figure(figsize=(8, 4.5))
sns.boxplot(data=df, x=(df["discount"] * 100).astype(int), y="profit_margin")
plt.axhline(0, color="red", ls="--", lw=1)
plt.title("Profit Margin by Discount Level"); plt.xlabel("Discount (%)"); plt.ylabel("Profit margin (%)")
save("12_discount_vs_margin")

# 13. Order value distribution
plt.figure(figsize=(9, 4.5))
sns.histplot(df["sales"], bins=40, kde=True)
plt.title("Distribution of Order Value"); plt.xlabel("Order value (₹)")
save("13_order_value_distribution")

# 14. Correlation heatmap
plt.figure(figsize=(7, 5.5))
sns.heatmap(df[["quantity", "unit_price", "discount", "sales", "profit"]].corr(),
            annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation Between Numeric Columns")
save("14_correlation_heatmap")

# ------------------------------------------------------------ 6. INSIGHTS
print("\n=== KEY INSIGHTS ===")
print("Top 5 products by revenue:\n", df.groupby("product")["sales"].sum().nlargest(5).round(0))
print("\nTop 5 products by units:\n", df.groupby("product")["quantity"].sum().nlargest(5))
print("\nCategory share of sales (%):\n", (cat_sales / cat_sales.sum() * 100).round(1))
print("\nCategory profit margin (%):\n",
      (df.groupby("category")["profit"].sum() / df.groupby("category")["sales"].sum() * 100).round(1))
best, worst = monthly.idxmax(), monthly.idxmin()
print(f"\nBest month : {best:%b %Y} (₹{monthly.max():,.0f})")
print(f"Weakest    : {worst:%b %Y} (₹{monthly.min():,.0f})")
yr = df.groupby("year")["sales"].sum()
print(f"\nYearly sales: {yr.round(0).to_dict()} | growth 2025 vs 2024: {yr[2025] / yr[2024] - 1:.1%}")
fest = df[df["month"].isin([10, 11])]["sales"].sum() / total_sales
print(f"Oct+Nov share of total sales: {fest:.1%}")
we = df[df["day_name"].isin(["Saturday", "Sunday"])]
print(f"Weekend share of sales: {we['sales'].sum() / total_sales:.1%} (2 of 7 days)")
print("\nAvg profit margin by discount %:\n",
      df.groupby((df['discount'] * 100).astype(int))["profit_margin"].mean().round(1))
print("\nRegion share (%):\n", (reg / reg.sum() * 100).round(1))
