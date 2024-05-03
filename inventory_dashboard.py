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
        if battery_capacity:
            if len(battery_capacity) == 1:  # Handle single value case
                query += f" AND battery_capacity = '{battery_capacity[0]}'"
            else:
                battery_capacity = tuple(map(str, battery_capacity))
                query += f" AND battery_capacity IN {battery_capacity}"
        if deployed_city:
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
    selected_cities = st.sidebar.multiselect('Select Deployed Cities', distinct_cities)

    # Fetch data from 'odoo_inventory' table for 'ops_status' with optional filters
    data_ops_status = fetch_data_from_supabase(['ops_status'], battery_capacity, selected_cities)

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

        # Fetch data from 'odoo_inventory' table for 'partner_id'
        data_partner_id = fetch_data_from_supabase(['deployed_city', 'partner_id'], battery_capacity, selected_cities)

        if data_partner_id is not None:
            # Create DataFrame for partner_id counts by deployed_city
            df_partner_id_counts = pd.DataFrame(data_partner_id, columns=['deployed_city', 'partner_id']).groupby('deployed_city')['partner_id'].count().reset_index()

            # Display the table showing count of partner_id for each deployed_city
            st.write("## Count of partner_id for each deployed_city")
            st.table(df_partner_id_counts)

        # Display the %Utilization scorecard
        st.write("## %Utilization Scorecard")
        st.write(f"%Utilization: {utilization_percentage:.2f}%")
        st.write("### Revenue Generation and Non-Revenue Generation Counts")
        st.write(df_counts)

if __name__ == "__main__":
    main()

