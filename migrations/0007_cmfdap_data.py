import sqlite3

con = sqlite3.connect('data/board_games.db')

MAPPED_TABLES = [
    ["categories", "category"], 
    ["mechanics", "mechanic"],
    ["families", "family"],
    ["designers", "designer"],
    ["artists", "artist"],
    ["publishers", "publisher"]
]

def db_upgrade():
    with con:
        for table in MAPPED_TABLES:
            con.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table[0]} (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                bgg_{table[1]}_id INTEGER UNIQUE,
                name TEXT,
                created_date DATETIME DEFAULT current_timestamp,
                updated_date DATETIME DEFAULT current_timestamp
                )
                """
            )

def db_downgrade():
    with con:
        for table in MAPPED_TABLES:
            con.execute(
                f"""
                DROP TABLE {table[0]}
                """
            )

if __name__ == '__main__':
    db_downgrade()
    db_upgrade()