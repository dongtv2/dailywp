import streamlit as st
import sqlite3
import pandas as pd
from functions.flightplan_process import clean_dataframe, get_all_REG_preflight, get_all_REG_nightstop


# Connect to the database
# Fetch data from the database
def fetch_mainbase_data():
    conn = sqlite3.connect('moc.db')
    query = "SELECT * FROM mainbase"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
def fetch_ac_data():
    conn = sqlite3.connect('moc.db')
    query = "SELECT * FROM aclist"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
mainbase = ['SGN', 'HAN', 'DAD', 'CXR', 'HPH', 'VII', 'VCA', 'PQC']
df_ac = fetch_ac_data()

tabs = st.tabs(['Read Flight Plan', 'Flight Plan Cleaned', 'Night stop & Preflight','Export data into AMOS'])

with tabs[0]:
    st.write('Read flightplan')
    try:
        col1, col2 = st.columns(2)

        with col1:
            st.write('Please upload a flightplan day 1')
            uploaded_file_day1 = st.file_uploader("Choose a file", key='upload_file_1')
            df_day1 = pd.read_excel(uploaded_file_day1) if uploaded_file_day1 else None
            st.write("File uploaded" if df_day1 is not None else 'Please upload a file')

        with col2:
            st.write('Please upload a flightplan day 2')
            uploaded_file_day2 = st.file_uploader("Choose a file", key='upload_file_2')
            df_day2 = pd.read_excel(uploaded_file_day2) if uploaded_file_day2 else None
            st.write("File uploaded" if df_day2 is not None else 'Please upload a file')
    except Exception as e:
        st.error(e)


with tabs[1]:
    st.write('Flight Plan Cleaned')
    try:
        col1, col2 = st.columns(2)

        with col1:
            st.write('Flight Plan Day 1')
            if df_day1 is not None:
                with st.expander('Click to see the flight data day 1'):
                    df_day1 = clean_dataframe(df_day1)
                    # df_day1 = adjust_sta_std_datetime(df_day1)
                    st.write(df_day1)

            else:
                st.write('No file uploaded for day 1')

        with col2:
            st.write('Flight Plan Day 2')
            if df_day2 is not None:
                with st.expander('Click to see the flight data day 2'):
                    df_day2 = clean_dataframe(df_day2)
                    # df_day2 = adjust_sta_std_datetime(df_day2)
                    st.write(df_day2)

            else:
                st.write('No file uploaded for day 2')
    except Exception as e:
        st.error(e)
with tabs[2]:
    st.subheader('Nighstop Day1 and Preflight Day 2')
    try:
        col1, col2 = st.columns(2)
        with col1:
            with st.expander('Get all Night Stop in DAY 1', expanded= True):
                df_nighstop_day1 = get_all_REG_nightstop(df_day1, mainbase)
                st.write(df_nighstop_day1)
        with col2:
            with st.expander('Get all Preflight in DAY 2', expanded=True):
                df_preflight_day2 = get_all_REG_preflight(df_day2, mainbase)
                st.write(df_preflight_day2)
    except Exception as e:
        st.error(e)

with tabs[3]:

    try:
        #Join df_ac with df_nighstop_day1 and df_preflight_day2
        st.markdown(""" ### Join 3 bảng AC, NS, PREFLIGHT""")
        wp_date = st.selectbox('DATE', df_day1['DATE'].unique())
        # Merge df_ac with df_nighstop_day1
        df_nightstop_ac = pd.merge(df_ac, df_nighstop_day1, on='REG', how='outer')
        # Merge df_nightstop_ac with df_preflight_day2
        df_final = pd.merge(df_nightstop_ac, df_preflight_day2, on='REG', how='outer')


        ## Drop các cols sau : DATE_x,Route_x,FLT_x, AC_x, DEP_x, STD_x, DATE_y, Route_y, FLT_y,.AC_y, ARR_y, STD_y, STA_y
        df_final.drop(columns=['TYPE','Route_x', 'FLT_x', 'AC_x', 'DEP_x', 'STD_x' , 'Route_y', 'FLT_y', 'AC_y', 'ARR_y', 'STA_y'], inplace=True)

        ## Kiểm tra ARR_x và DEP_y có giống nhau không
        df_final['Check'] = df_final['ARR_x'] == df_final['DEP_y']



        # Safely convert DATE_x to datetime, coercing errors to NaT
        df_final['DATE_x'] = pd.to_datetime(df_final['DATE_x'], errors='coerce')
        df_final['DATE_y'] = pd.to_datetime(df_final['DATE_y'], errors='coerce')

        # Format DATE_x, replacing NaT with a placeholder
        df_final['DATE_x'] = df_final['DATE_x'].apply(
            lambda x: x.strftime('%d.%b.%Y') if pd.notnull(x) else 'N/A'
        )
        df_final['DATE_y'] = df_final['DATE_y'].apply(
            lambda x: x.strftime('%d.%b.%Y') if pd.notnull(x) else 'N/A'
        )


        # Function to convert time to minutes
        def time_to_minutes(time_str):
            try:
                time = pd.to_datetime(time_str, format='%H:%M')
                return time.hour * 60 + time.minute
            except:
                return None  # Handle invalid or missing values


        # Apply the function to both columns
        df_final['STA_x'] = df_final['STA_x'].apply(time_to_minutes)
        df_final['STD_y'] = df_final['STD_y'].apply(time_to_minutes)

        # Xử lý dữ liệu cộ WPNO
        formatted_date = wp_date.replace('/', '')

        # Create the WPNO column
        df_final['WPNO'] = df_final['REG'] + '-OWP-' + formatted_date + '-REV00'

        # Thêm cột CLASS = L, PRIO = PRI1, MAIN-PROVIDE = VJC
        df_final['WP-STATUS'] = 'OPEN'
        df_final['DESCRIPTION'] = 'DAIL WORKPACKAGE'
        df_final['CLASS'] = 'L'
        df_final['PRIO'] = 'PRI1'
        df_final['MAIN-PROVIDE'] = 'VJC'

        # ĐỔi tên DATE_x thành START-DATE, DATE_y thành END-DATE, STA_x thành START-TIME, STD_y thành END-TIME
        df_final.rename(columns={'REG':'AIRCRAFT','ARR_x':'STATION','DATE_x': 'START-DATE', 'DATE_y': 'END-DATE', 'STA_x': 'START-TIME', 'STD_y': 'END-TIME'}, inplace=True)
        # Sắp xêp columns theo thứ tự WPNO, AIRCRAFT, DESCRIPTION,WP-STATUS,STATION,START-DATE, START-END, END-DATE, END-TIME, CLASS, PRIO, MAIN-PROVIDE
        df_final = df_final[['WPNO', 'AIRCRAFT', 'DESCRIPTION', 'WP-STATUS', 'STATION', 'START-DATE', 'START-TIME', 'END-DATE', 'END-TIME',
                             'CLASS', 'PRIO', 'MAIN-PROVIDE','Check']]

        # Display the table in Streamlit
        st.dataframe(df_final)

    except Exception as e:
        st.error(e)