import psycopg2
import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache_data(ttl=600)
def fetch_data_from_supabase(columns, filters):
    try:
        with psycopg2.connect(
            database="postgres",
            user='postgres.gqmpfexjoachyjgzkhdf',
            password='Change@2015Log9',
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='5432'
        ) as conn:
            with conn.cursor() as cursor:
                query = f"SELECT {', '.join(columns)} FROM odoo_inventory WHERE 1=1"
                for column, values in filters.items():
                    if values and column != 'region':  # Skip 'region' filter here
                        if len(values) == 1:
                            query += f" AND {column} = '{values[0]}'"
                        else:
                            values = tuple(map(str, values))
                            query += f" AND {column} IN {values}"
                cursor.execute(query)
                data_columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                return data_columns, data
    except psycopg2.Error as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None, None

@st.cache_data(ttl=600)
def fetch_distinct_values(column_name):
    try:
        with psycopg2.connect(
            database="postgres",
            user='postgres.gqmpfexjoachyjgzkhdf',
            password='Change@2015Log9',
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='5432'
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT DISTINCT {column_name} FROM odoo_inventory")
                data = cursor.fetchall()
                return [item[0] for item in data if item[0] is not None]  # Exclude None values
    except psycopg2.Error as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# Function to map deployed cities to regions
def get_region(city):
    west_cities = ['MUMBAI', 'SURAT', 'PUNE', 'AHMEDABAD', 'VADODARA', 'NAGPUR']
    north_cities = ['DELHI', 'LUCKNOW', 'KANPUR', 'JAIPUR', 'PRAYAGRAJ', 'AGRA', 'Agra', 'VARANASI', 'CHANDIGARH', 'Chandigarh', 'PANIPAT', 'Panipat', 'Sonipath', 'KOLKATA']
    south_cities = ['CHENNAI', 'BANGALORE', 'HYDERABAD', 'VIJAYAWADA', 'VIJAYWADA', 'KOCHI', 'COIMBATORE', 'Pondicherry']
    
    if city in west_cities:
        return 'West'
    elif city in north_cities:
        return 'North'
    elif city in south_cities:
        return 'South'
    else:
        return 'Not Known'

# Normalize ops_status values
def normalize_ops_status(status):
    normalization_dict = {
        'PILOT': 'PILOT',
        'PILOT VEHICLES': 'PILOT',
        'IOD': 'IOD',
        'IOD VEHICLES': 'IOD',
        'REGISTERED INVENTORY': 'REGISTERED INVENTORY',
        'REGISTERED VEHICLES STOCK': 'REGISTERED INVENTORY',
        'STOCK':'REGISTERED INVENTORY',
        'TR EXPIRED': 'UNREGISTERED INVENTORY',
        'UNREGISTERED INVENTORY': 'UNREGISTERED INVENTORY'
    }
    return normalization_dict.get(status, status)

def calculate_region_utilization(data_ops_status, selected_regions):
    region_counts = {'West': {'rev_gen': 0, 'total': 0},
                     'North': {'rev_gen': 0, 'total': 0},
                     'South': {'rev_gen': 0, 'total': 0},
                     'Not Known': {'rev_gen': 0, 'total': 0}}

    for row in data_ops_status:
        city = row[0]
        status = row[1]
        region = get_region(city)
        if not selected_regions or region in selected_regions:
            region_counts[region]['total'] += 1
            if status in ['RENTAL', 'PORTER']:
                region_counts[region]['rev_gen'] += 1

    region_utilization = {}
    overall_rev_gen = 0
    overall_total = 0

    for region, counts in region_counts.items():
        total = counts['total']
        rev_gen = counts['rev_gen']
        overall_rev_gen += rev_gen
        overall_total += total
        utilization = (rev_gen / total * 100) if total > 0 else 0
        region_utilization[region] = f"{utilization:.2f}%"

    overall_utilization = (overall_rev_gen / overall_total * 100) if overall_total > 0 else 0
    region_utilization['Overall'] = f"{overall_utilization:.2f}%"

    return region_utilization

def main():
    # Universal filters
    distinct_battery_capacities = fetch_distinct_values('battery_capacity')
    battery_capacity = st.sidebar.multiselect('Select Battery Capacity', distinct_battery_capacities)

    # Add Region filter
    distinct_cities = fetch_distinct_values('deployed_city')
    deployed_city = st.sidebar.multiselect('Select Deployed Cities', distinct_cities)

    region_options = ['West', 'North', 'South', 'Not Known']
    selected_regions = st.sidebar.multiselect('Select Region', region_options)
    
    distinct_ops_status = fetch_distinct_values('ops_status')
    ops_status = st.sidebar.multiselect('Select Ops Status', distinct_ops_status)

    distinct_partner_ids = fetch_distinct_values('partner_id')
    partner_id = st.sidebar.multiselect('Select Partner ID', distinct_partner_ids)

    distinct_chassis_numbers = fetch_distinct_values('chassis_number')
    chassis_number = st.sidebar.multiselect('Select Chassis Number', distinct_chassis_numbers)

    distinct_registration_numbers = fetch_distinct_values('registration_number')
    registration_number = st.sidebar.multiselect('Select Registration Number', distinct_registration_numbers)

    # Create a dictionary to store all filters except 'region'
    filters = {
        'battery_capacity': battery_capacity,
        'deployed_city': deployed_city,
        'ops_status': ops_status,
        'partner_id': partner_id,
        'chassis_number': chassis_number,
        'registration_number': registration_number,
    }

    # Fetch data from 'odoo_inventory' table for 'ops_status' with optional filters
    data_columns, data_ops_status = fetch_data_from_supabase(['deployed_city', 'ops_status'], filters)

    if data_ops_status is not None:
                # Normalize ops_status values
        data_ops_status = [(row[0], normalize_ops_status(row[1])) for row in data_ops_status]
        
        # Remove 'DEALER STOCK' and 'REPLACED & RCA PARTS' entries
        data_ops_status = [row for row in data_ops_status if row[1] not in ['DEALER STOCK', 'REPLACED & RCA PARTS','INPUT','QUALITY CONTROL']]

        # Filter based on selected regions
        if selected_regions:
            data_ops_status = [row for row in data_ops_status if get_region(row[data_columns.index('deployed_city')]) in selected_regions]

        # Calculate counts for 'rev gen' and 'non rev gen'
        ops_status_list = [row[1] for row in data_ops_status]
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

        # Calculate %Utilization for each region
        region_utilization = calculate_region_utilization(data_ops_status, selected_regions)

        # Display the %Utilization for each region
        st.write("## %Utilization by Region")
        region_utilization_df = pd.DataFrame(list(region_utilization.items()), columns=['Region', '%Utilization'])
        st.write(region_utilization_df)

        # Display the pie chart for ops_status
        st.write("## Ops Status Pie Chart")
        ops_status_counts = pd.Series(ops_status_list).value_counts()
        fig_ops_status = px.pie(ops_status_counts, values=ops_status_counts.values, names=ops_status_counts.index,
                                title='Ops Status Distribution', hole=0.3)
        fig_ops_status.update_traces(hoverinfo='label+percent')
        st.plotly_chart(fig_ops_status)

        # Fetch data from 'odoo_inventory' table for 'partner_id'
        data_columns, data_partner_id = fetch_data_from_supabase(['deployed_city', 'partner_id'], filters)

        if data_partner_id is not None:
            # Filter based on selected regions
            if selected_regions:
                data_partner_id = [row for row in data_partner_id if get_region(row[data_columns.index('deployed_city')]) in selected_regions]

            # Count occurrences of each partner_id and select top 10
            partner_id_list = [row[data_columns.index('partner_id')] for row in data_partner_id]
            partner_id_counts = pd.Series(partner_id_list).value_counts().head(10)

            # Display the pie chart for 'partner_id'
            st.write("## Top 10 Partner ID Pie Chart")
            fig_partner_id = px.pie(partner_id_counts, values=partner_id_counts.values, names=partner_id_counts.index,
                                    title='Top 10 Partner ID Distribution', hole=0.3)
            fig_partner_id.update_traces(hoverinfo='label+percent')
            st.plotly_chart(fig_partner_id)

        # Fetch data for pivot table
        data_columns, data_pivot = fetch_data_from_supabase(['deployed_city', 'ops_status'], filters)

        if data_pivot is not None:
            # Normalize ops_status values
            data_pivot = [(row[0], normalize_ops_status(row[1])) for row in data_pivot]
            
            # Remove 'DEALER STOCK' and 'REPLACED & RCA PARTS' entries
            data_pivot = [row for row in data_pivot if row[1] not in ['DEALER STOCK', 'REPLACED & RCA PARTS','INPUT','QUALITY CONTROL']]

            # Filter based on selected regions
            if selected_regions:
                data_pivot = [row for row in data_pivot if get_region(row[data_columns.index('deployed_city')]) in selected_regions]

            # Create DataFrame
            df_pivot = pd.DataFrame(data_pivot, columns=['deployed_city', 'ops_status'])
            # Pivot table
            pivot_table = pd.pivot_table(df_pivot, index='deployed_city', columns='ops_status', aggfunc='size', fill_value=0)
            # Display pivot table
            st.write("## Pivot Table: Count of Ops Status Across Deployed Cities")
            st.write(pivot_table)

        # Fetch data for partner_id count table
        data_columns, data_partner_id_count = fetch_data_from_supabase(['deployed_city', 'partner_id'], filters)

        if data_partner_id_count is not None:
            # Filter based on selected regions
            if selected_regions:
                data_partner_id_count = [row for row in data_partner_id_count if get_region(row[data_columns.index('deployed_city')]) in selected_regions]

            # Create DataFrame
            df_partner_id_count = pd.DataFrame(data_partner_id_count, columns=['deployed_city', 'partner_id'])
            # Group by partner_id and count deployed_city
            partner_id_count_table = df_partner_id_count.groupby('partner_id')['deployed_city'].value_counts().unstack(fill_value=0)
            # Display partner_id count table
            st.write("## Table: Count of Deployed Cities Across Partner IDs")
            st.write(partner_id_count_table)

        # Fetch data for deployed assets table
        data_columns, data_deployed_assets = fetch_data_from_supabase(['deployed_city', 'chassis_number', 'partner_id', 'battery_capacity', 'ops_status'], filters)

        if data_deployed_assets is not None:
            # Normalize ops_status values
            data_deployed_assets = [(row[0], row[1], row[2], row[3], normalize_ops_status(row[4])) for row in data_deployed_assets]
            
            # Remove 'DEALER STOCK' and 'REPLACED & RCA PARTS' entries
            data_deployed_assets = [row for row in data_deployed_assets if row[4] not in ['DEALER STOCK', 'REPLACED & RCA PARTS']]

            # Filter based on selected regions
            if selected_regions:
                data_deployed_assets = [row for row in data_deployed_assets if get_region(row[data_columns.index('deployed_city')]) in selected_regions]

                        # Create DataFrame
            df_deployed_assets = pd.DataFrame(data_deployed_assets, columns=['deployed_city', 'chassis_number', 'partner_id', 'battery_capacity', 'ops_status'])
            
            # Display the table
            st.write("## Table: Deployed Assets Information")
            st.write(df_deployed_assets)

if __name__ == "__main__":
    main()



