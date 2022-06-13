import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from pyvis.network import Network
import streamlit.components.v1 as components
import warnings
from pandas.core.common import SettingWithCopyWarning
import networkx as nx
from scipy.stats import gmean
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

with st.echo(code_location='below'):

    tabs = ['Визуализация данных по потреблению в США',
            'Вакансии "Пятёрочки". Граф',
            'Имитация каталога в "Перекрёстке"']

    tab = st.sidebar.radio('Выберите часть проекта', tabs)
    if tab == tabs[0]:

        st.title('Визуализация данных по потреблению в США')

        df = pd.read_csv("USA_consumption.csv")
        years = df.columns.tolist()[1:]
        df_melt = pd.melt(df.drop(df.tail(1).index), id_vars=['Goods'], value_vars=years)
        df1 = df.set_index('Goods')
        df1

        st.write('В БД выделено 73 компонента потребления. На каждый тратится больше миллиарда долларов.'
                 'Для построения следующего графика выберите минимальное кол-во миллионов долларов, потраченных '
                 'на потребление. Кстати, легенда на графике кликабельна!')
        money = st.slider('Выберите кол-во миллионов', 1000, 1000000, 200000)


        i, =np.where(df_melt['value']>money)
        y = pd.DataFrame(df_melt['value'][i[1:]])
        df_merged = df_melt.merge(y, on='value', how='inner')

        selection = alt.selection_multi(fields=['Goods'], bind='legend')
        line = alt.Chart(df_merged).mark_area().encode(
            alt.X("variable", title="Year"),
            alt.Y('value', title='Expenditures'),
            color="Goods",
            tooltip='Goods',
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2))).add_selection(selection)
        st.altair_chart(alt.layer(
            line).properties(width=900, height=500))


        array = (1 + np.diff(df1) / np.delete(np.array(df1), 18, axis=1)) * 100
        df2 = pd.DataFrame(gmean(array, axis=1), index=list(df['Goods']), columns=['Avg growth rate'])
        df_sorted = df2.sort_values(by=['Avg growth rate'], ascending=False)
        df_sorted['Avg growth rate'] = df_sorted['Avg growth rate'] - 100
        df3 = df_sorted.head(5).reset_index()
        df3 = df3.merge(df, how='left', left_on='index', right_on='Goods')
        df4 = df_sorted.tail(5).reset_index()
        df4 = df4.merge(df, how='left', left_on='index', right_on='Goods')

        line1 = alt.Chart(df3).mark_bar().encode(
            alt.X("Avg growth rate", title="Average growth rate, %"),
            alt.Y("index", title='Expenditures', sort='-x'),
            color='Avg growth rate', tooltip='Goods')

        st.subheader("Посчитаем средний темп прироста по всем компонентам потребления")
        st.write('Ниже Вы можете увидеть те части потребления, расходы на которые росли в среднем больше всего')

        st.altair_chart(alt.layer(
            line1).properties(width=700, height=300))

        line2 = alt.Chart(df4).mark_bar().encode(
            alt.X("Avg growth rate", title="Average growth rate, %"),
            alt.Y("index", title='Expenditures', sort='-x'),
            color='Avg growth rate', tooltip='Goods')

        st.write('Ниже Вы можете увидеть те части потребления, расходы на которые росли в среднем меньше всего')
        st.altair_chart(alt.layer(
            line2).properties(width=700, height=300))


    elif tab == tabs[1]:
        st.image('Rabota-v-Pyaterochke.jpg')
        st.title('Вакансии "Пятёрочки"')
        st.write('После скреппинга сайта "Пятёрочки" с помощью Силениума я создал базу данных'
                 ' по всем вакансиям, которые они предоставляют. Вот, что получилось:')
        vac = pd.read_csv('Vacancies.csv')
        vac

        @st.cache(suppress_st_warning=True)
        def vacancies():
            vacancies = pd.read_csv('Vacancies.csv')
            df_graph = vacancies[['Должность', 'Адрес']]
            for i in range(len(df_graph['Адрес'])):
                df_graph['Адрес'][i] = " ".join(df_graph['Адрес'][i].split()[3:])
            return df_graph

        st.write('Ниже можно нарисовать интерактивынй граф, демонстрирующий связь между должностью и адресами.')

        job_list = list(vacancies()['Должность'].unique())
        job_graph = st.selectbox("Выберите должность:", job_list, index=1)
        graph = nx.Graph([(job, addr) for (job, addr) in vacancies().values])
        subgraph = graph.subgraph([job_graph] + list(graph.neighbors(job_graph)))
        net = Network(bgcolor='red', font_color='white')
        net.from_nx(subgraph)
        net.show("job_graph.html")
        file = open("job_graph.html", 'r', encoding='utf-8')
        src = file.read()
        components.html(src, height=500, width=5000)

    elif tab == tabs[2]:
        st.image('Perekrestok.jpeg')
        st.header('Имитация каталога в "Перекрёстке"')
        st.subheader('Изначально у меня была идея сделать телеграм-бота с похожим функционалом,'
                     ' но пусть будет то же самое, только здесь)')
        st.write('То, как каталог был добыт, написано в ipynb-файле.')

        catalog = pd.read_csv('Catalog.csv')
        slovo = st.text_input('Поиск по названию товара', 'Coca')

        show_board = []
        for i in range(len(catalog['Name'])):
            if slovo in catalog['Name'][i]:
                show_board.append([
                catalog['Name'][i],
                catalog['Price'][i],
                catalog['Discount'][i]])
        show_board = pd.DataFrame(show_board, columns=['Товар', 'Цена', 'Скидка'])


        try:
            st.write("Перекрёсток рекомендует Вам:")
            show_board1= show_board.sample(5)
            show_board1

            st.write("Товар с самой большой скидкой из найденных:")
            show_board2 = show_board.sort_values(by=['Скидка'],ascending=False).head(1)
            show_board2

            st.write("Самый дорогой товар из найденных:")
            show_board3 = show_board.sort_values(by=['Цена'], kind='stable', ascending=False).head(1)
            show_board3

            st.write("Самый дешевый товар из найденных:")
            show_board4 = show_board.sort_values(by=['Цена'], ascending=True).head(1)
            show_board4
            st.balloons()
        except ValueError:
            st.error("Товар не найден. Попробуйте написать другой запрос")








