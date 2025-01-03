import streamlit as st
import os
import pandas as pd
from datetime import datetime, time, timedelta
import numpy as np
from datetime import datetime

main_bases = ['SGN', 'HAN', 'DAD', 'CXR', 'HPH', 'VII', 'VCA', 'PQC']


def clean_dataframe(df):
    """
    Hàm làm sạch DataFrame:
    1. Xóa các cột theo chỉ số (3 và 8).
    2. Xóa các hàng từ chỉ số 0 đến 5.
    3. Reset lại chỉ số.
    4. Sử dụng hàng đầu tiên làm header.
    5. Xóa các hàng có giá trị NaN trong cột 'DATE'.
    6. Xóa 2 dòng cuối cùng.
    7. Xóa chuỗi 'VN-' trong cột 'REG'.
    8. Reset lại chỉ số lần cuối.

    Tham số:
        df (pd.DataFrame): DataFrame gốc.

    Trả về:
        pd.DataFrame: DataFrame đã được làm sạch.
    """
    # Bước 1: Xóa các cột thứ 3 và thứ 8
    df.drop(df.columns[[3, 8]], axis=1, inplace=True)

    # Bước 2: Xóa các hàng từ 0 đến 5
    df = df.drop(df.index[0:6])

    # Bước 3: Reset lại chỉ số
    df = df.reset_index(drop=True)

    # Bước 4: Lấy hàng đầu tiên làm header
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])

    # Bước 5: Loại bỏ các dòng có giá trị NaN trong cột 'DATE'
    df = df.dropna(subset=['DATE'])

    # Bước 6: Xóa 2 dòng cuối cùng
    df = df[:-2]

    # Bước 7: Xóa chuỗi 'VN-' trong cột 'REG'
    if 'REG' in df.columns:
        df['REG'] = df['REG'].str.replace('VN-', '', regex=False)

    # Bước 8: Reset lại chỉ số lần cuối
    df = df.reset_index(drop=True)

    return df

# Get the pre-flight, transit, and night-stop flights
def get_all_REG_preflight(df, main_bases):
    """
    Hàm lấy dòng đầu tiên của mỗi REG và lọc các chuyến bay có DEP_1 thuộc mainbase.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.
        main_bases (list): Danh sách các mainbase.

    Trả về:
        pd.DataFrame: DataFrame chứa các chuyến bay đã được lọc.
    Example:
    - Mặc định trả về DataFrame chứa các chuyến bay có DEP_1 thuộc mainbase
    - Lọc SGN, or HAN...
        df_day1_preflight_sgn = get_all_REG_preflight(df_day1_combined,['SGN'])
    """
    # Nhóm theo REG và lấy dòng đầu tiên của mỗi REG
    first_rows = df.groupby('REG').first().reset_index()

    # Lọc các chuyến bay có DEP_1 thuộc mainbases
    filtered_df = first_rows[first_rows['DEP'].isin(main_bases)]

    # Sort STD_1 acsending
    filtered_df = filtered_df.sort_values(by='STD')
    # Reset index
    filtered_df.reset_index(drop=True, inplace=True)

    return filtered_df


def get_all_REG_nightstop(df, main_bases):
    """
    Tìm những tàu nightstop và không bay trong đêm.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.
        main_bases (list): Danh sách các mainbase.

    Trả về:
        pd.DataFrame: DataFrame chứa các tàu nightstop.
    """
    # Lấy last row của mỗi REG
    last_rows = df.groupby('REG').last().reset_index()

    # Kiểm tra xem REG có bay trong đêm hay không
    nightstop = last_rows[last_rows['ARR'].isin(main_bases)]

    # Reset index
    nightstop.reset_index(drop=True, inplace=True)

    # Sort STA
    nightstop.sort_values('STA')

    return nightstop

def combine_flights(df):
    """
    Hàm kết hợp các chuyến bay theo nhóm `REG` và `AC`:
    1. Ghép hai chuyến bay liên tiếp thành một hàng.
    2. Trả về DataFrame mới với các cột theo định dạng yêu cầu.

    Tham số:
        df (pd.DataFrame): DataFrame gốc.

    Trả về:
        pd.DataFrame: DataFrame đã kết hợp theo định dạng mong muốn.
    """
    combined_rows = []

    # Nhóm dữ liệu theo `REG` và `AC`
    grouped = df.groupby(['REG', 'AC'])

    for _, group in grouped:
        # Reset lại index cho mỗi group
        group = group.reset_index(drop=True)

        # Xử lý các chuyến bay theo từng cặp
        for i in range(len(group)):
            # Lấy dữ liệu của chuyến bay hiện tại
            current_flight = [
                group.loc[i, 'DATE'], group.loc[i, 'Route'],
                group.loc[i, 'FLT'], group.loc[i, 'REG'],
                group.loc[i, 'AC'], group.loc[i, 'DEP'],
                group.loc[i, 'ARR'], group.loc[i, 'STD'],
                group.loc[i, 'STA']
            ]

            # Kiểm tra nếu có chuyến bay tiếp theo
            if i + 1 < len(group):
                # Thêm FLT, DEP, ARR, STD, STA của chuyến bay tiếp theo
                current_flight.extend([
                    group.loc[i + 1, 'FLT'],
                    group.loc[i + 1, 'DEP'], group.loc[i + 1, 'ARR'],
                    group.loc[i + 1, 'STD'], group.loc[i + 1, 'STA']
                ])
            else:
                # Nếu không có chuyến bay tiếp theo, để trống FLT, DEP, ARR, STD, STA
                current_flight.extend(['', '', '', '', ''])

            combined_rows.append(current_flight)

    # Tạo DataFrame kết quả
    result_df = pd.DataFrame(combined_rows, columns=[
        'DATE', 'Route', 'FLT_1', 'REG', 'AC',
        'DEP_1', 'ARR_1', 'STD_1', 'STA_1',
        'FLT_2', 'DEP_2', 'ARR_2', 'STD_2', 'STA_2'
    ])

    return result_df


# Xú lý dữ liệu của STA và STD
def adjust_sta_std_datetime(df):
    """
    Điều chỉnh thời gian STA dựa trên ngày và so sánh với STD.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.

    Trả về:
        pd.DataFrame: DataFrame đã điều chỉnh thời gian STA.
    """
    # Kết hợp DATE với STA để tạo datetime
    df['STA'] = pd.to_datetime(df['DATE'] + ' ' + df['STA'], format='%d/%m/%y %H:%M', errors='coerce')
    df['STD'] = pd.to_datetime(df['DATE'] + ' ' + df['STD'], format='%d/%m/%y %H:%M', errors='coerce')

    # Nếu STA < STD, điều chỉnh STA thuộc về ngày hôm sau
    df.loc[df['STA'] < df['STD'], 'STA'] += pd.Timedelta(days=1)

    return df