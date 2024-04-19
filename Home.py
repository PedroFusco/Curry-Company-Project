import streamlit as st
from PIL import Image


st.set_page_config(
    page_title='Home'
)


image = Image.open("logo.png")

st.sidebar.image(image=image, width=300)

st.sidebar.markdown("# Curry Company")

st.sidebar.markdown("## Fastest Delivery in Town")
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth dashboard foi consttruido para acompanhar as métricas de crescimento dos Entregaores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
         - Visão Gerencial: Métricas gerais de comportamento
         - Visão Tática: Indicadores semanais de crescimento
         - Visão Geográfica: Insights de geolocalização
    - Visão Entregadores:
         - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurqantes:
         - Indicadores semanais de crescimento dos restaurantes
    ### Para dúvidas contate:
         - pedrofusconogueira@gmail.com
    """
)