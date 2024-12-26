import streamlit as st
import sqlite3
import pandas as pd

# Database connection
def create_connection():
    conn = sqlite3.connect('moc.db')
    return conn

# Fetch data from the database
def fetch_mainbase_data():
    conn = sqlite3.connect('moc.db')
    query = "SELECT * FROM mainbase"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
# Insert data into the database
def insert_mainbase_data(id, mainbase):
    conn = create_connection()
    c = conn.cursor()
    c.execute('INSERT INTO mainbase (ID, MAINBASE) VALUES (?, ?)', (id, mainbase))
    conn.commit()
    conn.close()

tab1,tab2,tab3,tab4 = st.tabs(["Main Base List ","Create New Mainbase","Flight Plan","Flight Schedule"])

with tab1:
    st.title("Main Base")
    mainbase = fetch_mainbase_data()
    st.write(mainbase)