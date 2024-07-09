import streamlit as st
from signals import Signals

st.set_page_config(
    page_title="Signal Convert",
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

st.title('Signal Convert')


with st.sidebar:
    st.title('Навигация')
    st.page_link(
        page='main.py',
        label='Home 🏠',
        use_container_width=True,
        help='Go to Home page',
        disabled=True
    )
    st.page_link(
        page='pages/1_file.py',
        label='Convert File 📁',
        use_container_width=True
    )
    st.markdown('---')


signals = Signals('static/signals.json')

st.markdown('---')

with st.form(key='convert_signal'):
    st.text('Конвертировать параметр сигнала в HEX и DEC')
    signal = st.text_input('Введите параметр сигнала',
                           value='X100',
                           max_chars=8,
                           help='Пример: X101, Y1, T1013, M20, V14747, CV215'
    )

    if st.form_submit_button('Конвертировать', type='primary'):
        try:
            result = signals.get_signals_by_param(signal)
            st.dataframe(result, use_container_width=True)
        except ValueError as e:
            st.error(str(e))


st.markdown('---')


with st.form(key='convert_signals'):
    st.text('Конвертировать параметры сигналов в HEX и DEC')
    signals_list = st.text_area(
        'Введите параметры сигналов',
        value='X0\nY1\nT1013\nM20\nV14747\nCV215',
        max_chars=1000,
        help='Пример: X101, Y1, T1013, M20, V14747, CV215'
    )

    if st.form_submit_button('Конвертировать', type='primary'):
        try:
            result = signals.get_signals_by_params(signals_list.split('\n'))
            st.dataframe(result, use_container_width=True)
        except ValueError as e:
            st.error(str(e))
