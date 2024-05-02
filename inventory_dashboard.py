# New filter for 'Region'
region_options = ['All', 'North', 'South', 'West', 'None']
selected_region = st.sidebar.selectbox('Select Region', region_options)

# Define city lists for each region
city_lists = {
    'North': ["Delhi","Jaipur","Kanpur","Lucknow","Kolkata","Varanasi","Prayagraj","Chandigarh","Agra","Panipat","Sonipath","Panchkula","Gurgaon"],
    'South': ["Bangalore","Bengaluru","Chennai","Hyderabad","Vijayawada","Mysore","Coimbatore"],
    'West': ["Ahmedabad","Mumbai","Pune","Vadodara","Surat","Gujarat"],
}

# Fetch data from 'odoo_inventory' table for 'ops_status' with optional filters
data_ops_status = fetch_data_from_supabase('ops_status', battery_capacity, selected_cities, selected_region)

if data_ops_status is not None:
    # Filter cities based on selected region
    if selected_region != 'All':
        selected_cities = [city for city in selected_cities if city in city_lists[selected_region]]

    # Calculate counts for 'rev gen' and 'non rev gen'
    rev_gen_count = sum(1 for status in data_ops_status if status in ['RENTAL', 'PORTER'])
    non_rev_gen_count = len(data_ops_status) - rev_gen_count
    total_count = len(data_ops_status)

    # Calculate %Utilization using existing counts
    if total_count == 0:
        utilization_percentage = 0
    else:
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
    data_partner_id = fetch_data_from_supabase('partner_id', battery_capacity, selected_cities, selected_region)

    if data_partner_id is not None:
        # Count occurrences of each partner_id and select top 10
        partner_id_counts = pd.Series(data_partner_id).value_counts().head(10)

        # Create columns to layout the charts
        col1, col2 = st.columns(2)

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




