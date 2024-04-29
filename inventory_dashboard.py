import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Function to fetch data from Supabase table
def fetch_data_from_supabase():
    try:
        conn = psycopg2.connect(
            database="postgres",
            user='postgres.gqmpfexjoachyjgzkhdf',
            password='Change@2015Log9',
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='5432'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT ops_status FROM odoo_inventory")
        data = cursor.fetchall()
        conn.close()
        return [item[0] for item in data]
    except psycopg2.Error as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# Main function to create the pie chart
def main():
    st.title("Pie Chart of Ops Status from Odoo Inventory")

    # Fetch data from 'odoo_inventory' table
    data = fetch_data_from_supabase()

    if data is not None:
        # Count occurrences of each ops status
        ops_status_counts = pd.Series(data).value_counts()

        # Create columns to layout the chart
        col1, col2 = st.columns([1, 1])  # Divide the page into two columns

        # Position the pie chart in the second half, right side of the page
        with col2:
            st.write("## Ops Status Pie Chart")
            fig, ax = plt.subplots(figsize=(8, 6))  # Adjust the figure size here
            ax.pie(ops_status_counts, labels=ops_status_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.tight_layout()  # Adjust layout to prevent label overlap
            st.pyplot(fig)

if __name__ == "__main__":
    main()
