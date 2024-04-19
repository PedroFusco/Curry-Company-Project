import pandas as pd
import plotly.express as px
import folium
from haversine import haversine, Unit
import plotly.graph_objects as go
import numpy as np


#===================================================================================
#Funções de limpeza de dados
#=================================================================================
def retira_espaco(df):
    """
    Função que retira os espaços que possam existir antes e/ou depois de uma string 

    Input: Dataframe
    Output: Dataframe
    """
    columns = dict(df.dtypes == "object")
    strings = []
    for col in columns:
        if columns[col] == True:
            strings.append(col)
    for str in strings:
        df[str] = df[str].str.strip()
        
    return df


def limpa_nan(df):
    """
    função que retira os valores "NaN"do dataframe

    Input: Dataframe
    Output: Dataframe
    """
    df = df[~df["Delivery_person_Age"].str.contains("NaN")]
    df = df[~df["Delivery_person_Ratings"].str.contains("NaN")]
    df = df[~df["Time_Orderd"].str.contains("NaN")]
    df = df[~df["Weatherconditions"].str.contains("NaN")]
    df = df[~df["Road_traffic_density"].str.contains("NaN")]
    df = df[~df["multiple_deliveries"].str.contains("NaN")]
    df = df[~df["Festival"].str.contains("NaN")]
    df = df[~df["City"].str.contains("NaN")]
    df = df.reset_index(drop=True)

    return df


def tipa_dados(df):
    """
    Função para atribuir o tipo correto de dados de cada coluna

    Input: Dataframe
    Output: Dataframe
    """
    df["Delivery_person_Age"] = df["Delivery_person_Age"].astype( int )
    df["Delivery_person_Ratings"] = df["Delivery_person_Ratings"].astype( float )
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%d-%m-%Y")
    df["multiple_deliveries"] = df["multiple_deliveries"].astype( int )
    df["Time_taken(min)"] = df["Time_taken(min)"].replace(to_replace="\(min\) ", value="", regex=True).astype(int)
    
    return df

#====================================================================================================================
#Funções visão empresa
#====================================================================================================================
def qtde_pedidos_dia(df):
    """
    Calcula a quantidade de pedidos por dia e retorna um gráfico de barras

    Input: Dataframe
    Output: Gráfico de barras (plotly express)
    """
    pedidos_dia_df = df.groupby("Order_Date").agg({"ID":"count"}).reset_index().rename(columns={"ID":"Qtde_Pedidos"})
    pedidos_dia_df["Order_Date"] = pd.to_datetime(pedidos_dia_df["Order_Date"], format="%d-%m-%y")

    fig = px.bar(data_frame=pedidos_dia_df, x="Order_Date", y="Qtde_Pedidos",
                 labels={'Qtde_Pedidos':'Quantidade de Pedidos', "Order_Date":"Data"})
    fig.update_traces(marker_color='#E11B14')
    
    
    return fig
    

def qtde_pedidos_trafego(df):
    """
    Calcula a distribuição dos pedidos por tipo de tráfego retornando um gráfico de pizza

    Input: Dataframe
    Output: Gráfico de pizza (plotly express)
    """
    pedidos_trafego_df = df.groupby("Road_traffic_density").agg({"ID":"count"}).reset_index().rename(columns={"ID":"Qtde_Pedidos"})
    pedidos_trafego_df["entregas_perc"] = pedidos_trafego_df["Qtde_Pedidos"]/pedidos_trafego_df["Qtde_Pedidos"].sum()

    fig = px.pie(data_frame=pedidos_trafego_df, names="Road_traffic_density", values="entregas_perc",
                color_discrete_sequence=px.colors.sequential.RdBu)

    return fig


def qtde_pedidos_trafego_cidade(df):
    """
    Calcula o volume de pedidos por cidade e por tipo de tráfego retornando um gráfico de bolhas

    Input: Dataframe
    Output: Gráfico de bolhas (plotly express)
    """
    cidade_trafego_df = df.groupby(["City", "Road_traffic_density"]).agg({"ID":"count"}).reset_index().rename(columns={"ID":"Qtde_Pedidos"})
    fig = px.scatter(data_frame=cidade_trafego_df, x="City", y="Road_traffic_density", size="Qtde_Pedidos", color="City",
                     labels={'City':'Cidades', "Road_traffic_density":"Tipo de Tráfego"},
                     color_discrete_sequence=['#E11B14', '#F24A05', '#FFC106'])
    return fig


def qtde_pedidos_semana(df):
    """
    Calcula a quantidade de pedidos por semana e retorna um gráfico de linha com as informações

    Input: Dataframe
    Output: Gráfico de linhas (plotly6 express)
    """
    df["week_of_year"] = df["Order_Date"].dt.strftime("%U")
    pedidos_semana_df = df.groupby("week_of_year").agg({"ID":"count"}).reset_index().rename(columns={"ID":"Qtde_Pedido"})
    fig = px.line(data_frame=pedidos_semana_df, x="week_of_year", y="Qtde_Pedido",
                 labels={'week_of_year':'Número da Semana do Ano', "Qtde_Pedido":"Quantidade de Pedidos"})

    return fig


def qtde_pedidos_semana_entregadores(df):
    """
    Calcula a quantidade de pedidos por entregador por semana (pedidos por semana/entregadores únicos) e retorna gráfico de linha

    Input: Dataframe
    Output: Gráfico de linhas
    """
    temp_pedido_por_semana = df.groupby("week_of_year").agg({"ID":"count"}).reset_index().rename(columns={"ID":"Qtde_Pedidos"})
    temp_entregadores_por_semana = df.groupby("week_of_year").agg({"Delivery_person_ID":"nunique"}).reset_index().rename(columns={"Delivery_person_ID":"Entregadores_Unicos"})

    pedidos_entregadores_semana = temp_pedido_por_semana.merge(temp_entregadores_por_semana, on="week_of_year", how="inner")
    pedidos_entregadores_semana["order_by_delivery"] = pedidos_entregadores_semana["Qtde_Pedidos"]/pedidos_entregadores_semana["Entregadores_Unicos"]

    fig = px.line(data_frame=pedidos_entregadores_semana, x="week_of_year", y="order_by_delivery",
                 labels={'week_of_year':'Número da Semana do Ano', "order_by_delivery":"Pedidos por Entregador"})

    return fig


def map_restaurantes(df):
    """ 
    A partir dos dados de latitude e longitude em um data frame, mostra a localização dos locais no mapa.

    Input: Dataframe
    Output: Mapa com a localiozação marcada (map folium)
    """
    loc_central_df = df.groupby(["City", "Road_traffic_density"]).agg({"Delivery_location_latitude":"median", "Delivery_location_longitude":"median"}).reset_index()
    map = folium.Map()
    for index, location_info in loc_central_df.iterrows():
        folium.Marker(location=[location_info["Delivery_location_latitude"],
                                location_info["Delivery_location_longitude"]], 
                    popup=location_info[["City", "Road_traffic_density"]]).add_to(map)
    return map

#====================================================================================================================
#Funções visão entregadores
#====================================================================================================================

def avaliacao_media_entregadores(df):
    """ 
    Cálcula a avaliação médio para cada entregador registrado na base

    Input: Dataframe
    Output: Dataframe
    """
    return  (df.groupby("Delivery_person_ID")
                .agg({"Delivery_person_Ratings":"mean"})
                .reset_index()
                .rename(columns={"Delivery_person_Ratings":"Media_avaliação"}))


def avaliacao_media_transito(df):
    """ 
    Calcula a avaliação média e o desvio padrão por trânsito

    Input: Dataframe
    Output: Dataframe
    """
    delivery_mean_std = df.groupby("Road_traffic_density").agg({"Delivery_person_Ratings":["mean", "std"]})
    delivery_mean_std.columns = ["Delivery_mean", "Delivery_std"]
    delivery_mean_std.reset_index(inplace=True)
    return delivery_mean_std


def avaliacao_media_clima(df):
    """ 
    Calcula a avaliação média e o desvio padrão por trânsito

    Input: Dataframe
    Output: Dataframe    
    """
    weather_mean_std = df.groupby("Weatherconditions").agg({"Delivery_person_Ratings":["mean", "std"]})
    weather_mean_std.columns = ["Delivery_mean", "Delivery_std"]
    weather_mean_std.reset_index(inplace=True)
    return weather_mean_std


def entregadores_rapidos(df):
    """ 
    Calcula e seleciona os dez entregadores com menores tempos de entrega

    Input: Dataframe
    Output: Dataframe    
    """
    mais_rapido_por_cidade = (
        (
            df
            .groupby(["City", "Delivery_person_ID"])
            .agg({"Time_taken(min)":"mean"})
            .reset_index()
        )
        .groupby("City")
        .apply(lambda x: x.nsmallest(n=10, columns="Time_taken(min)"))
        .reset_index(drop=True)
    )
    return mais_rapido_por_cidade


def entregadores_lentos(df):
    """ 
    Calcula e seleciona os dez entregadores com maiores tempos de entrega

    Input: Dataframe
    Output: Dataframe    
    """
    mais_lentos_por_cidade = (
        (
            df
            .groupby(["City", "Delivery_person_ID"])
            .agg({"Time_taken(min)":"mean"})
            .reset_index()
        )
        .groupby("City")
        .apply(lambda x: x.nlargest(n=10, columns="Time_taken(min)"))
        .reset_index(drop=True)
    )
    return mais_lentos_por_cidade
#====================================================================================================================
#Funções visão restaurantes
#====================================================================================================================
def distancia_media(df):
    """ 
    Calcula a distancia média entre os restaurantes e os locais de entrega

    Input: Dataframe
    Output: integer
    """
    df["distancia_restaurante"] = (
        df
        .apply(lambda x: haversine((x["Restaurant_latitude"], x["Restaurant_longitude"]), 
                                (x["Delivery_location_latitude"], x["Delivery_location_longitude"]), 
                                    unit=Unit.KILOMETERS),
                                    axis=1)
    )

    return round(df["distancia_restaurante"].mean(), 2)


def tempo_medio_desvio(df):
    """ 
    Calcula o tempo médio e o devio padrão de entrega por cidade e retorna um gráfico de barraws com as informações

    Input: Dataframe
    Output: Gráfico de barras (plotly graph_objects)
    """
    df_aux = df.groupby("City").agg({"Time_taken(min)":["mean", "std"]})
    df_aux.columns = ["avg_time", "std_time"]

    df_aux.reset_index(inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Control",
                        x=df_aux["City"],
                        y=df_aux["avg_time"],
                        error_y=dict(type="data", array=df_aux["std_time"])))

    fig.update_layout(barmode="group")
    return fig


def tempo_medio_std_cidade_trafego(df):
    """ 
    Calcula o tempo médio e o desvio padrão por cidade e por tipo de tráfego

    Input: Dataframe
    Output: Dataframe
    """
    tempo_media_cidade_tipo_trafego = df.groupby(["City", "Road_traffic_density"]).agg({"Time_taken(min)":["mean", "std"]})
    tempo_media_cidade_tipo_trafego.columns = ["tempo_medio", "desvio_padrao_tempo"]
    tempo_media_cidade_tipo_trafego.reset_index(inplace=True)
    return tempo_media_cidade_tipo_trafego


def media_distanci_cidade(df):
    """ 
    Calcula a distancia média entre os restaurantes e os locais de entrega por cidade retornando um gráfico de pizza

    Input: Dataframe
    Output: Gráfico de pizza (plotly graph_objects)
    """
    df["distance"] = df.apply(lambda x:
                        haversine((x["Restaurant_latitude"], x["Restaurant_longitude"]),
                                (x["Delivery_location_latitude"], x["Delivery_location_longitude"])), 
                        axis=1)

    avg_distance = df.groupby("City").agg({"distance":"mean"}).reset_index()

    fig = go.Figure(data=[go.Pie(labels=avg_distance["City"], 
                                    values=avg_distance["distance"], pull=[0, 0.1, 0])])
    return fig


def media_desvio_tempo_trafego(df):
    """ 
    Calcula tempo médio por de entrega por cidade e por tráfego returnando um gráfico do tipo sunburst

    Input: Dataframe
    Output: Gráfico sunburst (plotly express)
    """
    df_aux = df.groupby(["City", "Road_traffic_density"]).agg({"Time_taken(min)":["mean", "std"]})
    df_aux.columns = ["avg_time", "std_time"]
    df_aux.reset_index(inplace=True)
    fig = px.sunburst(df_aux, path=["City", "Road_traffic_density"], values="avg_time",
                    color="std_time", color_continuous_scale="RdBu",
                    color_continuous_midpoint=np.average(df_aux["std_time"]))
    return fig
