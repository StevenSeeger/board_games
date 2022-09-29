from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

import sys

sys.path.append('../board_games/')

from services.bgg_data_request_service import get_top_games
from services.board_game_db_service import load_in_top_board_games, get_board_game_descriptions, process_raw_bg_data
from services.airflow_services import load_in_raw_top_games, load_in_raw_hot_games, \
    process_raw_board_games, insert_new_top_games, update_ranks, get_needed_board_game_data, update_bg_mapped_tables
import psycopg2

con = psycopg2.connect(database="board_game", user='steven')

# import sqlite3

# con = sqlite3.connect('data/board_games.db')

default_args = {
    'owner': 'steven',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['sseeger1996@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    'get_hot_and_top_board_games',
    default_args=default_args,
    description='Load in New Top & Hot Board Games',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['board_games'],
) as dag:
    raw_top=PythonOperator(
        task_id='load_in_raw_top_games',
        python_callable=load_in_raw_top_games,
        op_kwargs={'db_con': con}
    )

    raw_hot=PythonOperator(
        task_id='load_in_raw_hot_games',
        python_callable=load_in_raw_hot_games,
        provide_context=True,
        op_kwargs={'db_con': con}
    )

    process_top=PythonOperator(
        task_id='process_top_games',
        python_callable=process_raw_board_games,
        op_kwargs={'db_con': con, 'type': 'top'}
    )

    process_hot=PythonOperator(
        task_id='process_hot_games',
        python_callable=process_raw_board_games,
        op_kwargs={'db_con': con, 'type': 'hot'}
    )

    new_ranks=PythonOperator(
        task_id='add_new_ranks',
        python_callable=insert_new_top_games,
        op_kwargs={'db_con': con}
    )

    get_raw_board_game_data=PythonOperator(
        task_id='get_raw_board_game_data',
        python_callable=get_needed_board_game_data,
        provide_context=True,
        op_kwargs={'db_con': con}
    )

    process_raw_bg_data=PythonOperator(
        task_id='process_raw_bg_data',
        python_callable=process_raw_bg_data,
        provide_context=True,
        op_kwargs={'db_con': con}
    )
    
    update_rankings=PythonOperator(
        task_id='update_bgg_ranks',
        python_callable=update_ranks,
        provide_context=True,
        op_kwargs={'db_con': con}
    )

    update_publishers_table=PythonOperator(
        task_id='update_publishers_table',
        python_callable=update_bg_mapped_tables,
        provide_context=True,
        op_kwargs={'db_con': con, 'table_name': 'publishers'}
    )

    update_categories_table=PythonOperator(
        task_id='update_categories_table',
        python_callable=update_bg_mapped_tables,
        provide_context=True,
        op_kwargs={'db_con': con, 'table_name': 'categories'}
    )

    update_mechanics_table=PythonOperator(
        task_id='update_mechanics_table',
        python_callable=update_bg_mapped_tables,
        provide_context=True,
        op_kwargs={'db_con': con, 'table_name': 'mechanics'}
    )

    update_families_table=PythonOperator(
        task_id='update_families_table',
        python_callable=update_bg_mapped_tables,
        provide_context=True,
        op_kwargs={'db_con': con, 'table_name': 'families'}
    )

    update_designers_table=PythonOperator(
        task_id='update_designers_table',
        python_callable=update_bg_mapped_tables,
        provide_context=True,
        op_kwargs={'db_con': con, 'table_name': 'designers'}
    )

    update_artists_table=PythonOperator(
        task_id='update_artists_table',
        python_callable=update_bg_mapped_tables,
        provide_context=True,
        op_kwargs={'db_con': con, 'table_name': 'artists'}
    )

    #Top Board Games
    raw_top >> process_top 
    process_top >> get_raw_board_game_data
    process_top >> new_ranks
    new_ranks >> update_rankings

    #Hot Board Gmaes
    raw_hot >> process_hot
    process_hot >> get_raw_board_game_data

    #Get Board Game Data
    get_raw_board_game_data >> process_raw_bg_data
    get_raw_board_game_data >> [update_publishers_table, update_categories_table, update_mechanics_table,
        update_families_table, update_designers_table, update_artists_table]

    #Finish by getting needed new ranks
    process_hot >> update_rankings