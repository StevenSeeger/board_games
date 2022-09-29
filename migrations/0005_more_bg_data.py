import sqlite3

con = sqlite3.connect('data/board_games.db')

new_columns = [
        ['playing_time', 'INTEGER'], 
        ['min_play_time', 'INTEGER'],
        ['max_play_time', 'INTEGER'],
        ['min_age', 'INTEGER'],
        ['board_game_category_ids', 'TEXT'],
        ['board_game_mechanic_ids', 'TEXT'],
        ['board_game_family_ids', 'TEXT'],
        ['board_game_designer_ids', 'TEXT'],
        ['board_game_publisher_ids', 'TEXT'],
        ['users_rated', 'INTEGER'],
        ['average', 'REAL'],
        ['bayes_average', 'REAL'],
        ['rank_value', 'REAL'],
        ['rank_bayes_average', 'REAL'],
        ['std_dev', 'REAL'],
        ['median', 'REAL'],
        ['num_comments', 'INTEGER'],
        ['num_weights', 'INTEGER'],
        ['average_weight', 'REAL']
    ]

['bgg_id', 'TEXT'],
['primary_name', 'TEXT'],
['description', 'TEXT'],
['year_published', 'TEXT'],
['min_players', 'TEXT'],
['max_players', 'TEXT'],
['playing_time', 'TEXT'],
['min_play_time', 'TEXT'],
['max_play_time', 'TEXT'],
['min_age', 'TEXT'],
['board_game_category_ids', 'TEXT'],
['board_game_category_values', 'TEXT'],
['board_game_mechanic_ids', 'TEXT'],
['board_game_mechanic_values', 'TEXT'],
['board_game_family_ids', 'TEXT'],
['board_game_family_values', 'TEXT'],
['board_game_designer_ids', 'TEXT'],
['board_game_designer_values', 'TEXT'],
['board_game_artist_ids', 'TEXT'],
['board_game_artist_values', 'TEXT'],
['board_game_publisher_ids', 'TEXT'],
['board_game_publisher_values', 'TEXT'],
['users_rated', 'TEXT'],
['average', 'TEXT'],
['bayes_average', 'TEXT'],
['rank_value', 'TEXT'],
['rank_bayes_average', 'TEXT'],
['std_dev', 'TEXT'],
['median', 'TEXT'],
['num_comments', 'TEXT'],
['num_weights', 'TEXT'],
['average_weight', 'TEXT']

def db_upgrade():
    with con:
        for column in new_columns:
            con.execute(
                f'''
                ALTER TABLE dim_board_games
                ADD COLUMN {column[0]} {column[1]};
                '''
            )

if __name__ == '__main__':
    db_upgrade()