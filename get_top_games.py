from services.bgg_data_request_service import get_top_games, get_hot_games
from services.board_game_db_service import create_tables, drop_all_tables, load_in_hot_board_games, load_in_top_board_games
import sqlite3

def main():
    con = sqlite3.connect('data/board_games.db')
    create_tables(con)
    top_games = get_top_games()
    load_in_top_board_games(con, top_games)
    hot_games = get_hot_games()
    load_in_hot_board_games(con, hot_games)
    return

if __name__ == "__main__":
    main()