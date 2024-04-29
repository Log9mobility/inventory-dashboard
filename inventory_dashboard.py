import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Function to fetch data from Supabase table
def fetch_data_from_supabase(column_name, battery_capacity=None):
    try:
        conn = psycopg2.connect(
            database="postgres",
            user='postgres.gqmpfexjoachyjgzkhdf',
            password='Change@2015Log9',
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='5432'
        )
        cursor = conn.cursor()
        if battery_capacity and 'All' not in battery_capacity:
            # Convert battery_capacity to tuple if it's not 'All'
            battery_capacity = tuple(map(str, battery_capacity))
            cursor.execute(f"SELECT {column_name} FROM odoo_inventory WHERE battery_capacity IN %s", (battery_capacity,))
        else:
            cursor.execute(f"SELECT {column_name} FROM odoo_inventory")
        data = cursor.fetchall()
        conn.close()
        return [item[0] for item in data]
    except psycopg2.Error as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# Function to fetch distinct battery capacities from Supabase table
def fetch_distinct_battery_capacities():
    try:
        conn = psycopg2.connect(
            database="postgres",
            user='postgres.gqmpfexjoachyjgzkhdf',
            password='Change@2015Log9',
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='5432'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT battery_capacity FROM odoo_inventory")
        data = cursor.fetchall()
        conn.close()
        return [item[0] for item in data]
    except psycopg2.Error as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# Main function to create the scorecard chart and other visualizations
def main():
    # Battery capacity filter
    distinct_battery_capacities = fetch_distinct_battery_capacities()
    battery_capacity = st.sidebar.multiselect('Select Battery Capacity', distinct_battery_capacities + ['All'])

    # Fetch data from 'odoo_inventory' table for 'ops_status' with optional battery capacity filter
    data_ops_status = fetch_data_from_supabase('ops_status', battery_capacity)

    if data_ops_status is not None:
        # Calculate counts for 'rev gen' and 'non rev gen'
        rev_gen_count = sum(1 for status in data_ops_status if status in ['RENTAL', 'PORTER'])
        non_rev_gen_count = len(data_ops_status) - rev_gen_count
        total_count = len(data_ops_status)

        # Calculate %Utilization using existing counts
        utilization_percentage = (rev_gen_count / total_count) * 100

        # Create DataFrame for rev_gen, non_rev_gen, and total counts
        df_counts = pd.DataFrame({
            'Category': ['Rev Gen', 'Non Rev Gen', 'Total'],
            'Count': [rev_gen_count, non_rev_gen_count, total_count]
        })

        # Display the %Utilization scorecard
        st.write("## %Utilization Scorecard")
        st.write(f"%Utilization: {utilization_percentage:.2f}%")
        st.write("### Revenue Generation and Non-Revenue Generation Counts")
        st.write(df_counts)

        # Fetch data from 'odoo_inventory' table for 'partner_id'
        data_partner_id = fetch_data_from_supabase('partner_id', battery_capacity)

        if data_partner_id is not None:
            # Count occurrences of each partner_id and select top 10
            partner_id_counts = pd.Series(data_partner_id).value_counts().head(10)

            # Create columns to layout the charts
            col1, col2 = st.columns([1, 1])

            # Position the pie chart for 'ops_status' in the first column
            with col1:
                st.write("## Ops Status Pie Chart")
                ops_status_counts = pd.Series(data_ops_status).value_counts()
                fig_ops_status, ax_ops_status = plt.subplots(figsize=(10, 8))
                ax_ops_status.pie(ops_status_counts, labels=None, autopct='%1.1f%%', startangle=90)
                ax_ops_status.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                plt.legend(ops_status_counts.index, loc="upper left", bbox_to_anchor=(1, 0.5))  # Place labels as legends and shift upwards
                plt.tight_layout()  # Adjust layout to prevent label overlap
                plt.rcParams['font.size'] = 12  # Adjust font size of labels
                st.pyplot(fig_ops_status)

            # Position the pie chart for 'partner_id' in the second column
            with col2:
                st.write("## Top 10 Partner ID Pie Chart")
                fig_partner_id, ax_partner_id = plt.subplots(figsize=(10, 8))
                ax_partner_id.pie(partner_id_counts, labels=None, autopct='%1.1f%%', startangle=90)
                ax_partner_id.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                plt.legend(partner_id_counts.index, loc="upper left", bbox_to_anchor=(1, 0.5))  # Place labels as legends and shift upwards
                plt.tight_layout()  # Adjust layout to prevent label overlap
                plt.rcParams['font.size'] = 12  # Adjust font size of labels
                st.pyplot(fig_partner_id)

if __name__ == "__main__":
    main()





