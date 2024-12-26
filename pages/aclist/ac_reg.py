import streamlit as st
import sqlite3
import pandas as pd

# Database connection
def create_connection():
    conn = sqlite3.connect('moc.db')
    return conn

# # Create table function
# def create_table(conn):
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS aclist
#                  (ID INTEGER PRIMARY KEY AUTOINCREMENT,
#                  REG TEXT NOT NULL,
#                  TYPE TEXT NOT NULL)''')
#     conn.commit()

# Fetch data from the database
def fetch_data():
    conn = create_connection()
    query = "SELECT * FROM aclist"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Insert data into the database
def insert_data(reg, type):
    if not reg or not type:  # Check if REG and TYPE are provided
        st.error("Both REG and TYPE must be provided.")
        return
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO aclist (REG, TYPE) VALUES (?, ?)", (reg, type))
    conn.commit()
    conn.close()
    st.rerun()  # Refresh the page

# Update data in the database
def update_data(id, reg, type):
    if not reg or not type:  # Check if REG and TYPE are provided
        st.error("Both REG and TYPE must be provided.")
        return
    conn = create_connection()
    c = conn.cursor()
    c.execute("UPDATE aclist SET REG = ?, TYPE = ? WHERE ID = ?", (reg, type, id))
    conn.commit()
    conn.close()
    st.rerun()  # Refresh the page

# Delete data from the database
def delete_data(id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM aclist WHERE ID = ?", (id,))
    conn.commit()
    conn.close()
    st.rerun()  # Refresh the page


# Display the header
st.title("Aircraft Management")

# Fetch the records from the database
df = fetch_data()

# CRUD operation forms
tab1, tab2, tab3, tab4 = st.tabs(["Add Aircraft", "Update Aircraft", "Delete Aircraft", "View Aircraft"])

# --- CREATE FORM ---
with tab1:
    st.subheader("Add New Aircraft")
    reg = st.text_input("Enter Aircraft Registration (REG)")
    type = st.text_input("Enter Aircraft Type (TYPE)")
    if st.button("Add Aircraft"):
        insert_data(reg, type)
        st.success(f"Aircraft {reg} added successfully!")

# --- UPDATE FORM ---
with tab2:
    st.subheader("Update Aircraft Information")
    update_id = st.selectbox("Select Aircraft to Update", df["REG"].tolist())
    update_reg = st.text_input("Enter New Aircraft Registration (REG)", value=df[df["REG"] == update_id]["REG"].iloc[0])
    update_type = st.text_input("Enter New Aircraft Type (TYPE)", value=df[df["REG"] == update_id]["TYPE"].iloc[0])
    if st.button("Update Aircraft"):
        update_data(update_id, update_reg, update_type)
        st.success(f"Aircraft {update_id} updated successfully!")

# --- DELETE FORM ---
with tab3:
    st.subheader("Delete Aircraft")
    delete_reg = st.selectbox("Select Aircraft to Delete", df["REG"].tolist())
    if st.button("Delete Aircraft"):
        delete_id = df[df["REG"] == delete_reg]["ID"].values[0]
        delete_data(delete_id)
        st.success(f"Aircraft {delete_reg} deleted successfully!")

with tab4:
    st.subheader("View Aircraft")
    df = fetch_data()  # Refresh the data after any CRUD operation
    st.table(df.reset_index(drop=True))  # Hide the index column