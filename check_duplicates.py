import pandas as pd

try:
    df = pd.read_excel('dmv questions.xlsx')
    
    # Check for duplicates based on Options and Correct Answer
    # We'll create a combined column for checking
    cols_to_check = ['Option A', 'Option B', 'Option C', 'Correct Answer']
    
    duplicates = df[df.duplicated(subset=cols_to_check, keep=False)]
    
    print(f"Total rows: {len(df)}")
    print(f"Unique content combinations: {len(df.drop_duplicates(subset=cols_to_check))}")
    print(f"Duplicate rows found: {len(duplicates)}")
    
    if not duplicates.empty:
        print("\nExample duplicates (showing Question text):")
        print(duplicates[['#', 'Question', 'Correct Answer']].head(10).to_string(index=False))
        
except Exception as e:
    print(f"Error: {e}")
