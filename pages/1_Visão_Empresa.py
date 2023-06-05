#libraries
from haversine import haversine, Unit
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

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
st.set_page_config(page_title='Visão Empresa', layout='wide')

st.markdown("# Marketplace - Visão Empresa")

#================================
#Barra lateral
#================================
image = Image.open("alvo.jpg")

st.sidebar.image(image=image, width=300)

st.sidebar.markdown("# Curry Company")

st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

st.sidebar.markdown("### Selecione uma data limite")
date_slider = st.sidebar.slider(
    "Limite da data.",
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format="DD-MM-YYYY"
)

st.sidebar.markdown("""---""")

st.sidebar.markdown("### Selecione as condições de trânsito")
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
tab1, tab2, tab3 = st.tabs(["Visão Gerencial", "Visão Tática", "Visão Geográfica"])


#Visão Gerencial
with tab1:

    #Gráfico de barra
    with st.container():
        fig_pedidos_dia = func.qtde_pedidos_dia(df)
        st.markdown("## Quantidade de Pedidos por Dia")
        st.plotly_chart(fig_pedidos_dia, use_container_width=True)

    st.markdown("""---""")

    with st.container():

        #Criando colunas
        col1, col2 = st.columns(2)

        with col1:
            fig_pedidos_trafego = func.qtde_pedidos_trafego(df)
            st.markdown("### Distribuição dos Pedidos por Tipo de Tráfego")
            st.plotly_chart(fig_pedidos_trafego , use_container_width=True)

        with col2:
            fig_cidade_trafego = func.qtde_pedidos_trafego_cidade(df)
            st.markdown("### Volume de Pedidos por Cidade e Tipo de Tráfego")
            st.plotly_chart(fig_cidade_trafego, use_container_width=True)


#Visão Tática
with tab2:
    with st.container():
        fig_pedidos_semana = func.qtde_pedidos_semana(df)
        st.markdown("## Pedidos por Semana")
        st.plotly_chart(fig_pedidos_semana, use_container_width=True)

    st.markdown("""---""")
    
    #Pedidos por entregador por semana
    with st.container():
        fig_pedidos_entregadores_semana = func.qtde_pedidos_semana_entregadores(df)
        st.markdown("## Quantidade de Pedidos por Entregador por Semana")
        st.plotly_chart(fig_pedidos_entregadores_semana, use_container_width=True)

#Visão Geográfica
with tab3:
    #Mapa com as cidades cadastradas
    with st.container():
        map = func.map_restaurantes(df)
        st.markdown("## Localização Central das Cidade e Tipo de Tráfego")          
        folium_static(map, width=1350, height=800)