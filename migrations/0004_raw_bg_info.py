import sqlite3

con = sqlite3.connect('data/board_games.db')

new_desc_table_columns = ['date_created', 'date_updated']

def db_upgrade():
    with con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS raw_board_game_info (
                bgg_id TEXT,
                primary_name TEXT,
                description TEXT,
                year_published TEXT,
                min_players TEXT,
                max_players TEXT,
                playing_time TEXT,
                min_play_time TEXT,
                max_play_time TEXT,
                min_age TEXT,
                board_game_category_ids TEXT,
                board_game_category_values TEXT,
                board_game_mechanic_ids TEXT,
                board_game_mechanic_values TEXT,
                board_game_family_ids TEXT,
                board_game_family_values TEXT,
                board_game_designer_ids TEXT,
                board_game_designer_values TEXT,
                board_game_artist_ids TEXT,
                board_game_artist_values TEXT,
                board_game_publisher_ids TEXT,
                board_game_publisher_values TEXT,
                users_rated TEXT,
                average TEXT,
                bayes_average TEXT,
                rank_value TEXT,
                rank_bayes_average TEXT,
                std_dev TEXT,
                median TEXT,
                num_comments TEXT,
                num_weights TEXT,
                average_weight TEXT
            );
        ''')

if __name__ == '__main__':
    db_upgrade()