import requests
import pandas as pd
from io import StringIO


# URL del repositorio en GitHub
repo_url = 'https://api.github.com/repos/Pacheco-Carvajal/GPA-Data-ElectroDunas/contents/'
sector_data_url = 'https://github.com/Pacheco-Carvajal/GPA-Data-ElectroDunas/raw/main/sector_economico_clientes.xlsx'

# Haz una solicitud GET a la API de GitHub para obtener la lista de archivos en el directorio
response = requests.get(repo_url)
file_data = response.json()

# Filtra los archivos que contienen "datos cliente" en su nombre
desired_files = [(file['download_url'], file['name']) for file in file_data if 'DATOSCLIENTE' in file['name']]

# Crea un DataFrame combinando todos los archivos encontrados
dfs = []
for file_url, file_name in desired_files:
    response = requests.get(file_url)
    content = response.content.decode('utf-8')
    df = pd.read_csv(StringIO(content))

    # Agrega una columna "fuente" con el nombre del archivo
    df['fuente'] = file_name

    dfs.append(df)

# Concatena los DataFrames en uno solo
client_sector_df = pd.concat(dfs, ignore_index=True)

#print(client_sector_df)

# Cargar el archivo Excel en un DataFrame
sectores = pd.read_excel(sector_data_url)

#print(sectores)

# Extraer los números de la columna 'fuente'
client_sector_df['fuente'] = client_sector_df['fuente'].str.extract('(\d+)')

# Concatenar 'Cliente' con los números extraídos
client_sector_df['fuente'] = 'Cliente ' + client_sector_df['fuente']

#print(client_sector_df)

client_sector_df = client_sector_df.rename(columns={'fuente': 'Cliente'})
sectores = sectores.rename(columns={'Cliente:': 'Cliente'})
sectores['Cliente'] = sectores['Cliente'].str.strip()

result_df = pd.merge(client_sector_df, sectores[['Cliente', 'Sector Económico:']], on='Cliente', how='left')

result_df = result_df.rename(columns={'Sector Económico:': 'Sector'})

result_df['Fecha'] = pd.to_datetime(result_df['Fecha'])
result_df.set_index('Fecha', inplace=True)

# print(result_df)
# print(result_df['Sector'].unique())

result_df.to_csv("./dashboard/data/preprocessed.csv")