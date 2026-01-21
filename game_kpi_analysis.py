import pandas as pd

# Load the dataset
# Note: Ensure your CSV is named 'indiequest_data.csv' in the same folder
try:
    df = pd.read_csv('indiequest_data.csv')

    print("--- GAME DATA KPI ANALYSIS ---\n")

    # 1. Identify the game with the HIGHEST rating in EACH PLATFORM
    # We use idxmax to find the index of the highest rating per group
    idx_max_rating = df.groupby('Platform')['Rating'].idxmax()
    highest_rated = df.loc[idx_max_rating, ['Platform', 'Title', 'Genre', 'Rating']]
    
    print("Highest Rated Game per Platform:")
    print(highest_rated)
    print("\n" + "-"*30 + "\n")

    # 2. Identify the game with the HIGHEST REVENUE in EACH PLATFORM
    idx_max_revenue = df.groupby('Platform')['Revenue'].idxmax()
    highest_revenue = df.loc[idx_max_revenue, ['Platform', 'Title', 'Genre', 'Revenue']]
    
    print("Highest Revenue Game per Platform:")
    print(highest_revenue)
    print("\n" + "-"*30 + "\n")

    # 3. State what the KPIs are
    print("KEY PERFORMANCE INDICATORS (KPIs):")
    print("1. Average Rating: Measures player satisfaction and game quality.")
    print("2. Total Revenue: Measures the financial success and market value.")
    print("3. Units Sold: Measures the reach and popularity of the game.")
    print("4. Revenue per Unit: (Calculated) Measures the pricing efficiency.")

except FileNotFoundError:
    print("Error: 'indiequest_data.csv' not found. Please ensure the file is in the correct directory.")