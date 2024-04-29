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

# Main function to create the pie charts
def main():
    # Fetch data from 'odoo_inventory' table for 'ops_status'
    data_ops_status = fetch_data_from_supabase('ops_status')

    if data_ops_status is not None:
        # Count occurrences of each ops status
        ops_status_counts = pd.Series(data_ops_status).value_counts()

        # Fetch data from 'odoo_inventory' table for 'partner_id'
        data_partner_id = fetch_data_from_supabase('partner_id')

        if data_partner_id is not None:
            # Count occurrences of each partner_id and select top 10
            partner_id_counts = pd.Series(data_partner_id).value_counts().head(10)

            # Create columns to layout the charts
            col1, col2 = st.columns([1, 1])

            # Position the pie chart for 'ops_status' in the first column
            with col1:
                st.write("## Ops Status Pie Chart")
                fig_ops_status, ax_ops_status = plt.subplots(figsize=(12, 10))
                ax_ops_status.pie(ops_status_counts, labels=None, autopct='%1.1f%%', startangle=90)
                ax_ops_status.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                plt.legend(ops_status_counts.index, loc="upper left", bbox_to_anchor=(1, 0))  # Place labels as legends
                plt.tight_layout()  # Adjust layout to prevent label overlap
                plt.rcParams['font.size'] = 12  # Adjust font size of labels
                st.pyplot(fig_ops_status)

            # Position the pie chart for 'partner_id' in the second column
            with col2:
                st.write("## Top 10 Partner ID Pie Chart")
                fig_partner_id, ax_partner_id = plt.subplots(figsize=(12, 10))
                ax_partner_id.pie(partner_id_counts, labels=None, autopct='%1.1f%%', startangle=90)
                ax_partner_id.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                plt.legend(partner_id_counts.index, loc="upper left", bbox_to_anchor=(1, 0.5))  # Place labels as legends
                plt.tight_layout()  # Adjust layout to prevent label overlap
                plt.rcParams['font.size'] = 12  # Adjust font size of labels
                st.pyplot(fig_partner_id)

if __name__ == "__main__":
    main()
