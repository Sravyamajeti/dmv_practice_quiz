import pandas as pd # 'pandas' is a tool for working with data like Excel files.

try:
    # Read the Excel file named 'dmv questions.xlsx'
    df = pd.read_excel('dmv questions.xlsx')
    
    # Print the names of the columns (headers) in the Excel file
    print("Columns:", df.columns.tolist())
    
    # Print the first 5 rows of data so we can see what it looks like
    print("\nFirst 5 rows:")
    print(df.head().to_string())
except Exception as e:
    # If there is an error (like the file is missing), print the error message
    print(f"Error reading excel file: {e}")
