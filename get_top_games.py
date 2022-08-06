from bgg_data_request_service import get_top_games
from board_game_db_service import create_tables, drop_all_tables, load_in_new_data
import sqlite3

def main():
    con = sqlite3.connect('data/board_games.db')
    create_tables(con)
    top_games = get_top_games()
    load_in_new_data(con, top_games)
    return

if __name__ == "__main__":
    main()