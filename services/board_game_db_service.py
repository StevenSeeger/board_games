import sqlite3
from services.bgg_data_request_service import get_new_ranks
from typing import NewType

DBConnection = NewType('DBConnection', sqlite3.Connection)

def create_tables(db_con: DBConnection) -> None:
    """Creates DB Tables (if they don't exist)

    This function creates all the needed tables
    if they don't previously exist

    Args:
        db_con (DBConnection) : Database DBConnection
    """
    _create_raw_top_board_games_table(db_con)
    _create_dim_board_games_table(db_con)
    _create_fact_top_games_table(db_con)
    _create_new_ranks_needed_view(db_con)
    _create_raw_new_ranks_table(db_con)
    return

def _create_raw_top_board_games_table(db_con: DBConnection) -> None:
    """Creates raw table for top board games
    
    This function creates raw_top_board_games
    when it doesn't exist

    Args:
        db_con (DBConnection) : Database DBConnection
    """
    with db_con:
        db_con.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_top_board_games (
                rank TEXT,
                bgg_id TEXT,
                name TEXT
            );
            """)
    return

def _create_dim_board_games_table(db_con: DBConnection) -> None:
    """Creates dimentional table for board games
    
    This function creates the dim_board_games
    table when it doesn't exist

    Args:
        db_con (DBConnection) : Database DBConnection
    """
    with db_con:
        db_con.execute(
        """
            CREATE TABLE IF NOT EXISTS dim_board_games (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                bgg_id INTEGER UNIQUE,
                created_date DATETIME DEFAULT current_timestamp,
                updated_date DATETIME DEFAULT current_timestamp
            );
        """
        )
    return

def _create_fact_top_games_table(db_con: DBConnection) -> None:
    """Creates fact table for top board games
    
    This function creates the fact_top_games
    table when it doesn't exist

    Args:
        db_con (DBConnection) : Database DBConnection
    """
    with db_con:
        db_con.execute(
        """
            CREATE TABLE IF NOT EXISTS fact_top_games (
                board_game_id INTEGER UNIQUE,
                rank INTEGER,
                created_date DATETIME DEFAULT current_timestamp,
                updated_date DATETIME DEFAULT current_timestamp,
            FOREIGN KEY (board_game_id) REFERENCES dim_board_games(id)
        );
        """
        )

def _create_raw_new_ranks_table(db_con: DBConnection) -> None:
    """Creates a raw datatable for new ranks
    
    This function creates the raw_new_ranks
    table when it doesn't exist

    Args:
        db_con (DBConnection) : Database DBConnection
    """
    with db_con:
        db_con.execute(
        """
            CREATE TABLE IF NOT EXISTS raw_ranks_new (
                board_game_id TEXT UNIQUE,
                rank TEXT
        );
        """
        )

def load_in_new_data(db_con: DBConnection, board_game_data: list) -> None:
    """Load in new data from BGG for Top Games

    This function uses raw data to load in new game data
    and fetches new ranks if duplicates exists

    Args:
        db_con (DBConnection) : Database DBConnection
        board_game_data (list) : Board Game Data in the format of [rank, bgg_id, name]
    """
    _load_top_games_raw(db_con, board_game_data)
    _process_new_board_games(db_con)
    _update_top_games(db_con)
    return

def _load_top_games_raw(db_con: DBConnection, board_game_data: list) -> None:
    """Load in raw top game data

    This function raw loads data from board game geeks

    Args:
        db_con (DBConnection) : Database DBConnection.
        board_game_data (list) : Board Game Data in the format of [rank, bgg_id, name]
    """
    query = 'DELETE FROM raw_top_board_games'
    with db_con:
        db_con.execute(query)

    query = 'INSERT INTO raw_top_board_games (rank, bgg_id, name) VALUES (?, ?, ?)'
    with db_con:
        db_con.executemany(query, board_game_data)

def _process_new_board_games(db_con: DBConnection) -> None:
    """Processes raw top board games

    This function process processes raw top
    board game data, and loads it into dim_board_games

    Args:
        db_con (DBConnection) : Database DBConnection.
    """
    #TODO: Get the number of new board games added
    with db_con:
        db_con.execute(
        """
            INSERT OR IGNORE INTO dim_board_games
                (name, bgg_id)
            SELECT
                name,
                CAST(bgg_id AS NUMERIC)
            FROM raw_top_board_games;
        """
        )

def _update_top_games(db_con: DBConnection) -> None: #TODO: Refactor this
    """Update fact_top_games table

    This function updates the fact_top_games table. If
    there are any conflicts with ranks, new ranking data will
    be fetched to update those tables

    Args:
        db_con (DBConnection) : Database DBConnection.
    """
    _insert_new_top_games(db_con)
    bgg_ids, update_ranks = _get_bgg_ids_that_need_new_ranks(db_con)
    if update_ranks:
        print(f"Querying and updating {len(bgg_ids)} ranks")
        new_ranks = get_new_ranks(bgg_ids)
        _update_top_ranks(new_ranks)
    else:
        print(f"`Fact Top Games` needs no updates")
    return


def _insert_new_top_games(db_con: DBConnection) -> None:
    """Insert new ranks to fact_top_games

    This function inserts new data into fact_top_games, and
    upon conflict, updates the new rank and updates the
    date_updated timestamp

    Args:
        db_con (DBConnection) : Database DBConnection.
    """
    with db_con:
        db_con.execute(
        """
            INSERT INTO fact_top_games
                (board_game_id, rank)
            SELECT
                dbg.id as board_game_id,
                CAST(rank AS NUMERIC) as rank
            FROM dim_board_games dbg
            INNER JOIN raw_top_board_games AS raw_bg
                ON dbg.bgg_id = CAST(raw_bg.bgg_id AS NUMERIC)
            ON CONFLICT(board_game_id) DO UPDATE SET rank = rank, updated_date = current_timestamp
        """
        )


def _create_new_ranks_needed_view(db_con: DBConnection) -> None:
    """Creates view for new_ranks_needed
    
    This function creates the view for when there
    are multiple board games mapped to the same
    ranking.

    Note: A view is a virtual table that pulls the
    data via saved query.

    Args:
        db_con (DBConnection) : Database DBConnection
    """
    # TODO: only get the items with the most recent date_updated to increase efficency
    # TODO: Need to also query for ranks that don't fall in the top 100
    with db_con:
        data = db_con.executescript(
            """
            CREATE VIEW IF NOT EXISTS new_ranks_needed AS
            SELECT dbg.bgg_id
            FROM fact_top_games ftg
            INNER JOIN dim_board_games dbg
                ON dbg.id = ftg.board_game_id
            WHERE rank IN (
                SELECT rank
                FROM fact_top_games
                GROUP BY rank
                HAVING COUNT(1) > 1
            );
            """
        )

def _get_bgg_ids_that_need_new_ranks(db_con: DBConnection) -> tuple[list, bool]:
    """Queries for bgg_ids that need new rank data

    This function grabs new rank data for when there
    are conflicts noted in `new_ranks_needed`.

    Args:
        db_con (DBConnection) : Database DBConnection.
    """
    bgg_ids = []
    with db_con:
        data = db_con.execute(
            """
            SELECT bgg_id
            FROM new_ranks_needed;
            """
        )

        bgg_ids = data.fetchall()
    
    if bgg_ids:
        update_needed = True
    else:
        update_needed = False

    return bgg_ids, update_needed

def _update_top_ranks(db_con: DBConnection, new_ranks: list) -> None:
    """Updates the top ranks

    This function inserts into the raw table
    and updates the new ranks

    Args:
        db_con (DBConnection) : Database DBConnection
        new_ranks (list) : List of the new ranks in format [bgg_id, rank]
    """
    _insert_raw_new_ranks(db_con, new_ranks)
    _update_new_ranks(db_con)

def _insert_raw_new_ranks(db_con: DBConnection, new_ranks: list) -> None:
    """Loads data into the raw_new_ranks table

    This function clears out the raw table and
    then loads data into the raw table

    Args:
        db_con (DBConnection) : Database DBConnection
        new_ranks (list) : List of the new ranks in format [bgg_id, rank]
    """
    query = 'DELETE FROM raw_new_ranks'
    with db_con:
        db_con.execute(query)

    query = 'INSERT INTO raw_top_board_games (bgg_id, ranks) VALUES (?, ?, ?)'
    with db_con:
        db_con.executemany(query, new_ranks)

def _update_new_ranks(db_con: DBConnection):
    """Updates fact_top_games with new ranks from raw_new_ranks

    This function updates fact_top_ranks with the
    new need ranks data

    Args:
        db_con (DBConnection) : Database DBConnection.
    """
    with db_con:
        db_con.execute(
            """
            UPDATE fact_top_games
            SET 
                fact_top_games.rank = CAST(raw_new_ranks.rank AS NUMERIC),
                date_updated = current_timestamp
            FROM
                raw_new_ranks
            WHERE
                fact_top_games.bgg_id = CAST(raw_new_ranks.bgg_id AS NUMERIC)
            """
        )

def drop_all_tables(db_con) -> None:
    """Drop all tables from the database

    This function drops all tables in the db.
    This is mainly used as a dev function when
    needing to start from fresh.

    Args:
        db_con (DBConnection): Database DBConnection
    """
    tables = ['dim_board_games', 'fact_top_games', 'raw_top_board_games']
    for table in tables:
        with db_con:
            db_con.execute(
                f"""
                DROP TABLE IF EXISTS {table};
                """
            )
    return