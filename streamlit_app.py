import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO

# Define a helper function to calculate age from the birthday
def calculate_age(birthdate):
    birthdate = datetime.strptime(birthdate, "%m/%d/%Y")
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

# Streamlit app
st.title('Child Data Processor')

# Text area for pasting CSV data
csv_input = st.text_area("Paste the CSV data here")

if not csv_input:
    st.stop()

# Read the CSV data from the input
data = StringIO(csv_input)
df = pd.read_csv(data, sep='\t')

# Initialize an empty list to hold the data for the new sheet
data = []

# Sanitize column names
df.columns = df.columns.str.strip()
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace('(and last name if different from parent/guardian)', '')
df.columns = df.columns.str.replace(' ', '_')
df.columns = df.columns.str.replace('/', '_')
df.columns = df.columns.str.replace('(', '_')
df.columns = df.columns.str.replace(')', '_')
df.columns = df.columns.str.replace('-', '_')
df.columns = df.columns.str.replace('#', '')
df.columns = df.columns.str.replace('\'s', '')
df.columns = df.columns.str.strip("_")

# Strip all the values
df = df.applymap(lambda x: x.strip() if pd.notna(x) else x)

st.write(df)

# Process each row in the original sheet
for index, row in df.iterrows():
    parent_first_name = row['parent_guardian_first_name']
    parent_last_name = row['parent_guardian_last_name']

    # Loop through each child's information in the row
    for i in range(1, 7):  # There are up to 6 children
        child_first_name_col = f'child_{i}_first_name'
        child_birthday_col = f'child_{i}_birthday'
        child_grade_col = f'grade_child_{i}_most_recently_completed'

        if pd.notna(row[child_first_name_col]):
            child_first_name = row[child_first_name_col]
            child_birthday = row[child_birthday_col]
            child_grade = row[child_grade_col]

            # Calculate the child's age
            child_age = calculate_age(child_birthday)

            # Append the processed data to the list
            data.append([
                parent_first_name,
                parent_last_name,
                child_first_name,
                child_age,
                child_grade
            ])

# Create a new DataFrame for the processed data
new_df = pd.DataFrame(data, columns=[
    'parent_guardian_first_name',
    'parent_guardian_last_name',
    'child_first_name',
    'child_age',
    'child_most_recently_completed'
])

def class_division(row):
    if row["child_age"] < 4:
        return "Nursery"
    elif row['child_age'] < 6 or row["child_most_recently_completed"].lower() in ["pre-k", "kindergarden", "kindergarten", "k"]:
        return "4Yrs-K"
    elif row["child_most_recently_completed"].lower() in ["1st grade", "first", "1st", "1", "2", "2nd", "second"]:
        return "1-2 grade"
    elif row["child_most_recently_completed"].lower() in ["3rd grade", "3rd", "third", "3", "4", "4th", "fourth"]:
        return "3-4 grade"
    elif row["child_most_recently_completed"].lower() in ["5th grade", "5th", "fifth", "5", "6", "6th", "sixth"]:
        return "5-6 grade"
    else:
        st.error(dict(row))
        return "Unknown"


new_df["class_division"] = new_df.apply(class_division, axis=1)
# Convert the new DataFrame to CSV format
csv_output = new_df.to_csv(index=False, sep='\t')

# Display the CSV output in a code block
st.code(csv_output)