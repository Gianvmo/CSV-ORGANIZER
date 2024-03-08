import os
import re
import math
import pandas as pd
from fuzzywuzzy import process

# Function to recursively find CSV files in a directory
def find_csv_files(directory):
    csv_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files
# Function to extract first name from a cell
def extract_first_name(cell):
    return cell.strip() if isinstance(cell, str) else str(cell)

# Function to extract last name from a cell
def extract_last_name(cell):
    return cell.strip() if isinstance(cell, str) else str(cell)

# Function to extract email from a cell
def extract_email(cell):
    if isinstance(cell, str) and '@' in cell:
        return cell.strip().lower()
    else:
        return str(cell)

# Function to extract phone number from a cell
def extract_phone_number(cell):
    if isinstance(cell, str):
        # Remove non-numeric characters
        phone_number = re.sub(r'\D', '', cell)
        if len(phone_number) >= 10:  # Assuming all phone numbers should have 11 digits
            return phone_number
    return str(cell)

# Function to extract state from a cell
def extract_state(cell):
    if isinstance(cell, str) and len(cell) == 2 :
        return cell.strip().upper()
    else:
        return str(cell)

# Function to extract zip code from a cell
def extract_zip_code(cell):
    if isinstance(cell, str):
        # Extract only the first 5 digits using regular expressions
        zip_code_match = re.search(r'\d{5}', cell)
        if zip_code_match:
            return zip_code_match.group()
    elif isinstance(cell, (int, float)) and not math.isnan(cell):
        # Convert numeric values to string and extract the first 5 characters
        zip_code_str = str(int(cell))
        return zip_code_str[:5]

    return str(cell)


# Get the current directory
directory = os.path.join(os.getcwd(), "DESKTOP/LEADS")

# Find all CSV files in the directory and its subdirectories
csv_files = find_csv_files(directory)

reference_df = pd.read_csv('DESKTOP/reference.csv')

# List to hold DataFrames of each CSV
dfs = []

# Dictionary to hold mappings of similar column names
column_mapping = {}

# List to hold filenames that were successfully read
successful_files = []

# List to hold filenames that encountered errors
failed_files = []

# Loop through each CSV file found
for csv_file in csv_files:
    try:
        # Read CSV into a DataFrame
        df = pd.read_csv(csv_file)

        # Reset index of the DataFrame
        df = df.reset_index(drop=True)
        # Remove rows where Column A or D contains "nan"


        dfs.append(df)
        successful_files.append(csv_file)
    except Exception as e:
        failed_files.append(csv_file)
        print(f"Failed to read file: {csv_file} - Error: {e}")

# Check if any DataFrames were successfully read
if dfs:
    # Concatenate DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)

    # Extract attributes from identified columns
    combined_df['firstName'] = combined_df['firstName'].apply(extract_first_name)
    combined_df['lastName'] = combined_df['lastName'].apply(extract_last_name)
    combined_df['email'] = combined_df['email'].apply(extract_email)
    combined_df['phoneNumber'] = combined_df['phoneNumber'].apply(extract_phone_number)
    combined_df['state'] = combined_df['state'].apply(extract_state)
    combined_df['postalCode'] = combined_df['postalCode'].apply(extract_zip_code)

    # Selecting only the required columns
    combined_df = combined_df[['firstName', 'lastName', 'email', 'phoneNumber', 'state', 'postalCode']]

    # Remove duplicates based on a specific column
    combined_df.drop_duplicates(subset=['phoneNumber'], inplace=True)

    # Export the cleaned and merged DataFrame to a new CSV file
    combined_df.to_csv('final_organized_leads6.csv', index=False)

    print("Organized leads CSV file created successfully.")

# Print list of failed files
print("\nFiles failed to read:")
print(failed_files)
print("\nSuccessful to read:")
for file_path in successful_files:
    print(file_path)

