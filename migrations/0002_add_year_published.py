import sqlite3

con = sqlite3.connect('data/board_games.db')

new_columns = [['year_published', 'INTEGER'], ['min_players', 'INTEGER'], ['max_players', 'INTEGER']]

def db_upgrade():
    # with con:
    #     for column in new_columns:
    #         con.execute(
    #             f'''
    #             ALTER TABLE dim_board_games
    #             ADD COLUMN {column[0]} {column[1]};
    #             '''
    #         )
    
    with con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS descriptions_board_game (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                board_game_id INTEGER UNIQUE,
                description TEXT,
            FOREIGN KEY (board_game_id) REFERENCES dim_board_games(id)
            );
        ''')

if __name__ == '__main__':
    db_upgrade()