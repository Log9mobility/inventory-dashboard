import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px

# Function to fetch data from Supabase table
def fetch_data_from_supabase(columns, battery_capacity=None, deployed_city=None):
    # Implementation of fetch_data_from_supabase function

# Function to fetch distinct values for a column from Supabase table
def fetch_distinct_values(column_name):
    # Implementation of fetch_distinct_values function

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
        
        # Plot pie chart using Plotly Express
        ops_status_counts = pd.Series(ops_status_list).value_counts().reset_index()
        ops_status_counts.columns = ['ops_status', 'count']
        fig_ops_status = px.pie(ops_status_counts, values='count', names='ops_status', 
                                 title='Ops Status Pie Chart', 
                                 hover_data=['ops_status', 'count'], 
                                 labels={'ops_status': 'Ops Status', 'count': 'Count'})
        
        # Display the pie chart
        st.plotly_chart(fig_ops_status)
        
        # The rest of your code...

if __name__ == "__main__":
    main()
