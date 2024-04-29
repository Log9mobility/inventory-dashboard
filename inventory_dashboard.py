import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Function to fetch data from Supabase table
def fetch_data_from_supabase(column_name):
    try:
        conn = psycopg2.connect(
            database="postgres",
            user='postgres.gqmpfexjoachyjgzkhdf',
            password='Change@2015Log9',
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='5432'
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT {column_name} FROM odoo_inventory")
        data = cursor.fetchall()
        conn.close()
        return [item[0] for item in data]
    except psycopg2.Error as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# Main function to create the pie chart
def main():
    st.title("Pie Charts from Odoo Inventory")

    # Fetch data from 'odoo_inventory' table for 'ops_status'
    data_ops_status = fetch_data_from_supabase('ops_status')

    if data_ops_status is not None:
        # Count occurrences of each ops status
        ops_status_counts = pd.Series(data_ops_status).value_counts()

        # Position the pie chart for 'ops_status' in the first half, left side of the page
        st.write("## Ops Status Pie Chart")
        fig_ops_status, ax_ops_status = plt.subplots(figsize=(8, 6))
        ax_ops_status.pie(ops_status_counts, labels=ops_status_counts.index, autopct='%1.1f%%', startangle=90)
        ax_ops_status.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()  # Adjust layout to prevent label overlap
        plt.rcParams['font.size'] = 12  # Adjust font size of labels
        st.pyplot(fig_ops_status)

    # Fetch data from 'odoo_inventory' table for 'partner_id'
    data_partner_id = fetch_data_from_supabase('partner_id')

    if data_partner_id is not None:
        # Count occurrences of each partner_id
        partner_id_counts = pd.Series(data_partner_id).value_counts()

        # Position the pie chart for 'partner_id' in the second half, right side of the page
        st.write("## Partner ID Pie Chart")
        fig_partner_id, ax_partner_id = plt.subplots(figsize=(8, 6))
        ax_partner_id.pie(partner_id_counts, labels=partner_id_counts.index, autopct='%1.1f%%', startangle=90)
        ax_partner_id.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()  # Adjust layout to prevent label overlap
        plt.rcParams['font.size'] = 12  # Adjust font size of labels
        st.pyplot(fig_partner_id)

if __name__ == "__main__":
    main()

