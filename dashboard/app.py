import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime as dt
import requests
from io import BytesIO
from io import StringIO
import random
import colorsys

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "ElectroDunas"

# URL del repositorio en GitHub
REPO_URL = 'https://api.github.com/repos/Pacheco-Carvajal/GPA-Data-ElectroDunas/contents/'
SECTOR_DATA_FILE_URL = 'https://github.com/Pacheco-Carvajal/GPA-Data-ElectroDunas/raw/main/sector_economico_clientes.xlsx'


server = app.server
app.config.suppress_callback_exceptions = True

def generate_random_color(n):
    color_list = []
    for i in range(n):
        hue = random.uniform(0.33, 0.66)  # Green to blue
        saturation = random.uniform(0.5, 1)  # High saturation
        lightness = random.uniform(0.1, 0.3)  # Very low lightness for darker shades
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        color_list.append(color)
    return color_list

# Load data from csv
def load_data(repo_url, sector_data_url):
    result_df = pd.read_csv("preprocessed.csv")

    # Haz una solicitud GET a la API de GitHub para obtener la lista de archivos en el directorio
    # response = requests.get(repo_url)
    # file_data = response.json()

    # # Filtra los archivos que contienen "datos cliente" en su nombre
    # desired_files = [(file['download_url'], file['name']) for file in file_data if 'DATOSCLIENTE' in file['name']]

    # # Crea un DataFrame combinando todos los archivos encontrados
    # dfs = []
    # for file_url, file_name in desired_files:
    #     response = requests.get(file_url)
    #     content = response.content.decode('utf-8')
    #     df = pd.read_csv(StringIO(content))

    #     # Agrega una columna "fuente" con el nombre del archivo
    #     df['fuente'] = file_name

    #     dfs.append(df)

    # # Concatena los DataFrames en uno solo
    # client_sector_df = pd.concat(dfs, ignore_index=True)

    # #print(client_sector_df)

    # # Cargar el archivo Excel en un DataFrame
    # sectores = pd.read_excel(sector_data_url)

    # #print(sectores)

    # # Extraer los números de la columna 'fuente'
    # client_sector_df['fuente'] = client_sector_df['fuente'].str.extract('(\d+)')

    # # Concatenar 'Cliente' con los números extraídos
    # client_sector_df['fuente'] = 'Cliente ' + client_sector_df['fuente']

    # #print(client_sector_df)

    # client_sector_df = client_sector_df.rename(columns={'fuente': 'Cliente'})
    # sectores = sectores.rename(columns={'Cliente:': 'Cliente'})
    # sectores['Cliente'] = sectores['Cliente'].str.strip()

    # result_df = pd.merge(client_sector_df, sectores[['Cliente', 'Sector Económico:']], on='Cliente', how='left')

    # result_df = result_df.rename(columns={'Sector Económico:': 'Sector'})

    result_df['Fecha'] = pd.to_datetime(result_df['Fecha'])
    result_df.set_index('Fecha', inplace=True)

    # print(result_df)
    # print(result_df['Sector'].unique())

    # result_df.to_csv("./preprocessed.csv")
    #print(result_df)
    return result_df

# Cargar datos
data = load_data(REPO_URL, SECTOR_DATA_FILE_URL)

# Graficar serie
def plot_series(data, initial_date, proy):

    data_plot = data.loc[initial_date:]
    data_plot = data_plot[:-(120-proy)]
    fig = go.Figure([
        go.Scatter(
            name='Demanda energética',
            x=data_plot.index,
            y=data_plot['Active_energy'],
            mode='lines',
            line=dict(color="#188463"),
        ),
        #go.Scatter(
        #    name='Proyección',
        #    x=data_plot.index,
        #    y=data_plot['forecast'],
        #    mode='lines',
        #    line=dict(color="#bbffeb",),
        #),
        #go.Scatter(
        #    name='Upper Bound',
        #    x=data_plot.index,
        #    y=data_plot['Upper bound'],
        #    mode='lines',
        #    marker=dict(color="#444"),
        #    line=dict(width=0),
        #    showlegend=False
        #),
        #go.Scatter(
        #    name='Lower Bound',
        #    x=data_plot.index,
        #    y=data_plot['Lower bound'],
        #    marker=dict(color="#444"),
        #    line=dict(width=0),
        #    mode='lines',
        #    fillcolor="rgba(242, 255, 251, 0.3)",
        #    fill='tonexty',
        #    showlegend=False
        #)
    ])

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis_title='Energía Activa [kWh]',
        #title='Continuous, variable value error bars',
        hovermode="x"
    )
    #fig = px.line(data2, x='local_timestamp', y="Demanda total [MW]", markers=True, labels={"local_timestamp": "Fecha"})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#2cfec1")
    fig.update_xaxes(showgrid=True, gridwidth=0.25, gridcolor='#7C7C7C')
    fig.update_yaxes(showgrid=True, gridwidth=0.25, gridcolor='#7C7C7C')
    #fig.update_traces(line_color='#2cfec1')

    return fig



def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            #html.H5("Proyecto 1"),
            html.H3("ElectroDunas"),
            html.Div(
                id="intro",
                children="Esta herramienta proporciona datos sobre el consumo de energía en Perú por parte de clientes no regulados de ElectroDunas. El tablero facilita la visualización de datos históricos de consumo y también permite generar un pronóstico de la demanda, con alertas visuales en caso de desviaciones significativas."
            ),
        ],
    )


def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Div(
                children = [
                    html.Label('Selecciona un cliente:'),
                    dcc.Dropdown(
                        id='client-dropdown-control',
                        options=[{'label': "todos", 'value': "todos"}] + [
                            {'label': cliente, 'value': cliente} for cliente in data['Cliente'].unique() if pd.notna(cliente)
                        ],
                        value="todos",  # Valor predeterminado: "todos"
                        style={'width': '100%'}
                    ),
                ], className="four columns", style={'width': '95%', 'margin':'1%'}
            ),
            html.Div(
                children = [
                    html.Label('Selecciona un sector:'),
                    dcc.Dropdown(
                        id='sector-dropdown-control',
                        options=[{'label': "todos", 'value': "todos"}] + [
                            {'label': sector, 'value': sector} for sector in data['Sector'].unique() if pd.notna(sector)
                        ],
                        value="todos",  # Valor predeterminado: "todos"
                        style={'width': '100%'}
                    ),
                ], className="four columns", style={'width': '95%', 'margin':'1%', 'margin-bottom':'3%'}
            ),

            html.Br(),
            html.Br(),

            # Fecha inicial
            html.Label("Seleccionar fecha y hora inicial:", style=dict(margin='1%')),

            html.Div(
                id="componentes-fecha-inicial",
                children=[
                    html.Div(
                        id="componente-fecha",
                        children=[
                            dcc.DatePickerSingle(
                                id='datepicker-inicial',
                                min_date_allowed=min(data.index.date),
                                max_date_allowed=max(data.index.date),
                                #initial_visible_month=max(data.index.date),
                                date=min(data.index.date)#-dt.timedelta(days=7)
                            )
                        ],
                        style=dict(width='30%')
                    ),
                    
                    html.P(" ",style=dict(width='5%', textAlign='center')),
                    
                    html.Div(
                        id="componente-hora",
                        children=[
                            dcc.Dropdown(
                                id="dropdown-hora-inicial-hora",
                                options=[{"label": i, "value": i} for i in np.arange(0,25)],
                                value=pd.to_datetime(max(data.index)-dt.timedelta(days=7)).hour,
                                # style=dict(width='50%', display="inline-block")
                            )
                        ],
                        style=dict(width='20%')
                    ),
                ],
                style=dict(display='flex', margin='1%')
            ),

            html.Br(),
            # Fecha final
            html.Label("Seleccionar fecha y hora final:", style=dict(margin='1%')),

            html.Div(
                id="componentes-fecha-final",
                children=[
                    html.Div(
                        id="componente-fecha-final",
                        children=[
                            dcc.DatePickerSingle(
                                id='datepicker-final',
                                min_date_allowed=min(data.index.date),
                                max_date_allowed=max(data.index.date),
                                #initial_visible_month=max(data.index.date),
                                date=max(data.index.date) #-dt.timedelta(days=7)
                            )
                        ],
                        style=dict(width='30%')
                    ),
                    
                    html.P(" ",style=dict(width='5%', textAlign='center')),
                    
                    html.Div(
                        id="componente-hora-final",
                        children=[
                            dcc.Dropdown(
                                id="dropdown-hora-final-hora",
                                options=[{"label": i, "value": i} for i in np.arange(0,25)],
                                value=pd.to_datetime(max(data.index)-dt.timedelta(days=7)).hour,
                                # style=dict(width='50%', display="inline-block")
                            )
                        ],
                        style=dict(width='20%')
                    ),
                ],
                style=dict(display='flex', margin='1%')
            ),

            html.Br(),

            # Slider proyección
            html.Div(
                id="campo-slider",
                children=[
                    html.P("Ingrese horas a proyectar:"),
                    dcc.Slider(
                        id="slider-proyeccion",
                        min=0,
                        max=119,
                        step=1,
                        value=0,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                    )
                ]
            ),
            html.Br(),
            # html.Hr(),
            html.Br(),
            html.Div([html.B(id = 'consumo-total-title', children = "Total consumo de energía activa:", style=dict(width='75%')), html.P(" ",style=dict(width='3%', textAlign='center')), html.P(id = 'consumo-total-value', children = "100 kWh", style=dict(width='25%'))], style = dict(display='flex', margin='1%')),
            html.Div([html.B(id = 'datos-anomalos-title', children = "Total datos anomalos del cliente:", style=dict(width='75%')), html.P(" ",style=dict(width='3%', textAlign='center')), html.P(id = 'datos-anomalos-value', children = "200", style=dict(width='25%'))], style = dict(display='flex', margin='1%')),
            html.Div([html.B(id = 'franja-consumo-title', children = "Franja horaria con mayor consumo del cliente:", style=dict(width='75%')), html.P(" ",style=dict(width='3%', textAlign='center')), html.P(id = 'franja-consumo-value', children = "8 am - 5 pm", style=dict(width='25%'))], style = dict(display='flex', margin='1%')),
            html.Div([html.B(id = 'mape-modelo-title', children = "Error (MAPE) del pronóstico del consumo del cliente:", style=dict(width='75%')), html.P(" ",style=dict(width='3%', textAlign='center')), html.P(id = 'mape-modelo-value', children = "9%", style=dict(width='25%'))], style = dict(display='flex', margin='1%'))
        ]
    )


app.layout = html.Div(
    id="app-container",
    #style={'zoom': '90%'},
    children=[
        
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(), generate_control_card()]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                # Grafica de la serie de tiempo
                html.Div(
                    id="model_graph",
                    children=[
                        html.B(id = 'series-plot-title', children = "Demanda energética, pronóstico y anomalías [kWh]"),
                        html.Hr(),
                        dcc.Graph(
                            id="plot_series",  
                            #style={'height': '300px'}
                        )
                    ],
                ),
                html.Div(
                    id="descriptive_graphs",
                    children = [
                        html.Div([
                            dcc.Graph(
                                id='bar-chart',
                                #style={'height': '200px'}
                            )
                        ], className="six columns"),
                        html.Div([
                            dcc.Graph(
                                id='area-chart',
                                #style={'height': '200px'}
                            )
                        ], className="six columns"),
                    ], className="row"
                )
            ],
        ),
    ],
)


# Crea una función de callback para actualizar los gráficos y contadores en función de las selecciones en los menús desplegables
@app.callback(
    [Output('bar-chart', 'figure'), Output('sector-dropdown-control', 'value'), Output('area-chart', 'figure'), Output('series-plot-title', 'children'), Output('consumo-total-value', 'children'), Output('franja-consumo-title', 'children') ,Output('franja-consumo-value', 'children')],
    [Input('client-dropdown-control', 'value'), Input('sector-dropdown-control', 'value'), Input('datepicker-inicial', 'date'), Input('datepicker-final', 'date'), Input('dropdown-hora-inicial-hora', 'value'), Input('dropdown-hora-final-hora', 'value')]
)
def actualizar_graficos_y_contadores(client, sector, initial_date, end_date, initial_hour, end_hour):
    # print(initial_date)
    # print(initial_hour)
    # print(type(initial_date))
    # print(type(initial_hour))
    # print(data)

    start_datetime = pd.Timestamp(f"{initial_date} {initial_hour:02}:00:00")
    end_datetime = pd.Timestamp(f"{end_date} {end_hour:02}:00:00")

    if 'Fecha' not in data.columns:
        data_w_fecha_col = data.reset_index()

    if client == 'todos' or client == None:
        series_plot_title = "Por favor selecciona un cliente para ver la Demanda energética, pronóstico y anomalías [kWh]"

        if sector == 'todos' or sector == None:
            df_filtrado = data_w_fecha_col
            title_bar = 'Total consumo energía activa por clientes de todos los sectores'

            df_filtrado_area = df_filtrado
            title_area = 'Total voltajes FA y FC por clientes de todos los sectores'
        else:
            df_filtrado = data_w_fecha_col[data_w_fecha_col['Sector'] == sector]
            title_bar = f'Total consumo energía activa por clientes del sector <br> {sector}'

            df_filtrado_area = df_filtrado
            title_area = f'Total voltajes FA y FC por clientes del sector <br> {sector}'

    else:
        series_plot_title = f"Demanda energética, pronóstico y anomalías del {client}"

        sector = data_w_fecha_col[data_w_fecha_col['Cliente'] == client].iloc[0]['Sector']
        df_filtrado = data_w_fecha_col[data_w_fecha_col['Sector'] == sector]
        title_bar = f'Total consumo energía activa por clientes del sector <br> {sector}'

        df_filtrado_area = df_filtrado[df_filtrado['Cliente'] == client]
        title_area = f'Total voltajes FA y FC del {client} del sector <br> {sector}'


    df_filtrado = df_filtrado[(df_filtrado['Fecha'] >= start_datetime) & (df_filtrado['Fecha'] <= end_datetime)]
    df_filtrado_area = df_filtrado_area[(df_filtrado_area['Fecha'] >= start_datetime) & (df_filtrado_area['Fecha'] <= end_datetime)]

    # print(df_filtrado)

    data_bar = df_filtrado.groupby('Cliente')['Active_energy'].sum().reset_index()

    data_bar = data_bar.sort_values('Active_energy', ascending=False)

    custom_colors = generate_random_color(31)

    # Crea el gráfico de barras
    fig_bar = {
        'data': [
            {'x': data_bar['Cliente'], 'y': data_bar['Active_energy'], 'type': 'bar', 'name': 'Active Energy', 'marker': {'color': custom_colors}},
        ],
        'layout': {
            'title': title_bar,
            'xaxis': {'title': 'Cliente'},
            'yaxis': {'title': f'Consumo total de energía activa en las <br> fechas y horas seleccionadas'} # del {initial_date} <br> a las {initial_hour} horas al <br> {end_date} a las {end_hour} horas'},
        }
    }

    data_area_voltaje_fa = df_filtrado_area.groupby('Fecha')['Voltaje_FA'].sum().reset_index()
    data_area_voltaje_fc = df_filtrado_area.groupby('Fecha')['Voltaje_FC'].sum().reset_index()

    # Generate the area plot
    fig_area = go.Figure(data=[go.Scatter(
        x=data_area_voltaje_fa['Fecha'],
        y=data_area_voltaje_fa['Voltaje_FA'],
        fill='tozeroy',  # Fill to zero on the y-axis
        mode='lines',  # Lines with markers at data points 
        line=dict(color='blue'),  # Line color
        name="Voltaje FA"
    ),
    go.Scatter(
            x=data_area_voltaje_fc['Fecha'],
            y=data_area_voltaje_fc['Voltaje_FC'],
            fill='tozeroy',  # Fill to zero on the y-axis
            mode='lines',  # Lines with markers at data points
            line=dict(color='green'),  # Line color
            name="Voltaje FC"
        )
    ])

    # Update layout if necessary
    fig_area.update_layout(
        title={
            'text': title_area,
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Fecha',
        yaxis_title='Voltaje FA / FC',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(label = "Todo", step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    consumo_total = str(round(df_filtrado_area['Active_energy'].sum(),2)) + " [kWh]"

    # Extraer la hora del día
    df_filtrado_area['Hora'] = df_filtrado_area['Fecha'].dt.hour

    # Agrupar por hora y sumar la energía activa
    energy_per_hour = df_filtrado_area.groupby('Hora')['Active_energy'].sum()

    # Calcula la suma rodante de 4 horas
    rolling_sum = energy_per_hour.rolling(window=4).sum()

    # Encontrar el inicio del periodo de 4 horas con el mayor consumo
    max_period_start = rolling_sum.idxmax()
    max_value = rolling_sum.max()

    title_franja_horaria = "Franja de 4 horas con mayor consumo de los clientes:" if "todos" == client else f"Franja horaria con mayor consumo del {client.lower()}:"
    franja_horaria = f"{max_period_start} - {max_period_start+4}"

    return fig_bar, sector, fig_area, series_plot_title, consumo_total, title_franja_horaria, franja_horaria


@app.callback(
    Output("plot_series", "figure"),
    [Input("datepicker-inicial", "date"),
    Input("dropdown-hora-inicial-hora", "value"),
    Input("slider-proyeccion", "value"), 
    Input('client-dropdown-control', 'value'), 
    Input('datepicker-final', 'date'), 
    Input('dropdown-hora-final-hora', 'value')]
)
def update_output_div(date, hour, proy, client, end_date, end_hour):

    if ((date is not None) & (hour is not None) & (proy is not None)):
        hour = str(hour)
        minute = str(0)

        initial_date = date + " " + hour + ":" + minute
        initial_date = pd.to_datetime(initial_date, format="%Y-%m-%d %H:%M")

        client_data = data[data["Cliente"] == client]

        # Graficar
        plot = plot_series(client_data, initial_date, int(proy))
        return plot


# Run the server
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
