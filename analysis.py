import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def main():
    # Set aesthetic parameters for plots
    plt.style.use('ggplot')

    # 1. Fetching the data
    file_path = r"C:\Users\user\Downloads\data.csv\data.csv"
    print(f"Loading data from {file_path}...")

    try:
        # Using unicode_escape to avoid encoding issues sometimes present in CSVs from Windows
        df = pd.read_csv(file_path, encoding='unicode_escape')
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    print(f"\nInitial Dataset Shape: {df.shape}")

    # 2. Evaluate and Clean the Data
    print("\n--- Data Cleaning Process ---")

    # a. Check for missing values
    missing_values = df.isnull().sum()
    print("Missing Values per Column:\n", missing_values[missing_values > 0])

    # b. Drop rows with missing CustomerID as they are crucial for reliable sales analysis
    initial_len = len(df)
    df = df.dropna(subset=['CustomerID'])
    print(f"Dropped {initial_len - len(df)} rows due to missing CustomerID.")

    # c. Handle duplicates
    duplicate_count = df.duplicated().sum()
    print(f"Found {duplicate_count} duplicate rows. Removing them...")
    df = df.drop_duplicates()

    # d. Convert Data Types
    print("Converting InvoiceDate to datetime objects...")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Adding a YearMonth column for monthly trend analysis
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')

    # e. Handle incorrect data (e.g., negative quantities which usually represent returns/cancellations)
    returns = len(df[df['Quantity'] <= 0])
    print(f"Found {returns} records with Quantity <= 0 (returns/cancellations). These will be excluded for overall positive sales trend analysis.")
    df_sales = df[df['Quantity'] > 0].copy()

    # f. Add a Total Price column
    df_sales['TotalPrice'] = df_sales['Quantity'] * df_sales['UnitPrice']

    print(f"\nCleaning complete. Final dataset shape for analysis: {df_sales.shape}")

    # 3. Visualize Trends and Data
    print("\n--- Generating Visualizations ---")
    
    # Create directory for saving visualizations
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)

    # Plot 1: Monthly Sales Trend (Line Chart)
    monthly_sales = df_sales.groupby('YearMonth')['TotalPrice'].sum()
    
    plt.figure(figsize=(12, 6))
    # Convert period index to string for plotting
    monthly_sales.index = monthly_sales.index.astype(str)
    monthly_sales.plot(kind='line', marker='o', color='#1f77b4', linewidth=2)
    plt.title('Monthly Sales Trend', fontsize=16)
    plt.xlabel('Month-Year', fontsize=12)
    plt.ylabel('Total Sales ($)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    trend_path = os.path.join(output_dir, 'monthly_sales_trend.png')
    plt.savefig(trend_path)
    print(f"Saved {trend_path}")

    # Plot 2: Top 10 Countries by Sales (Bar Chart)
    plt.figure(figsize=(10, 6))
    top_countries = df_sales.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(10)
    top_countries.plot(kind='bar', color='#ff7f0e')
    plt.title('Top 10 Countries by Total Sales', fontsize=16)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Total Sales ($)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    countries_path = os.path.join(output_dir, 'top_10_countries.png')
    plt.savefig(countries_path)
    print(f"Saved {countries_path}")

    # Plot 3: Top 10 Selling Products by Quantity (Bar Chart)
    plt.figure(figsize=(12, 6))
    top_products = df_sales.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
    top_products.plot(kind='bar', color='#2ca02c')
    plt.title('Top 10 Selling Products (by Quantity)', fontsize=16)
    plt.xlabel('Product Description', fontsize=12)
    plt.ylabel('Total Quantity Sold', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    products_path = os.path.join(output_dir, 'top_10_products.png')
    plt.savefig(products_path)
    print(f"Saved {products_path}")

    # Show the plots
    # plt.show()
    print("\nProcess completed successfully.")

if __name__ == "__main__":
    main()
