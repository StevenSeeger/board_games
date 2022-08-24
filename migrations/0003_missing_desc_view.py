import sqlite3

con = sqlite3.connect('data/board_games.db')

new_desc_table_columns = ['date_created', 'date_updated']

def db_upgrade():
    with con:
        con.execute('''
            CREATE VIEW IF NOT EXISTS desc_needed AS
                SELECT id AS board_game_id, bgg_id
                FROM dim_board_games
                WHERE id NOT IN (
                    SELECT DISTINCT board_game_id
                    FROM board_game_descriptions
                    WHERE description IS NOT NULL
                )
        ''')

        con.execute('''
            CREATE TABLE IF NOT EXISTS board_game_descriptions (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                board_game_id INTEGER UNIQUE,
                description TEXT,
                created_date DATETIME DEFAULT current_timestamp,
                updated_date DATETIME DEFAULT current_timestamp,
            FOREIGN KEY (board_game_id) REFERENCES dim_board_games(id)
        );
        ''')

if __name__ == '__main__':
    db_upgrade()