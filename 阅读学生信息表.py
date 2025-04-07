import pandas as pd

# --- Configuration ---
excel_file = 'your_student_data.xlsx' # Replace with your actual file path
# Example path for a common Chinese font on Windows. Adjust if needed.
# On Linux/MacOS, find a suitable font path like '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
FONT_PATH = 'C:/Windows/Fonts/simhei.ttf'
# --- End Configuration ---


try:
    df = pd.read_excel(excel_file)
    print("Data loaded successfully. First 5 rows:")
    print(df.head())
    print("\nData Info:")
    df.info()
except FileNotFoundError:
    print(f"Error: File not found at {excel_file}")
    exit()
except Exception as e:
    print(f"Error loading Excel file: {e}")
    exit()

# Basic Data Cleaning (Example: Handle potential empty mottos)
df['人生格言'] = df['人生格言'].fillna('') # Replace NaN with empty string
# Convert rank columns to numeric, coercing errors (non-numeric values become NaN)
rank_cols = ['大一上学期名次', '大一下学期名次', '大二上学期名次', '大二下学期名次', '大三上学期名次']
for col in rank_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
