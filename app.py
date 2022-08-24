from dash import Dash, html, dcc
import plotly.express as px
import sqlite3
import pandas as pd
from services.monitoring_data_service import create_num_per_rank_data, graph_bg_descriptions_dates, pie_bg_descriptions, graph_fact_top_games_date_affected, graph_num_games_created_per_date, colors

app = Dash(__name__)
con = sqlite3.connect('data/board_games.db')

fig_pie = create_num_per_rank_data(con) 

created_games_by_day = graph_num_games_created_per_date(con)

fact_top_games_updates = graph_fact_top_games_date_affected(con)

desc_pie = pie_bg_descriptions(con)
desc_bar = graph_bg_descriptions_dates(con)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(    
        children='Board Game Data Monitoring',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    dcc.Graph(
        id='example-graph_2',
        figure=created_games_by_day
    ),

    html.Div(className='parent', children=[
        dcc.Graph(
            'example-graph2',
            figure=fig_pie,
            className='plot'
        ),
        html.Div(className='space'),
        dcc.Graph(
            'example-graph3',
            figure=fact_top_games_updates,
            className='plot'
        )
    ]),

        html.Div(className='parent', children=[
        dcc.Graph(
            'example-graph4',
            figure=desc_pie,
            className='plot'
        ),
        html.Div(className='space'),
        dcc.Graph(
            'example-graph5',
            figure=desc_bar,
            className='plot'
        )
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)