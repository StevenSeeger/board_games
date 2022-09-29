import sqlite3

con = sqlite3.connect('data/board_games.db')

new_columns = [
        ['description', 'TEXT'],
        ['year_published', 'INTEGER'],
        ['min_players', 'INTEGER'],
        ['max_players', 'INTEGER'],
        ['playing_time', 'INTEGER'],
        ['min_play_time', 'INTEGER'],
        ['max_play_time', 'INTEGER'],
        ['min_age', 'INTEGER'],
        ['board_game_category_ids', 'TEXT'],
        ['board_game_mechanic_ids', 'TEXT'],
        ['board_game_family_ids', 'TEXT'],
        ['board_game_designer_ids', 'TEXT'],
        ['board_game_artist_ids', 'TEXT'],
        ['board_game_publisher_ids', 'TEXT'],
        ['users_rated', 'REAL'],
        ['average', 'REAL'],
        ['bayes_average', 'REAL'],
        ['rank_value', 'INTEGER'],
        ['rank_bayes_average', 'REAL'],
        ['std_dev', 'REAL'],
        ['median', 'REAL'],
        ['num_comments', 'INTEGER'],
        ['num_weights', 'INTEGER'],
        ['average_weight', 'REAL']
    ]

def db_upgrade():
    with con:
        for column in new_columns:
            try:
                con.execute(
                    f'''
                    ALTER TABLE dim_board_games
                    ADD COLUMN {column[0]} {column[1]};
                    '''
                )
            except:
                print(f"{column} most likely already existed")

if __name__ == '__main__':
    db_upgrade()