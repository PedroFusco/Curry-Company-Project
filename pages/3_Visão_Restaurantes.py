#libraries
from haversine import haversine, Unit
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np

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
st.set_page_config(page_title='Visão Restaurantes', layout='wide')
st.markdown("# Marketplace - Visão Restaurantes")

#================================
#Barra lateral
#================================
image = Image.open("logo.png")

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
    ["Baixo", "Médio", "Alto", "Congestionado"],
    default=["Baixo", "Médio", "Alto", "Congestionado"]
)
st.sidebar.markdown("""---""")

map1 = {"High":"Alto", "Jam":"Congestionado", "Low":"Baixo", "Medium":"Médio"}
map2 = {"conditions Cloudy":"Nublado", "conditions Fog":"Nevoeiro", "conditions Sandstorms":"Tempestades de areia",
        "conditions Stormy":"Tempestuoso","conditions Sunny":"Ensolarado","conditions Windy":"Ventoso"}
map3 = {"Urban":"Urbano", "Semi-Urban":"Semi-Urbano", "Metropolitian":"Metropolitano"}

df["Road_traffic_density"] = df["Road_traffic_density"].map(map1)
df["Weatherconditions"] = df["Weatherconditions"].map(map2)
df["City"] = df["City"].map(map3)


df = df[df["Order_Date"] <= date_slider]
df = df[df["Road_traffic_density"].isin(list(traffic_options))]
#================================
#Layout no Streamlit
#================================
tab1, tab2, tab3 = st.tabs(["visão gerencial", "", ""])

with tab1:
    st.markdown("### Visão Geral")
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            entregadores_unicos = df['Delivery_person_ID'].nunique()
            col1.metric("Quantidade de entregadores:", entregadores_unicos)

        with col2:
            distancia_media = func.distancia_media(df)
            col2.metric("Distância média dos restaurantes", distancia_media)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            tempo_medio_festival = df[df['Festival'] == 'Yes']['Time_taken(min)'].mean().round()
            col1.metric("Tempo médio de entrega durante o Festival", tempo_medio_festival)

        with col2:
            desvio_padrao_festival = df[df['Festival'] == 'Yes']['Time_taken(min)'].std().round()
            col2.metric("Desvio padrão de entrega durante o Festival", desvio_padrao_festival)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            tempo_medio_Sfestival = df[df['Festival'] == 'No']['Time_taken(min)'].mean().round()
            col1.metric("Tempo médio de entrega fora do Festival", tempo_medio_Sfestival)

        with col2:
            desvio_padrao_Sfestival = df[df['Festival'] == 'No']['Time_taken(min)'].std().round()
            col2.metric("Desvio padrão de entrega fora do Festival", desvio_padrao_Sfestival)


    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Tempo médio e o desvio padrão de entrega por cidade")
            fig = func.tempo_medio_desvio(df)
            st.plotly_chart(fig,use_container_width=True)

        with col2:
            st.markdown("### Tempo médio e o desvio padrão por cidade e tráfego")
            tempo_media_cidade_tipo_trafego = func.tempo_medio_std_cidade_trafego(df)
            st.dataframe(tempo_media_cidade_tipo_trafego, width=500, height=400)
       
    st.markdown("""---""")
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Média da distancia por cidade")
            fig = func.media_distanci_cidade(df)
            st.plotly_chart(fig)
            

        with col2:
            st.markdown("### Media e desvio padrão do tempo no tráfego")
            fig = func.media_desvio_tempo_trafego(df)
            st.plotly_chart(fig)

    
