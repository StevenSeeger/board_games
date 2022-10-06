import sqlite3
from typing import NewType
import sys
import re

sys.path.append('../board_games')
DBConnection = NewType('DBConnection', sqlite3.Connection)

from services.bgg_data_request_service import get_top_games, get_hot_games, get_new_ranks, get_all_board_game_data
from services.board_game_db_service import _update_top_ranks, process_raw_bg_data

MAPPED_TABLES = [
    ["categories", "category"], 
    ["mechanics", "mechanic"],
    ["families", "family"],
    ["designers", "designer"],
    ["artists", "artist"],
    ["publishers", "publisher"]
]

MAPPED_TABLES_DICT = {
    "categories": "category", 
    "mechanics": "mechanic",
    "families": "family",
    "designers": "designer",
    "artists": "artist",
    "publishers": "publisher"
}

def load_in_raw_top_games(db_con):
    """Load ins in top games from bgg into raw table

    This funciton requests the top 100 board games from board game geeks and
    places them into a raw top board game table

    Args:
        db_con: DataBase Connection
    """

    new_top_games = get_top_games()
    query = 'DELETE FROM raw_top_board_games;'

    with db_con.cursor() as curs:
        curs.execute(query)

    query = 'INSERT INTO raw_top_board_games (rank, bgg_id, name) VALUES (%s, %s, %s)'

    with db_con.cursor() as curs:
        curs.executemany(query, new_top_games)

def load_in_raw_hot_games(db_con):
    """Load ins in top games from bgg into raw table

    This funciton requests the top 100 board games from board game geeks and
    places them into a raw top board game table

    Args:
        db_con: DataBase Connection
    """

    new_hot_games = get_hot_games()
    query = 'DELETE FROM raw_hot_board_games;'
    with db_con.cursor() as curs:
        curs.execute(query)

    query = 'INSERT INTO raw_hot_board_games (hot_rank, bgg_id, name) VALUES (%s, %s, %s)'

    with db_con.cursor() as curs:
        curs.executemany(query, new_hot_games)

def process_raw_board_games(db_con: DBConnection, type: str) -> None:
    """Processes raw board games

    This function process processes raw
    board game data, and loads it into dim_board_games

    Args:
        db_con (DBConnection) : Database DBConnection.
    """
    #TODO: Get the number of new board games added
    with db_con.cursor() as curs:
        curs.execute(
        f"""
            INSERT INTO dim_board_games
                (name, bgg_id)
            SELECT
                name,
                CAST(bgg_id AS NUMERIC)
            FROM raw_{type}_board_games
            ON CONFLICT (bgg_id) DO NOTHING;
        """
        )

def insert_new_top_games(db_con: DBConnection) -> None:
    """Insert new ranks to fact_top_games

    This function inserts new data into fact_top_games, and
    upon conflict, updates the new rank and updates the
    date_updated timestamp

    Args:
        db_con (DBConnection) : Database DBConnection.
    """
    with db_con.cursor() as curs:
        curs.execute(
        """
            INSERT INTO fact_top_games
                (board_game_id, rank)
            SELECT
                dbg.id as board_game_id,
                CAST(rank AS NUMERIC) as rank
            FROM dim_board_games dbg
            INNER JOIN raw_top_board_games AS raw_bg
                ON dbg.bgg_id = CAST(raw_bg.bgg_id AS NUMERIC)
            ON CONFLICT(board_game_id) DO UPDATE SET rank = EXCLUDED.rank, updated_date = current_timestamp;
        """
        )

def update_ranks(db_con):

    with db_con.cursor() as curs:
        results = curs.execute("""
            SELECT bgg_id
            FROM new_ranks_needed;
        """)
        bgg_ids = curs.fetchall()

    if bgg_ids == []:
        return

    new_ranks = get_new_ranks(bgg_ids)

    _update_top_ranks(db_con, new_ranks)

def get_needed_board_game_data(db_con):
    with db_con.cursor() as curs:
        curs.execute("""
            DELETE FROM raw_board_game_info;
        """)

    with db_con.cursor() as curs:
        results = curs.execute("""
            SELECT DISTINCT bgg_id
            FROM dim_board_games
            WHERE description IS NULL;
        """)

        bgg_ids = curs.fetchall()

    if bgg_ids == []:
        return
    
    for id in bgg_ids:
        _query_raw_board_game_data(db_con, id)

def _query_raw_board_game_data(db_con, bgg_id):

    data = get_all_board_game_data(bgg_id)

    with db_con.cursor() as curs:
        query = """
        INSERT INTO raw_board_game_info (
            bgg_id, primary_name, description, year_published, min_players, max_players, playing_time, min_play_time,
            max_play_time, min_age, board_game_category_ids, board_game_category_values, board_game_mechanic_ids,
            board_game_mechanic_values, board_game_family_ids, board_game_family_values, board_game_designer_ids,
            board_game_designer_values, board_game_artist_ids, board_game_artist_values, board_game_publisher_ids,
            board_game_publisher_values, users_rated, average, bayes_average, rank_value, rank_bayes_average,
            std_dev, median, num_comments, num_weights, average_weight
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        curs.execute(query, data)

def update_bg_mapped_tables(db_con, table_name):
    column_name = MAPPED_TABLES_DICT[table_name]

    print(f"Working on `{table_name}` table")
    with db_con.cursor() as curs:
        query = f"""
        SELECT board_game_{column_name}_ids, board_game_{column_name}_values
        FROM raw_board_game_info
        """
        results = curs.execute(query)
        
        data = curs.fetchall()

    if data == []:
        return

    all_ids = []
    all_values = []
    for row in data:
        if row[0] == "":
            continue
        int_ids = row[0].split("|")
        int_ids = list(map(int, int_ids))
        all_ids.extend(int_ids)
        all_values.extend(row[1].split("|"))

    data = set(zip(all_ids, all_values))
    
    with db_con.cursor() as curs:
        query = f"""
        INSERT INTO {table_name} (bgg_{column_name}_id, name)
        VALUES (%s, %s)
        ON CONFLICT(bgg_{column_name}_id) DO NOTHING
        """
        curs.executemany(query, data)