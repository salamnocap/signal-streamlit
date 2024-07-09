import io
import os
import csv
import streamlit as st
import pandas as pd

from datetime import datetime
from signals import Signals

TITLE = 'Convert File'
PREPROCESSED_PATH = 'static/preprocessed'

st.set_page_config(
    page_title=TITLE,
    page_icon="🚨",
    layout="wide"
)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNavItems"]{
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.title('Навигация')
    st.page_link(
        page='main.py',
        label='Домой 🏠',
        use_container_width=True,
        help='Вернуться на главную страницу',
    )
    st.page_link(
        page='pages/1_file.py',
        label='Конвертировать файл 📁',
        use_container_width=True,
        help='В этом разделе вы можете конвертировать файл сигналов',
        disabled=True
    )
    st.markdown('---')

signals = Signals('static/signals.json')


def create_excel_buffer(df: pd.DataFrame) -> io.BytesIO:
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


def load_example_file(filepath: str) -> pd.DataFrame:
    return pd.read_excel(filepath)


def change_group_name(name: str) -> pd.DataFrame:
    data = pd.read_csv('static/template.csv')
    data['groups'][1] = name
    return data


def save_to_file(df1: pd.DataFrame, df2: pd.DataFrame, type: str) -> io.BytesIO:
    buffer = io.BytesIO()
    df1.to_csv(buffer, header=False, index=False)
    buffer.seek(0, io.SEEK_END)
    df2.to_csv(buffer, index=False, mode='a')
    buffer.seek(0)
    if type == 'xlsx':
        data = pd.read_csv(buffer)
        data = data.rename(columns=lambda x: x if x in ['name', 'parent'] else '')
        buffer = io.BytesIO()
        data.to_excel(buffer, index=False)
        buffer.seek(0)
    return buffer


st.title(TITLE)
st.text('Конвертировать параметров сигнал в HEX и DEC')

st.markdown('---')

example_file_path = 'static/ШУ1_Сигналы.xlsx'
example_df = load_example_file(example_file_path)
example_buffer = create_excel_buffer(example_df)

st.markdown('### Пример входного файла')
st.dataframe(example_df, height=200, use_container_width=True)
column1, column2 = st.columns([4,1])
column1.markdown('---')
column2.download_button(
    label='Скачать 📥',
    data=example_buffer,
    file_name='ШУ1_Сигналы.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    help='Скачать пример входного файла',
    use_container_width=True
)

st.markdown('---')

uploaded_file = st.file_uploader('Выберите файл:',
                                 type=['xlsx', 'csv'],
                                 help='Загрузите файл',
                                 label_visibility='collapsed')

if uploaded_file is not None:
    if uploaded_file.type == 'text/csv':
        uploaded_df = pd.read_csv(uploaded_file)
    else:
        uploaded_df = pd.read_excel(uploaded_file)
    st.write("Исходные данные:")
    uploaded_df = st.data_editor(uploaded_df, use_container_width=True)
    name = st.text_input('Введите наименование',
                         placeholder='Silos, NewGran',
                         max_chars=1000,
                         help='Введите наименование группы')

    if st.button('Конвертировать', type='primary', help='Конвертировать данные'):
        converted_df = signals.get_signals_by_file_params(uploaded_df)
        converted_df['group'] = name
        groups_data = change_group_name(name)
        st.markdown('---')
        st.write("Конвертированные данные:")
        st.dataframe(converted_df, use_container_width=True)

        data_csv = save_to_file(groups_data, converted_df, 'csv')
        data_xlsx = save_to_file(groups_data, converted_df, 'xlsx')

        col1, col2 = st.columns(2)
        col1.download_button(
            label='Скачать 📄(.csv)',
            type='primary',
            data=data_csv,
            file_name=f'converted_signals_{datetime.now()}.csv',
            mime='application/octet-stream',
            use_container_width=True,
            help='Скачать в формате CSV'
        )
        col2.download_button(
            label='Скачать (.xlsx)',
            type='primary',
            data=data_xlsx,
            file_name=f'converted_signals_{datetime.now()}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True,
            help='Скачать в формате XLSX'
        )
