"""
generate_data.py
Creates data/sales_raw.csv - a simulated retail sales dataset (2024-2025).

The file is deliberately a little messy (duplicates, missing values,
inconsistent text) so the cleaning step in sales_analysis.py has real work to do.
Run:  python generate_data.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# ---------- master data ----------
# product: (category, price in INR, cost as share of price, popularity weight)
products = {
    "Wireless Mouse":        ("Electronics",     799, 0.58, 9),
    "Bluetooth Headphones":  ("Electronics",    2499, 0.62, 6),
    "USB-C Charger":         ("Electronics",    1299, 0.55, 8),
    "Power Bank":            ("Electronics",    1899, 0.60, 7),
    "Smart Watch":           ("Electronics",    4999, 0.68, 3),
    "Webcam":                ("Electronics",    2999, 0.64, 3),
    "Office Chair":          ("Furniture",      6999, 0.72, 2),
    "Study Table":           ("Furniture",      5499, 0.70, 2),
    "Bookshelf":             ("Furniture",      4299, 0.69, 2),
    "Desk Lamp":             ("Furniture",       899, 0.57, 6),
    "Notebook Pack":         ("Office Supplies", 349, 0.50, 14),
    "Gel Pen Box":           ("Office Supplies", 199, 0.45, 16),
    "Stapler":               ("Office Supplies", 249, 0.48, 8),
    "Desk Organizer":        ("Office Supplies", 599, 0.52, 7),
    "Whiteboard":            ("Office Supplies",1499, 0.60, 3),
    "Laptop Backpack":       ("Accessories",    1799, 0.55, 6),
    "Water Bottle":          ("Accessories",     499, 0.47, 10),
    "Phone Case":            ("Accessories",     399, 0.42, 12),
}
names = list(products)
pop = np.array([products[p][3] for p in names], dtype=float)
pop /= pop.sum()

cities = {
    "Mumbai": "West", "Pune": "West", "Ahmedabad": "West",
    "Delhi": "North", "Bengaluru": "South", "Chennai": "South",
    "Hyderabad": "South", "Kolkata": "East",
}
city_names = list(cities)
city_w = np.array([22, 10, 8, 20, 17, 8, 10, 5], dtype=float)
city_w /= city_w.sum()

# ---------- order dates (festive season + weekends + yearly growth) ----------
days = pd.date_range("2024-01-01", "2025-12-31", freq="D")
month_w = {1: .85, 2: .85, 3: .95, 4: .95, 5: 1.0, 6: .9,
           7: .9, 8: 1.0, 9: 1.05, 10: 1.35, 11: 1.45, 12: 1.2}
w = []
for d in days:
    x = month_w[d.month]
    x *= 1.25 if d.dayofweek >= 5 else 1.0
    x *= 1.18 if d.year == 2025 else 1.0
    w.append(x)
w = np.array(w); w /= w.sum()

N = 10600
order_dates = rng.choice(days, size=N, p=w)
order_dates = pd.to_datetime(np.sort(order_dates))

prod_idx = rng.choice(len(names), size=N, p=pop)
prod = [names[i] for i in prod_idx]
cat = [products[p][0] for p in prod]
price = np.array([products[p][1] for p in prod], dtype=float)
cost = price * np.array([products[p][2] for p in prod])

qty = rng.choice([1, 2, 3, 4, 5], size=N, p=[.55, .25, .1, .06, .04])
discount = rng.choice([0, .05, .10, .15, .20, .30], size=N,
                      p=[.40, .15, .20, .12, .09, .04])
city = rng.choice(city_names, size=N, p=city_w)
region = [cities[c] for c in city]
cust = rng.integers(1001, 2800, size=N)

sales = np.round(qty * price * (1 - discount), 2)
profit = np.round(sales - qty * cost, 2)

df = pd.DataFrame({
    "order_id": [f"ORD{100000 + i}" for i in range(N)],
    "order_date": order_dates.strftime("%Y-%m-%d"),
    "customer_id": [f"C{c}" for c in cust],
    "city": city, "region": region,
    "category": cat, "product": prod,
    "quantity": qty, "unit_price": price,
    "discount": discount, "sales": sales, "profit": profit,
})

# ---------- make it realistically messy ----------
# 1) inconsistent text in category
idx = rng.choice(N, 180, replace=False)
df.loc[idx[:90], "category"] = df.loc[idx[:90], "category"].str.lower()
df.loc[idx[90:], "category"] = " " + df.loc[idx[90:], "category"] + " "
# 2) missing region / discount
df.loc[rng.choice(N, 150, replace=False), "region"] = np.nan
df.loc[rng.choice(N, 100, replace=False), "discount"] = np.nan
# 3) duplicate rows
dups = df.sample(120, random_state=1)
df = pd.concat([df, dups]).sample(frac=1, random_state=7).reset_index(drop=True)

df.to_csv("data/sales_raw.csv", index=False)
print("saved data/sales_raw.csv", df.shape)
