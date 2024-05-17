import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Function to fetch data from Supabase table
def fetch_data_from_supabase(columns, battery_capacity=None, deployed_city=None):
    try:
        conn = psycopg2.connect(
            database="postgres",
            user='postgres.gqmpfexjoachyjgzkhdf',
            password='Change@2015Log9',
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='5432'
        )
        cursor = conn.cursor()
        query = f"SELECT {', '.join(columns)} FROM odoo_inventory WHERE 1=1"
        if battery_capacity and 'All' not in battery_capacity:
            if len(battery_capacity) == 1:  # Handle single value case
                query += f" AND battery_capacity = '{battery_capacity[0]}'"
            else:
                battery_capacity = tuple(map(str, battery_capacity))
                query += f" AND battery_capacity IN {battery_capacity}"
        if deployed_city and 'All' not in deployed_city:
            if len(deployed_city) == 1:  # Handle single value case
                query += f" AND deployed_city = '{deployed_city[0]}'"
            else:
                query += f" AND deployed_city IN {tuple(deployed_city)}"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data
    except psycopg2.Error as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# Function to fetch distinct values for a column from Supabase table
def fetch_distinct_values(column_name):
    try:
        conn = psycopg2.connect(
            database="postgres",
            user='postgres.gqmpfexjoachyjgzkhdf',
            password='Change@2015Log9',
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='5432'
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT {column_name} FROM odoo_inventory")
        data = cursor.fetchall()
        conn.close()
        return [item[0] for item in data]
    except psycopg2.Error as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# Main function to create the scorecard chart and other visualizations
def main():
    # Universal filters
    distinct_battery_capacities = fetch_distinct_values('battery_capacity')
    battery_capacity = st.sidebar.multiselect('Select Battery Capacity', distinct_battery_capacities + ['All'])

    distinct_cities = fetch_distinct_values('deployed_city')
    selected_cities = st.sidebar.multiselect('Select Deployed Cities', distinct_cities + ['All'])

    # Fetch data from 'odoo_inventory' table for 'ops_status' with optional filters
    data_ops_status = fetch_data_from_supabase(['ops_status'], battery_capacity if 'All' not in battery_capacity else None, selected_cities if 'All' not in selected_cities else None)

    if data_ops_status is not None:
        # Calculate counts for 'rev gen' and 'non rev gen'
        ops_status_list = [item[0] for item in data_ops_status]
        rev_gen_count = sum(1 for status in ops_status_list if status in ['RENTAL', 'PORTER'])
        non_rev_gen_count = len(ops_status_list) - rev_gen_count
        total_count = len(ops_status_list)

        # Calculate %Utilization using existing counts
        utilization_percentage = (rev_gen_count / total_count) * 100 if total_count != 0 else 0

        # Create DataFrame for rev_gen, non_rev_gen, and total counts
        df_counts = pd.DataFrame({
            'Category': ['Rev Gen', 'Non Rev Gen', 'Total'],
            'Count': [rev_gen_count, non_rev_gen_count, total_count]
        })

        # Display the %Utilization and revenue generation count in two columns at the top of the page
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("## %Utilization")
            st.write(f"{utilization_percentage:.2f}%")
        with col2:
            st.write("## Revenue Generation and Non-Revenue Generation Counts")
            st.write(df_counts)

        # Display the pie charts
        st.write("## Ops Status Pie Chart")
        ops_status_counts = pd.Series(ops_status_list).value_counts()
        fig_ops_status, ax_ops_status = plt.subplots(figsize=(10, 9))
        ax_ops_status.pie(ops_status_counts, labels=None, autopct='%1.1f%%', startangle=90)
        ax_ops_status.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.legend(ops_status_counts.index, loc="upper left", bbox_to_anchor=(1, 0.8))  # Place labels as legends and shift upwards
        plt.tight_layout()  # Adjust layout to prevent label overlap
        plt.rcParams['font.size'] = 12  # Adjust font size of labels
        st.pyplot(fig_ops_status)

        # Fetch data from 'odoo_inventory' table for 'partner_id'
        data_partner_id = fetch_data_from_supabase(['partner_id'], battery_capacity if 'All' not in battery_capacity else None, selected_cities if 'All' not in selected_cities else None)

        if data_partner_id is not None:
            # Count occurrences of each partner_id and select top 10
            partner_id_list = [item[0] for item in data_partner_id]
            partner_id_counts = pd.Series(partner_id_list).value_counts().head(10)

            # Display the pie chart for 'partner_id'
            st.write("## Top 10 Partner ID Pie Chart")
            fig_partner_id, ax_partner_id = plt.subplots(figsize=(10, 9))
            ax_partner_id.pie(partner_id_counts, labels=None, autopct='%1.1f%%', startangle=90)
            ax_partner_id.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.legend(partner_id_counts.index, loc="upper left", bbox_to_anchor=(1, 0.8))  # Place labels as legends and shift upwards
            plt.tight_layout()  # Adjust layout to prevent label overlap
            plt.rcParams['font.size'] = 12  # Adjust font size of labels
            st.pyplot(fig_partner_id)

        # Fetch data for pivot table
        data_pivot = fetch_data_from_supabase(['deployed_city', 'ops_status'], battery_capacity if 'All' not in battery_capacity else None, selected_cities if 'All' not in selected_cities else None)

        if data_pivot is not None:
            # Create DataFrame
            df_pivot = pd.DataFrame(data_pivot, columns=['deployed_city', 'ops_status'])
            # Pivot table
            pivot_table = pd.pivot_table(df_pivot, index='deployed_city', columns='ops_status', aggfunc='size', fill_value=0)
            # Display pivot table
            st.write("## Pivot Table: Count of Ops Status Across Deployed Cities")
            st.write(pivot_table)

        # Fetch data for partner_id count table
        data_partner_id_count = fetch_data_from_supabase(['deployed_city', 'partner_id'], battery_capacity if 'All' not in battery_capacity else None, selected_cities if 'All' not in selected_cities else None)

        if data_partner_id_count is not None:
            # Create DataFrame
            df_partner_id_count = pd.DataFrame(data_partner_id_count, columns=['deployed_city', 'partner_id'])
            # Group by partner_id and count deployed_city
            partner_id_count_table = df_partner_id_count.groupby('partner_id')['deployed_city'].value_counts().unstack(fill_value=0)
            # Display partner_id count table
            st.write("## Table: Count of Deployed Cities Across Partner IDs")
            st.write(partner_id_count_table)

        # Fetch data for pivot table
        data_pivot = fetch_data_from_supabase(['deployed_city', 'chassis_number', 'partner_id', 'battery_capacity', 'ops_status'], battery_capacity if 'All' not in battery_capacity else None, selected_cities if 'All' not in selected_cities else None)

        if data_pivot is not None:
            # Create DataFrame
            df_pivot = pd.DataFrame(data_pivot, columns=['deployed_city', 'chassis_number', 'partner_id', 'battery_capacity', 'ops_status'])
            
            # Display the table
            st.write("## Table: Deployed Assets Information")
            st.write(df_pivot)

if __name__ == "__main__":
    main()

