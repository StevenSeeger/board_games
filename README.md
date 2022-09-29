# Board Game Tracking

This is a project to learn better ETL practices, create dashboard to track ETL services/pipelines, etc. Eventually, I would like to start doing some ML stuff on board games, but I gotta get more board game data first.

## Airflow

Airflow is setup at the port: 2000

Install airflow, and follow the setup instructions from: `https://airflow.apache.org/`. You may need to change the config file to point to the dags file in this project.

## Postgres

Postgres is on the default port

Set up a postgres database. To kickstart your database with some data, you can use pgloader to load up the data from `board_games.db` in the data folder, but that data should be considered old and dead. In order to do this, install the command line tool `pgloader` and run the `migrate_to_psql.db` with pgloader. This will look like `pgloader migrate_to_psql.db`. You can update the `migrate_to_psql.db` to point the correct username and password, or you can make a user named `pgloader_role` with the password `password` and load up the data that way. Also, please don't `@` me about the insecure password. Same with the fact that I have a user named `steven` with no password.


## Dash(board)

Dash is on thr port: 8050

^ Wow I am too funny.

### Board Game Data Monitoring

This is a simple dashboard to view the health of the data that was read in. This ideally is used as quick peek and glance to make sure that the daily ETL ran correctly. The purpose of having this sitting outside of airflow (which aruably also reports the health of the ETL pipeline) is to look at the meta-data and metrics behind the data. If a day ever sees a large increase, or there are mulitple board games with the same rank, we would expect to see this here.