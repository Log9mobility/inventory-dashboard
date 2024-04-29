pip install streamlit matplotlib
import streamlit as st
import matplotlib.pyplot as plt
def main():
    st.title('Pie Chart Example')
     # Sample data
    labels = ['A', 'B', 'C', 'D']
    sizes = [15, 30, 45, 10]
    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # Display the chart using Streamlit
    st.pyplot(fig)
if __name__ == "__main__":
    main()
