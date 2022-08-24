import sqlite3

con = sqlite3.connect('data/board_games.db')

new_desc_table_columns = ['date_created', 'date_updated']

def db_upgrade():
    with con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS raw_board_game_info (
                bgg_id TEXT,
                primaryname TEXT,
                description TEXT,
                yearpublished TEXT,
                minplayers TEXT,
                maxplayers TEXT,
                playingtime TEXT,
                minplaytime TEXT,
                maxplaytime TEXT,
                minage TEXT,
                boardgamecategory TEXT,
                boardgamemechanic TEXT,
                boardgamefamily TEXT,
                boardgamedesigner TEXT,
                boardgamepublisher TEXT,
                usersrated TEXT,
                average TEXT,
                bayesaverage TEXT,
                rankvalue TEXT,
                rankbayesaverage TEXT,
                stddev TEXT,
                median TEXT,
                numcomments TEXT,
                numweights TEXT,
                averageweight TEXT
            );
        ''')

if __name__ == '__main__':
    db_upgrade()