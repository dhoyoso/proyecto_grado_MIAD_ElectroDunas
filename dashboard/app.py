import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime as dt
import random
import colorsys

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "ElectroDunas"

# Ruta con los datos pre procesados utilizados en los diagramas descriptivos históricos.
PREPROCESSED_DATA_PATH = "data/preprocessed.csv"
# Ruta con los datos de los consumos y pronósticos de los clientes.
CONSUMPTION_AND_PREDICION_DATA_PATH = "data/"

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

def calculate_mape(actual, predicted):
    return (abs((actual - predicted) / actual)).mean() * 100

# Load data from csv
def load_data(data_path):
    result_df = pd.read_csv(data_path)

    result_df['Fecha'] = pd.to_datetime(result_df['Fecha'])
    result_df.set_index('Fecha', inplace=True)

    return result_df

# Cargar datos
data = load_data(PREPROCESSED_DATA_PATH)

# Graficar serie
def plot_series(data, initial_date, traces = False):
    data_plot = data.loc[initial_date:]

    figures = [go.Scatter(
            name='Demanda energética',
            x=data_plot.index,
            y=data_plot['Active_energy'],
            mode='lines',
            line=dict(color="#188463"),
        )]
    
    if traces:
        figures.append(go.Scatter(
           name='Proyección',
           x=data_plot.index,
           y=data_plot['Predictions'],
           mode='lines',
           line=dict(color="#bbffeb",),
        ))
        figures.append(go.Scatter(
           name='Upper Bound',
           x=data_plot.index,
           y=data_plot['Upper_Bound'],
           mode='lines',
           marker=dict(color="#444"),
           line=dict(width=0),
           showlegend=False
        ))
        figures.append(go.Scatter(
           name='Lower Bound',
           x=data_plot.index,
           y=data_plot['Lower_Bound'],
           marker=dict(color="#444"),
           line=dict(width=0),
           mode='lines',
           fillcolor="rgba(242, 255, 251, 0.3)",
           fill='tonexty',
           showlegend=False
        ))

    fig = go.Figure(figures)

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
                            {'label': cliente, 'value': cliente} for cliente in sorted(data['Cliente'].unique()) if pd.notna(cliente)
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
                                date=min(data.index.date),#-dt.timedelta(days=7)
                                display_format='DD/MM/YYYY'
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
                                date=max(data.index.date), #-dt.timedelta(days=7)
                                display_format='DD/MM/YYYY'
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
            # html.Hr(),
            html.Br(),
            html.Div([html.B(id = 'consumo-total-title', children = "Total consumo de energía activa:", style=dict(width='75%')), html.P(" ",style=dict(width='3%', textAlign='center')), html.P(id = 'consumo-total-value', children = "100 kWh", style=dict(width='25%'))], style = dict(display='flex', margin='1%')),
            html.Div([html.B(id = 'franja-consumo-title', children = "Franja horaria con mayor consumo del cliente:", style=dict(width='75%')), html.P(" ",style=dict(width='3%', textAlign='center')), html.P(id = 'franja-consumo-value', children = "8 am - 5 pm", style=dict(width='25%'))], style = dict(display='flex', margin='1%')),
            html.Div([html.B(id = 'datos-anomalos-title', children = "Total datos anomalos del cliente:", style=dict(width='75%')), html.P(" ",style=dict(width='3%', textAlign='center')), html.P(id = 'datos-anomalos-value', children = "200", style=dict(width='25%'))], style = dict(display='flex', margin='1%')),
            html.Div([html.B(id = 'mape-modelo-title', children = "Error (MAPE) del pronóstico del consumo del cliente:", style=dict(width='75%')), html.P(" ",style=dict(width='3%', textAlign='center')), html.P(id = 'mape-modelo-value', children = "9%", style=dict(width='25%'))], style = dict(display='flex', margin='1%')),
            html.Br(),
            html.Br(),
            html.Div([html.B(id = 'alert-title', className='alert', children = "", style=dict(width='100%', textAlign='center'))], style = dict(display='flex', margin='1%'))
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
            'xaxis': {'title': 'Cliente', 'showgrid': True, 'gridcolor': '#FFFFFF'},
            'yaxis': {'title': f'Consumo total de energía activa en las <br> fechas y horas seleccionadas', 'showgrid': True, 'gridcolor': '#FFFFFF'}, # del {initial_date} <br> a las {initial_hour} horas al <br> {end_date} a las {end_hour} horas'},
            'plot_bgcolor': '#252e3f',  # Dark blue background color
            'paper_bgcolor': '#252e3f',  # Consistent with plot background
            'font': {'color': '#FFFFFF'}  # White font for better readability
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
                ]),
            bgcolor='#1f2630',  # Custom background color for buttons
            font=dict(color='#FFFFFF'),  # Button text color
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        plot_bgcolor = '#252e3f',  # Dark blue background color
        paper_bgcolor = '#252e3f',  # Consistent with plot background
        font = {'color': '#FFFFFF'}  # White font for better readability
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
    if max_period_start >= 20:
        max_period_start = 20
    franja_horaria = f"{max_period_start} - {max_period_start+4}"

    return fig_bar, sector, fig_area, series_plot_title, consumo_total, title_franja_horaria, franja_horaria


@app.callback(
    [Output("plot_series", "figure"), Output("mape-modelo-value", "children"), Output("datos-anomalos-value", "children"), Output("alert-title", "children")],
    [Input("datepicker-inicial", "date"),
    Input("dropdown-hora-inicial-hora", "value"),
    Input('client-dropdown-control', 'value'), 
    Input('datepicker-final', 'date'), 
    Input('dropdown-hora-final-hora', 'value')]
)
def update_output_div(date, hour, client, end_date, end_hour):

    if ((date is not None) & (hour is not None)):
        hour = str(hour)
        minute = str(0)

        initial_date = date + " " + hour + ":" + minute
        initial_date = pd.to_datetime(initial_date, format="%Y-%m-%d %H:%M")

        if client != 'todos':
            client_data = pd.read_excel(CONSUMPTION_AND_PREDICION_DATA_PATH+client+'.xlsx')

            client_data['Fecha'] = pd.to_datetime(client_data['Fecha'])
            client_data.set_index('Fecha', inplace=True)
            traces = True
            mape = round(calculate_mape(client_data['Active_energy'], client_data['Predictions']), 2)

            # Filter for anomalies
            anomalies_below = client_data[client_data['Active_energy'] < client_data['Lower_Bound']]
            anomalies_above = client_data[client_data['Active_energy'] > client_data['Upper_Bound']]

            # Count anomalies
            count_anomalies_below = anomalies_below.shape[0]
            count_anomalies_above = anomalies_above.shape[0]

            # Total anomalies
            total_anomalies = count_anomalies_below + count_anomalies_above

            valid_predictions = client_data['Predictions'].notna().sum()

            if total_anomalies/valid_predictions>0.2:
                alert_title = 'ALERTA DE CONSUMO ANOMALO'
            else:
                alert_title = ''
            

        else:
            client_data = data[data["Cliente"] == client]
            total_anomalies = 'Selecciona un Cliente'
            mape = 'Selecciona un Cliente'
            traces = False
            alert_title = ''

        # Graficar
        plot = plot_series(client_data, initial_date, traces)
        return plot, mape, total_anomalies, alert_title


# Run the server
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
