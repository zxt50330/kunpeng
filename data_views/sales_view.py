import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = psycopg2.connect(host="localhost", database="kunpeng", user="", password="")

# Define the query to get monthly sales data by sku
query = '''WITH monthly_sales AS (
  SELECT to_char(date_trunc('month', date), 'YYYY-MM') AS month,
         sku,
         SUM(total_quantity) AS monthly_quantity
  FROM sales_daily_quantity
  GROUP BY month, sku
)
SELECT month, sku, monthly_quantity
FROM monthly_sales
WHERE sku IN (
  SELECT sku
  FROM monthly_sales
  GROUP BY sku
  ORDER BY SUM(monthly_quantity) DESC
  LIMIT 10
)
ORDER BY month, monthly_quantity DESC;'''

# Execute the query and fetch the results
cur = conn.cursor()
cur.execute(query)
rows = cur.fetchall()

# Close the cursor and the database connection
cur.close()
conn.close()

# Convert the results to a pandas DataFrame
df = pd.DataFrame(rows, columns=["month", "sku", "monthly_sales"])
df['monthly_sales'] = df['monthly_sales'].apply(lambda x: float(x))
# Pivot the DataFrame to get monthly sales data by SKU
pivoted_df = df.pivot(index="month", columns="sku", values="monthly_sales")

# Calculate the total sales and sort the columns by descending order
total_sales = pivoted_df.sum()
sorted_columns = total_sales.sort_values(ascending=False).index

# Plot the monthly sales for each SKU
fig, ax = plt.subplots(figsize=(10, 6))
pivoted_df[sorted_columns].plot(kind="bar", ax=ax)
ax.set_xlabel("Month")
ax.set_ylabel("Sales")
ax.set_title("Monthly Sales by SKU")
plt.show()
