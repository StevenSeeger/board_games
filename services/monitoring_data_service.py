import pandas as pd
import plotly.express as px


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


def apply_layout(func):
    """Applies default layout on plots"""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        result.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
        return result
    return wrapper

@apply_layout
def create_num_per_rank_data(db_con) -> px.pie:
    with db_con:
        data = db_con.execute(
            """
            WITH num_per_rank AS (
                SELECT rank, COUNT(1) AS num_per_rank
                FROM fact_top_games
                GROUP BY 1
                ORDER BY 2 DESC
            )
            SELECT
                CASE WHEN rank IS NULL THEN 'No Ranking' ELSE num_per_rank END,
                SUM(num_per_rank) AS num_of_each_rank
            FROM num_per_rank
            GROUP BY 1
            """
        )
        data = data.fetchall()
    df = pd.DataFrame(data, columns=['Unique Counts per Rank', 'Count'])
    fig_pie = px.pie(
        df,
        names='Unique Counts per Rank',
        values='Count',
        title="Unique Count per Rank<br><sup>fact_top_games</sup>",
        hole=.5
    )
    return fig_pie

@apply_layout
def graph_num_games_created_per_date(db_con) -> px.bar:

    with db_con:
        data = db_con.execute(
            """
            SELECT 
                date(created_date) AS date,
                'Created',
                COUNT(1)
            FROM dim_board_games
            GROUP BY 1

            UNION ALL

            SELECT 
                date(updated_date) AS date,
                'Updated',
                COUNT(1)
            FROM dim_board_games
            GROUP BY 1
            ORDER BY 1 DESC
            LIMIT 60
            """
        )
        data = data.fetchall()
    df = pd.DataFrame(data, columns=['Date', 'Type', 'Count'])
    fig = px.bar(df, x='Date', y='Count', title='Num Board Games Per Day<br><sup>dim_board_games</sup>', color='Type', barmode='group')
    fig.update_xaxes(dtick=86400000)
    fig.update_layout(bargroupgap=0.0, barmode='group', bargap=0.75, xaxis={"rangeslider":{"visible":True}})
    return fig

@apply_layout
def graph_fact_top_games_date_affected(db_con) -> px.bar:
    with db_con:
        data = db_con.execute(
            """
            SELECT 
                date(created_date) AS date,
                'Created',
                COUNT(1)
            FROM fact_top_games
            GROUP BY 1

            UNION ALL

            SELECT 
                date(updated_date) AS date,
                'Updated',
                COUNT(1)
            FROM fact_top_games
            GROUP BY 1
            ORDER BY 1 DESC
            LIMIT 30
            """
        )
        data = data.fetchall()
    df = pd.DataFrame(data, columns=['Date', 'Type', 'Count'])
    fig = px.bar(df, x='Date', y='Count', title='Rank Created/Updated<br><sup>fact_top_games</sup>', color='Type', barmode='group')
    fig.update_xaxes(dtick=86400000)
    fig.update_yaxes(range = [0,10])
    fig.update_layout(bargroupgap=0.0, barmode='group', bargap=0.75, xaxis={"rangeslider":{"visible":True}})
    return fig

@apply_layout
def pie_bg_descriptions(db_con) -> px.pie:
    with db_con:
        data = db_con.execute(
            """
            SELECT 
                CASE 
                    WHEN description IS NULL THEN 'no_description'
                    ELSE 'has_description'
                END AS no_description,
                COUNT(1) AS count
            FROM dim_board_games
            GROUP BY 1;
            """
        )
        data = data.fetchall()
    df = pd.DataFrame(data, columns=['Description', 'Count'])
    fig_pie = px.pie(
        df,
        names='Description',
        values='Count',
        title="% of Board Games w/ Descriptions",
        hole=.5
    )
    return fig_pie

@apply_layout
def graph_bg_descriptions_dates(db_con) -> px.bar:
    with db_con:
        data = db_con.execute(
            """
            SELECT 
                date(created_date) AS date,
                'Created',
                COUNT(1)
            FROM dim_board_games
            GROUP BY 1

            UNION ALL

            SELECT 
                date(updated_date) AS date,
                'Updated',
                COUNT(1)
            FROM dim_board_games
            GROUP BY 1
            ORDER BY 1 DESC
            LIMIT 20
            """
        )
        data = data.fetchall()
    df = pd.DataFrame(data, columns=['Date', 'Type', 'Count'])
    fig = px.bar(df, x='Date', y='Count', title='Descriptions Scraped<br><sup>Created & Updated</sup>', color='Type', barmode='group')
    fig.update_xaxes(dtick=86400000)
    fig.update_layout(bargroupgap=0.0, barmode='group', bargap=0.75, xaxis={"rangeslider":{"visible":True}})
    return fig