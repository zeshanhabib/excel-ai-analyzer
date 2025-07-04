import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sales_data(num_records: int = 1000) -> pd.DataFrame:
    """Generate sample sales data as DataFrame."""
    np.random.seed(42)
    
    # Products and regions
    products = ['Laptop', 'Desktop', 'Monitor', 'Keyboard', 'Mouse', 'Headphones', 'Webcam', 'Tablet']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
    sales_reps = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Martinez']
    
    # Generate date range
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    data = []
    for _ in range(num_records):
        product = np.random.choice(products)
        region = np.random.choice(regions)
        sales_rep = np.random.choice(sales_reps)
        date = dates[np.random.randint(0, len(dates))]
        
        # Product-specific pricing
        base_prices = {
            'Laptop': 800, 'Desktop': 600, 'Monitor': 200, 'Keyboard': 50,
            'Mouse': 30, 'Headphones': 80, 'Webcam': 40, 'Tablet': 300
        }
        
        price = base_prices[product] * np.random.uniform(0.8, 1.2)
        quantity = np.random.poisson(3) + 1
        revenue = price * quantity
        
        # Add seasonal trends
        month = date.month
        if month in [11, 12]:  # Holiday season
            revenue *= np.random.uniform(1.2, 1.5)
        elif month in [6, 7]:  # Summer
            revenue *= np.random.uniform(0.8, 1.1)
        
        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Product': product,
            'Region': region,
            'Sales_Rep': sales_rep,
            'Quantity': quantity,
            'Unit_Price': round(price, 2),
            'Revenue': round(revenue, 2),
            'Profit_Margin': round(np.random.uniform(0.1, 0.3), 2),
            'Customer_Satisfaction': round(np.random.uniform(3.5, 5.0), 1)
        })
    
    return pd.DataFrame(data)

def generate_employee_data(num_records: int = 500) -> pd.DataFrame:
    """Generate sample employee data as DataFrame."""
    np.random.seed(43)
    
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance']
    positions = ['Junior', 'Senior', 'Lead', 'Manager', 'Director']
    locations = ['New York', 'San Francisco', 'London', 'Toronto', 'Berlin']
    
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Chris', 'Lisa']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    data = []
    for i in range(num_records):
        dept = np.random.choice(departments)
        pos = np.random.choice(positions)
        location = np.random.choice(locations)
        
        # Salary based on position
        base_salaries = {'Junior': 60000, 'Senior': 85000, 'Lead': 110000, 'Manager': 130000, 'Director': 180000}
        salary = base_salaries[pos] * np.random.uniform(0.9, 1.3)
        
        hire_date = datetime.now() - timedelta(days=np.random.randint(30, 2000))
        
        data.append({
            'Employee_ID': f'EMP{i+1:04d}',
            'First_Name': np.random.choice(first_names),
            'Last_Name': np.random.choice(last_names),
            'Department': dept,
            'Position': pos,
            'Location': location,
            'Hire_Date': hire_date.strftime('%Y-%m-%d'),
            'Salary': int(salary),
            'Performance_Rating': round(np.random.uniform(3.0, 5.0), 1),
            'Years_Experience': np.random.randint(1, 15),
            'Training_Hours': np.random.randint(10, 100)
        })
    
    return pd.DataFrame(data)

def generate_inventory_data(num_records: int = 300) -> pd.DataFrame:
    """Generate sample inventory data as DataFrame."""
    np.random.seed(44)
    
    categories = ['Electronics', 'Computers', 'Accessories', 'Software']
    suppliers = ['TechCorp', 'ElectroSupply', 'CompuParts', 'SoftwarePlus']
    warehouses = ['Warehouse A', 'Warehouse B', 'Warehouse C']
    
    products = ['Monitor', 'Keyboard', 'Mouse', 'Webcam', 'Speakers', 'Cables', 'Adapters', 'Cases']
    
    data = []
    for i in range(num_records):
        product = np.random.choice(products)
        category = np.random.choice(categories)
        supplier = np.random.choice(suppliers)
        warehouse = np.random.choice(warehouses)
        
        cost = np.random.uniform(10, 500)
        price = cost * np.random.uniform(1.2, 2.5)
        stock = np.random.randint(0, 1000)
        reorder_level = np.random.randint(10, 100)
        
        last_order = datetime.now() - timedelta(days=np.random.randint(1, 90))
        
        data.append({
            'Product_ID': f'PROD{i+1:04d}',
            'Product_Name': product,
            'Category': category,
            'Supplier': supplier,
            'Warehouse': warehouse,
            'Cost_Price': round(cost, 2),
            'Selling_Price': round(price, 2),
            'Stock_Quantity': stock,
            'Reorder_Level': reorder_level,
            'Last_Order_Date': last_order.strftime('%Y-%m-%d'),
            'Status': 'In Stock' if stock > reorder_level else 'Low Stock' if stock > 0 else 'Out of Stock'
        })
    
    return pd.DataFrame(data)

def create_sample_sales_data():
    """Create sample sales data Excel file."""
    df = generate_sales_data(1000)
    
    # Save to Excel
    df.to_excel('sample_data/sales_data.xlsx', index=False)
    print("✅ Created sales_data.xlsx")
    
def create_sample_employee_data():
    """Create sample employee data Excel file."""
    df = generate_employee_data(500)
    
    # Save to Excel
    df.to_excel('sample_data/employee_data.xlsx', index=False)
    print("✅ Created employee_data.xlsx")
    
def create_sample_inventory_data():
    """Create sample inventory data Excel file."""
    df = generate_inventory_data(300)
    
    # Save to Excel
    df.to_excel('sample_data/inventory_data.xlsx', index=False)
    print("✅ Created inventory_data.xlsx")
    
if __name__ == "__main__":
    # Create sample data directory if it doesn't exist
    os.makedirs('sample_data', exist_ok=True)
    
    # Generate and save sample datasets
    print("Generating sample datasets...")
    
    create_sample_sales_data()
    create_sample_employee_data()
    create_sample_inventory_data()
    
    # Multi-sheet example
    with pd.ExcelWriter('sample_data/multi_sheet_example.xlsx') as writer:
        generate_sales_data(100).to_excel(writer, sheet_name='Sales', index=False)
        generate_employee_data(50).to_excel(writer, sheet_name='Employees', index=False)
        generate_inventory_data(50).to_excel(writer, sheet_name='Inventory', index=False)
    print("✅ Created multi_sheet_example.xlsx")
    
    print("\n📊 Sample data files created in the 'sample_data' directory!")
    print("You can use these files to test the Excel AI Analyzer application.")
