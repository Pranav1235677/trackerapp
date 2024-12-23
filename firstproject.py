import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Function to generate a simulated dataset
def generate_data(month):
    categories = ["Food", "Transportation", "Bills", "Groceries", "Entertainment", "Healthcare", "Shopping", "Dining", "Travel", "Education"]
    payment_modes = ["Cash", "Online", "NetBanking", "Credit Card", "Debit Card", "Wallet"]
    data = []
    for _ in range(100):
        data.append({
            "Date": fake.date_this_year(),
            "Category": random.choice(categories),
            "Payment_Mode": random.choice(payment_modes),
            "Description": fake.sentence(nb_words=6),
            "Amount_Paid": round(random.uniform(10.0, 500.0), 2),
            "Cashback": round(random.uniform(0.0, 20.0), 2),
            "Month": month
        })
    return pd.DataFrame(data)

# Function to initialize the SQLite database
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            Date TEXT,
            Category TEXT,
            Payment_Mode TEXT,
            Description TEXT,
            Amount_Paid REAL,
            Cashback REAL,
            Month TEXT
        )
    """)
    conn.commit()
    conn.close()

# Function to load data into the database
def load_data_to_db(data):
    conn = sqlite3.connect('expenses.db')
    data.to_sql('expenses', conn, if_exists='append', index=False)
    conn.close()

# Function to query data from the database
def query_data(query):
    conn = sqlite3.connect('expenses.db')
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

# Extended SQL Queries
SQL_QUERIES = {
    "Total Amount Spent per Category": "SELECT Category, SUM(Amount_Paid) AS Total_Spent FROM expenses GROUP BY Category",
    "Monthly Spending Breakdown": "SELECT Month, SUM(Amount_Paid) AS Total_Spent FROM expenses GROUP BY Month",
    "Top 5 Highest Expenses": "SELECT * FROM expenses ORDER BY Amount_Paid DESC LIMIT 5",
    "Payment Mode Analysis": "SELECT Payment_Mode, COUNT(*) AS Transaction_Count, SUM(Amount_Paid) AS Total_Spent FROM expenses GROUP BY Payment_Mode",
    "Average Cashback by Category": "SELECT Category, AVG(Cashback) AS Avg_Cashback FROM expenses GROUP BY Category",
    "Spending Trends Over Time": "SELECT Date, SUM(Amount_Paid) AS Daily_Spent FROM expenses GROUP BY Date ORDER BY Date",
    "Top Spending Days": "SELECT Date, SUM(Amount_Paid) AS Total_Spent FROM expenses GROUP BY Date ORDER BY Total_Spent DESC LIMIT 10",
    "Average Spending by Month": "SELECT Month, AVG(Amount_Paid) AS Avg_Spending FROM expenses GROUP BY Month",
    "Category Breakdown for a Specific Month": "SELECT Category, SUM(Amount_Paid) AS Total_Spent FROM expenses WHERE Month='January' GROUP BY Category",
    "Highest Cashback Transactions": "SELECT * FROM expenses ORDER BY Cashback DESC LIMIT 5",
    "Transactions Above 300": "SELECT * FROM expenses WHERE Amount_Paid > 300 ORDER BY Amount_Paid DESC"
}

# Main Streamlit app
st.title("Personal Expense Tracker")

# Sidebar options
option = st.sidebar.selectbox(
    "Choose an option",
    ["Generate Data", "View Data", "Visualize Insights", "Run SQL Query", "Predefined SQL Queries"]
)

if option == "Generate Data":
    st.subheader("Generate Expense Data")
    month = st.text_input("Enter the month:", "January")
    if st.button("Generate"):
        data = generate_data(month)
        load_data_to_db(data)
        st.success(f"Data for {month} generated and loaded into the database!")
        st.dataframe(data.head())

elif option == "View Data":
    st.subheader("View Expense Data")
    data = query_data("SELECT * FROM expenses")
    st.dataframe(data)

elif option == "Visualize Insights":
    st.subheader("Spending Insights")
    query = "SELECT Category, SUM(Amount_Paid) as Total_Spent FROM expenses GROUP BY Category"
    data = query_data(query)

    st.bar_chart(data.set_index("Category"))

    # Pie Chart
    fig, ax = plt.subplots()
    ax.pie(data["Total_Spent"], labels=data["Category"], autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

elif option == "Run SQL Query":
    st.subheader("Run Custom SQL Query")
    query = st.text_area("Enter your SQL query:")
    if st.button("Execute"):
        try:
            data = query_data(query)
            st.dataframe(data)
        except Exception as e:
            st.error(f"An error occurred: {e}")

elif option == "Predefined SQL Queries":
    st.subheader("Predefined SQL Queries")
    query_name = st.selectbox("Select a query to run", list(SQL_QUERIES.keys()))
    query = SQL_QUERIES[query_name]
    if st.button("Run Query"):
        data = query_data(query)
        st.dataframe(data)
        if query_name == "Spending Trends Over Time":
            st.line_chart(data.set_index("Date"))
        elif query_name in ["Total Amount Spent per Category", "Payment Mode Analysis"]:
            st.bar_chart(data.set_index(data.columns[0]))

# Initialize the database
init_db()