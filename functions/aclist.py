# Database connection
import sqlite3
import pandas as pd
import streamlit as st

def create_connection():
    conn = sqlite3.connect('moc.db')
    return conn

# Fetch data from the database
def fetch_aclist_data():
    conn = sqlite3.connect('moc.db')
    query = "SELECT * FROM aclist"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Insert data into the database
def insert_aclist_data(reg, type):
    conn = create_connection()
    c = conn.cursor()
    c.execute('INSERT INTO aclist (REG, TYPE) VALUES (?, ?)', (reg, type))
    conn.commit()
    conn.close()

# Delete data from the database
def delete_aclist_data(id):
    conn = create_connection()
    c = conn.cursor()
    c.execute('DELETE FROM aclist WHERE ID = ?', (id,))
    conn.commit()
    conn.close()
# Update data in the database
def update_aclist_data(id, reg, type):
    conn = create_connection()
    c = conn.cursor()
    c.execute('UPDATE aclist SET REG = ?, TYPE = ? WHERE ID = ?', (reg, type, id))
    conn.commit()
    conn.close()