import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set a premium aesthetic theme
sns.set_theme(style="darkgrid", rc={"axes.facecolor": "#f9f9f9", "figure.facecolor": "#f0f0f0"})

def load_and_clean_data(file_path):
    if not os.path.exists(file_path):
        print(f"[WARNING] File not found at {file_path}.")
        print("[INFO] Generating mock sales data for demonstration purposes...")
        
        # Generate dummy data
        np.random.seed(42)
        dates = pd.date_range(start="2023-01-01", periods=365, freq="D")
        regions = ['EMEA', 'APAC', 'Japan', 'Americas']
        categories = ['Classic Cars', 'Vintage Cars', 'Motorcycles', 'Trucks and Buses', 'Planes']
        products = [f'Prod_{i}' for i in range(1, 15)]
        
        df = pd.DataFrame({
            'ORDERDATE': np.random.choice(dates, 1000),
            'SALES': np.random.uniform(500, 15000, 1000),
            'TERRITORY': np.random.choice(regions, 1000, p=[0.4, 0.2, 0.1, 0.3]),
            'PRODUCTLINE': np.random.choice(categories, 1000),
            'PRODUCTCODE': np.random.choice(products, 1000),
            'QUANTITYORDERED': np.random.randint(10, 50, 1000)
        })
        date_col = 'ORDERDATE'
        df['YearMonth'] = df[date_col].dt.to_period('M')
        return df, date_col
        
    # Load dataset
    df = pd.read_csv(file_path, encoding='ISO-8859-1')
    
    # Clean data
    df.drop_duplicates(inplace=True)
    
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna('Unknown')
                
    # Datetime conversion
    date_col = next((col for col in ['ORDERDATE', 'Order Date', 'Date', 'date'] if col in df.columns), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df['YearMonth'] = df[date_col].dt.to_period('M')
        
    return df, date_col

def create_dashboard():
    file_path = r"C:\Users\user\Downloads\archive (1)\sales_data_sample.csv"
    data = load_and_clean_data(file_path)
    
    if data is None:
        return
    df, date_col = data
    
    # Identify key columns
    sales_col = next((c for c in ['SALES', 'Sales', 'sales', 'Revenue'] if c in df.columns), None)
    region_col = next((c for c in ['TERRITORY', 'REGION', 'Country', 'COUNTRY'] if c in df.columns), None)
    product_col = next((c for c in ['PRODUCTLINE', 'Category', 'CATEGORY'] if c in df.columns), None)
    item_col = next((c for c in ['PRODUCTCODE', 'Product', 'PRODUCTNAME'] if c in df.columns), None)

    if not sales_col:
        print("[ERROR] Could not find a 'Sales' column. Dashboard cannot proceed.")
        return

    # Calculate KPIs
    total_sales = df[sales_col].sum()
    total_orders = len(df)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    qty_col = next((c for c in ['QUANTITYORDERED', 'Quantity', 'QTY'] if c in df.columns), None)
    total_items = df[qty_col].sum() if qty_col else "N/A"

    # Set up the Dashboard Layout using GridSpec
    fig = plt.figure(figsize=(10, 7))
    fig.suptitle("Executive Sales Data Dashboard", fontsize=14, fontweight='bold', y=0.48, color='#333333')
    
    # 3 rows, 2 columns. The top row is small and just for text/KPIs.
    gs = plt.GridSpec(3, 2, height_ratios=[0.25, 1.5,1.5], hspace=0.35, wspace=0.25)
    
    # --- ROW 1: KPIs ---
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.axis('off') # Hide axes
    
    kpi_text = (
        f"Total Revenue: ${total_sales:,.2f}    |    "
        f"Total Orders: {total_orders:,}    |    "
        f"Avg Order Value: ${avg_order_value:,.2f}    |    "
        f"Total Items Sold: {total_items:,}"
    )
    
    # Add KPI text in the center
    ax_kpi.text(0.5, 0.5, kpi_text, fontsize=20, ha='center', va='center', 
                bbox=dict(facecolor='#ffffff', edgecolor='#dddddd', boxstyle='round,pad=0.8'),
                fontweight='bold', color='#1f77b4')

    # --- ROW 2 / COL 1: Sales by Region ---
    ax_region = fig.add_subplot(gs[1, 0])
    if region_col:
        sales_by_region = df.groupby(region_col)[sales_col].sum().sort_values(ascending=False)
        sns.barplot(x=sales_by_region.values, y=sales_by_region.index, hue=sales_by_region.index, 
                    palette='viridis', legend=False, ax=ax_region)
        ax_region.set_title('Total Sales by Region', fontsize=18, fontweight='bold', pad=15)
        ax_region.set_xlabel('Total Sales ($)', fontsize=14)
        ax_region.set_ylabel('Region', fontsize=14)
        ax_region.tick_params(labelsize=12)

    # --- ROW 2 / COL 2: Sales by Product Category ---
    ax_cat = fig.add_subplot(gs[1, 1])
    if product_col:
        sales_by_cat = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False)
        colors = sns.color_palette('pastel')[0:len(sales_by_cat)]
        wedges, texts, autotexts = ax_cat.pie(
            sales_by_cat.values, 
            labels=sales_by_cat.index, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=colors,
            textprops={'fontsize': 12},
            wedgeprops={'edgecolor': 'w', 'linewidth': 1.5}
        )
        # Make percentages bold
        plt.setp(autotexts, size=12, weight="bold")
        ax_cat.set_title('Sales Distribution by Product Category', fontsize=18, fontweight='bold', pad=15)

    # --- ROW 3 / COL 1: Monthly Sales Trend ---
    ax_trend = fig.add_subplot(gs[2, 0])
    if date_col and 'YearMonth' in df.columns:
        monthly_sales = df.groupby('YearMonth')[sales_col].sum()
        monthly_sales.index = monthly_sales.index.astype(str)
        
        ax_trend.plot(monthly_sales.index, monthly_sales.values, marker='o', color='#d62728', 
                      linestyle='-', linewidth=2.5, markersize=8)
        ax_trend.set_title('Monthly Sales Trend', fontsize=18, fontweight='bold', pad=15)
        ax_trend.set_xlabel('Month-Year', fontsize=14)
        ax_trend.set_ylabel('Total Sales ($)', fontsize=14)
        ax_trend.tick_params(axis='x', rotation=45, labelsize=10)
        ax_trend.tick_params(axis='y', labelsize=12)
        ax_trend.grid(True, linestyle='--', alpha=0.7)

    # --- ROW 3 / COL 2: Top 10 Products ---
    ax_top = fig.add_subplot(gs[2, 1])
    if item_col:
        top_products = df.groupby(item_col)[sales_col].sum().sort_values(ascending=False).head(10)
        sns.barplot(x=top_products.values, y=top_products.index, hue=top_products.index, 
                    palette='magma', legend=False, ax=ax_top)
        ax_top.set_title('Top 10 Products by Revenue', fontsize=18, fontweight='bold', pad=15)
        ax_top.set_xlabel('Revenue ($)', fontsize=14)
        ax_top.set_ylabel('Product', fontsize=14)
        ax_top.tick_params(labelsize=12)

    # Save and Show
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, "executive_dashboard.png")
    
    # Adjust layout so it doesn't get cut off
    plt.tight_layout()
    # But GridSpec needs a slight adjustment for the suptitle
    fig.subplots_adjust(top=0.45) 
    
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    print(f"[SUCCESS] Dashboard generated and saved to '{plot_path}'")
    
    # Display the dashboard
    plt.show()

if __name__ == "__main__":
    create_dashboard()
