#libraries
from haversine import haversine, Unit
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image

import func

#Carregando os dados
df = pd.read_csv("dados/curry_df.csv")

#Retirando espaços antes e depois dos dados
df = func.retira_espaco(df)
#Retirando valores "NaN"
df = func.limpa_nan(df)
#Tipando os dados
df = func.tipa_dados(df)



#================================
#Stremlit
#================================
st.set_page_config(page_title='Visão Entregadores', layout='wide')
st.markdown("# Marketplace - Visão Entregadores")

#================================
#Barra lateral
#================================
image = Image.open("alvo.jpg")

st.sidebar.image(image=image, width=300)

st.sidebar.markdown("# Curry Company")

st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Selecione uma data limite")
date_slider = st.sidebar.slider(
    "Limite da data.",
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format="DD-MM-YYYY"
)

st.sidebar.markdown("""---""")


traffic_options = st.sidebar.multiselect(
    "Condições de trânsito.",
    ["Low", "Medium", "High", "Jam"],
    default=["Low", "Medium", "High", "Jam"]
)
st.sidebar.markdown("""---""")


df = df[df["Order_Date"] <= date_slider]
df = df[df["Road_traffic_density"].isin(list(traffic_options))]
#================================
#Layout no Streamlit
#================================
tab1, tab2, tab3 = st.tabs(["visão gerencial", "", ""])




with tab1:
    with st.container():
        st.markdown("## Métricas Basicas")
        col1, col2, col3, col4 = st.columns(4, gap="large")
        with col1:
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric("Maior idade entre os entregadores:", maior_idade)

        with col2:
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric("Menor idade entre os entregadores:", menor_idade)

        with col3:
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
            col3.metric("Melhor condição de veículo:", melhor_condicao)

        with col4:
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric("Pior condição de veículo:", pior_condicao)
    

    with st.container():
        st.markdown("""---""")
        st.markdown("## Avaliações")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Avaliações médias por entregadores")
            df_avg_ratings_per_deliver = func.avaliacao_media_entregadores(df)
            st.dataframe(df_avg_ratings_per_deliver)

        with col2:
            st.markdown("### Avaliação média e desvio padão por trânsito")
            delivery_mean_std = func.avaliacao_media_transito(df)
            st.dataframe(delivery_mean_std)


            st.markdown("### Avaliação média e desvio padrão por clima")
            weather_mean_std = func.avaliacao_media_clima(df)
            st.dataframe(weather_mean_std)


    with st.container():
        st.markdown("""---""")
        st.markdown("## Velocidade de Entrega")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Top entregadores mais rápidos")
            mais_rapido_por_cidade = func.entregadores_rapidos(df)
            st.dataframe(mais_rapido_por_cidade)

        
        with col2:
            st.markdown("### Top entregadores menos rápidos")
            mais_lentos_por_cidade = func.entregadores_lentos(df)
            st.dataframe(mais_lentos_por_cidade)
