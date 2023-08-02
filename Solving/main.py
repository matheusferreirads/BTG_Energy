import pandas as pd
import re
import time
from functools import wraps
import os
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata
import matplotlib.pyplot as plt


folder_path = r'forecast_files'
contour_path = r'Solving\PSATCMG_CAMARGOS.bln'

def read_contour_file(file_path: str) -> pd.DataFrame:
    line_split_comp = re.compile(r'\s*,')

    with open(file_path, 'r') as f:
        raw_file = f.readlines()

    l_raw_lines = [line_split_comp.split(raw_file_line.strip()) for raw_file_line in raw_file]
    l_raw_lines = list(filter(lambda item: bool(item[0]), l_raw_lines))
    float_raw_lines = [list(map(float, raw_line))[:2] for raw_line in l_raw_lines]
    header_line = float_raw_lines.pop(0)
    assert len(float_raw_lines) == int(header_line[0])
    return pd.DataFrame(float_raw_lines, columns=['lat', 'long'])


def read_data_file(file_path: str) -> pd.DataFrame:
    with open(file_path, 'r') as f:
        raw_file = f.readlines()

    list_dados = [line.split() for line in raw_file]
    float_raw_lines = [list(map(float, raw_line)) for raw_line in list_dados]
    return pd.DataFrame(float_raw_lines, columns=['lat', 'long', 'data_value'])

def main() -> None:
    dataframes = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        df_temp = read_data_file(file_path)
        dataframes.append(df_temp)

    combined_df = pd.concat(dataframes, ignore_index=True)



    df_acumulado_sum = combined_df.groupby(['lat', 'long'])['data_value'].sum()
    df_acumulado_sum = df_acumulado_sum.reset_index()
    contour_df: pd.DataFrame = read_contour_file(contour_path)
    filtered_df = df_acumulado_sum.query('-43.75 >= lat >= -45 & -21 >= long >= -22.6')


    latitudes = filtered_df['lat'].values
    longitudes = filtered_df['long'].values
    data_values = filtered_df['data_value'].values

    grid_x, grid_y = np.mgrid[min(latitudes):max(latitudes):100j, min(longitudes):max(longitudes):100j]
    grid_z = griddata((latitudes, longitudes), data_values, (grid_x, grid_y), method='cubic')
    plt.contourf(grid_x, grid_y, grid_z, cmap='viridis')

    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.colorbar(label='Vol. Precipitação Acumulada')
    plt.plot(contour_df['lat'], contour_df['long'], linewidth=2, color='black')

    fill_spec = filtered_df.query('-43.9 >= lat >= -44.8 & -21.2 >= long >= -22.5 & data_value != 126.39999999999999')
    for index, row in fill_spec.iterrows():
        plt.text(row['lat'], row['long'], str(row['data_value']), fontsize=10, color='white', ha='center', va='center', weight='bold')


    total_precipitation = np.sum(fill_spec['data_value'])
    plt.figtext(0.45, 0.2, f'Vol. Total: {total_precipitation:.2f}', fontsize=10, color='white', weight='bold')
    plt.savefig('Contour_chart_Matplot.png')



#------------------------------###-------------------------------------------
#Graph2
    

    latitudes = filtered_df['lat'].values
    longitudes = filtered_df['long'].values
    data_values = filtered_df['data_value'].values

    grid_x, grid_y = np.mgrid[min(longitudes):max(longitudes):100j, min(latitudes):max(latitudes):100j]
    grid_z = griddata((longitudes, latitudes), data_values, (grid_x, grid_y), method='cubic')

    latitudes = filtered_df['lat'].values
    longitudes = filtered_df['long'].values
    data_values = filtered_df['data_value'].values

    grid_x, grid_y = np.mgrid[min(longitudes):max(longitudes):100j, min(latitudes):max(latitudes):100j]
    grid_z = griddata((longitudes, latitudes), data_values, (grid_x, grid_y), method='cubic')



    heatmap = go.Figure(data=go.Heatmap(
        x=grid_y[0, :],
        y=grid_x[:, 0],
        z=grid_z.T, 
        colorscale='Viridis',
        transpose=True 
    ))
    heatmap.update_layout(
        title=dict(text='<b>Vol Precipitação Acumulada | Camargos - Bacia do Grande<b>',  font=dict(size=17,)),
        xaxis_title=dict(text='<b>Latitude<b>',  font=dict(size=16,)),
        yaxis_title=dict(text='<b>Longitude<b>',  font=dict(size=16,)),
        width=600, 
        height=700   
    )
    contorno_trace = go.Scatter(
        x=contour_df['lat'],
        y=contour_df['long'],
        mode='lines',
        line=dict(color='black', width=2.5)
    )
    for index, row in fill_spec.iterrows():
        heatmap.add_annotation(
            x=row['lat'],
            y=row['long'],
            text=str(row['data_value']),
            showarrow=False,
            arrowhead=2,
            ax=-40,
            ay=-40,
            font=dict(color='white', size=12.5)
        )
    heatmap.add_annotation(
        x=-44,
        y=-22.4,
        text=f'Vol. Total: {total_precipitation:.2f}',
        font=dict(color='white', size=13),
        showarrow=False
    )

    heatmap.add_trace(contorno_trace)
    heatmap.write_html('Contour_Chart_Softened_Plotly.html')
    


if __name__ == '__main__':
    main()