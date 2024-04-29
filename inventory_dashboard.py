yimport streamlit as st
import psycopg2
import pandas as pd
from streamlit_echarts import st_echarts
import numpy as np
import os
import time
import plotly.express as px
import plotly.subplots as sp
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pydeck as pdk
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime, timedelta


# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Set page configuration to wide mode and set page title
st.set_page_config(layout="wide", page_title="Inventory Dashboard")

# Mapbox Access Token
# Set Mapbox access token
px.set_mapbox_access_token("pk.eyJ1IjoicC1zaGFybWEiLCJhIjoiY2xzNjRzbTY1MXNodjJsbXUwcG0wNG50ciJ9.v32bwq-wi6whz9zkn6ecow")

# Function to connect to database and get data using psycopg2
@st.cache_data

def get_data():
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

        # Create a pie chart
        fig, ax = plt.subplots()
        ax.pie(ops_status_counts, labels=ops_status_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

if __name__ == "__main__":
    main()
