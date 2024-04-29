import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from supabase_py import create_client

# Connect to Supabase
supabase_url = "https://gqmpfexjoachyjgzkhdf.supabase.co"
supabase_key = "process.env.SUPABASE_KEY"
supabase = create_client(supabase_url, supabase_key)

def fetch_data_from_supabase(odoo_inventory):
    # Query Supabase table
    response = supabase.table(odoo_inventory).select().execute()
    if response['status'] == 200:
        data = response['data']
        df = pd.DataFrame(data)
        return df
    else:
        st.error("Error fetching data from Supabase")
        return None
        
# Main function to create the pie chart
def main():
    st.title("Pie Chart of Ops Status from Odoo Inventory")

    # Fetch data from 'odoo_inventory' table
    table_name = "odoo_inventory"
    data = fetch_data_from_supabase(table_name)

    if data is not None:
        # Count occurrences of each ops status
        ops_status_counts = data['ops status'].value_counts()

        # Create a pie chart
        fig, ax = plt.subplots()
        ax.pie(ops_status_counts, labels=ops_status_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

if __name__ == "__main__":
    main()
