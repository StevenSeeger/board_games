import string
from typing import List
from xmlrpc.client import ResponseError
import xmltodict
import requests
import re
import html
import time

def get_top_games() -> List:
    response_list = _get_data()

    # Getting Rank
    rank_pattern = re.compile("name=\"\d+\"")
    name_rank = rank_pattern.search(response_list[1]).group(0)
    rank = name_rank.split('"')[1]

    # Getting the id and name
    href_pattern = re.compile("href=\".*\" >")
    href = href_pattern.search(response_list[1]).group(0)
    id = href.split('/')[2]
    name = href.split('/')[3].split('"')[0]

    # Getting rank, id and name

    # regex patterns
    rank_pattern = re.compile("name=\"\d+\"")
    href_pattern = re.compile("href=\".*\" >")

    top_games = []

    for game in response_list:

        name_rank = rank_pattern.search(game).group(0)
        rank = name_rank.split('"')[1]

        href = href_pattern.search(game).group(0)
        id = href.split('/')[2]
        name = href.split('/')[3].split('"')[0]

        top_games.append((rank, id, name))

    return top_games

def get_hot_games() -> List:
    api_url = "https://boardgamegeek.com/xmlapi2/hot?boardgame"
    response = requests.get(api_url, stream=True)
    game_list = xmltodict.parse(response.content)['items']['item']
    hot_50 = []
    for game in game_list:
        hot_50.append([game['@rank'], game['@id'], game['name']['@value']])
    
    return hot_50

def _get_data() -> List:
    url = 'https://boardgamegeek.com/browse/boardgame'
    response = requests.get(url, stream=True)

    response_str = str(response.content)
    response_list = response_str.split("tr id=\\\'row_\\\'")
    del response_list[0] # REMOVING METADATA

    return response_list

def _get_rank_from_bgg_id(bgg_id: int) -> int:
    url = f'https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}&stats=1'
    response = requests.get(url, stream=True)
    
    response_str = str(response.content)
    response_stats = response_str.split("<statistics page=")[1]

    rank_pattern = re.compile("\"Board Game Rank\" value=\"\d+\"")
    rank = rank_pattern.search(response_stats)
    if rank is None:
        return None
    rank = rank.group(0)
    rank = re.search(r'\d+', rank).group()
    if rank:
        rank = int(rank)

    return rank

def get_new_ranks(bgg_ids: list) -> list:
    """
    Cool Documentation
    """
    new_ranks = []
    for bgg_id in bgg_ids:
        rank = _get_rank_from_bgg_id(bgg_id[0])
        new_ranks.append([bgg_id[0], rank])

    return new_ranks

def get_board_game_description(bgg_id: int) -> string:
    url = f'https://boardgamegeek.com/xmlapi2/thing?id={bgg_id}&stats=1'
    response = requests.get(url, stream=True)
    
    response_str = str(response.content)
    response_desc = re.split(r'</?description>', response_str)
    if len(response_desc) == 1:
        return None
    else:
        response_desc = response_desc[1]
    for _ in range(3):
        response_desc = html.unescape(response_desc)

    response_desc = response_desc.strip('\n')
    response_desc = response_desc.strip('\t')
    response_desc = re.sub(r'\s+', ' ', response_desc)
    # response_desc = re.escape(response_desc)

    return response_desc

def _clean_board_game_description(description):

    for _ in range(3):
        description = html.unescape(description)

    description = description.strip('\n')
    description = description.strip('\t')
    description = re.sub(r'\s+', ' ', description)

    return description

def get_all_board_game_data(bgg_id: int) -> list:
    url = f'https://boardgamegeek.com/xmlapi2/thing?id={bgg_id[0]}&stats=1'
    print(url)
    response = requests.get(url, stream=True)

    parsed = xmltodict.parse(response.content)
    if parsed == {'error': {'message': 'Rate limit exceeded.'}}:
        time.sleep(10)
        return get_all_board_game_data(bgg_id)
    else:
        game_data = parsed['items']['item']

    bgg_id = str(bgg_id[0])

    if type(game_data['name']) == list:
        name = game_data['name'][0]['@value']
    else:
        name = game_data['name']['@value']

    description = game_data['description']
    description = _clean_board_game_description(description)
    year_published = game_data['yearpublished']['@value']
    min_players = game_data['minplayers']['@value']
    max_players = game_data['maxplayers']['@value']
    playing_time = game_data['playingtime']['@value']
    min_play_time = game_data['minplaytime']['@value']
    max_play_time = game_data['maxplaytime']['@value']
    min_age = game_data['minage']['@value']

    # Parse apart array data
    board_game_category_ids = []
    board_game_category_values = []
    board_game_mechanic_ids = []
    board_game_mechanic_values = []
    board_game_family_ids = []
    board_game_family_values = []
    board_game_designer_ids = []
    board_game_designer_values = []
    board_game_artist_ids = []
    board_game_artist_values = []
    board_game_publisher_ids = []
    board_game_publisher_values = []
    for item in game_data['link']:
        if item['@type'] == 'boardgamecategory':
            board_game_category_ids.append(item['@id'])
            board_game_category_values.append(item['@value'])
        elif item['@type'] == 'boardgamemechanic':
            board_game_mechanic_ids.append(item['@id'])
            board_game_mechanic_values.append(item['@value'])
        elif item['@type'] == 'boardgamefamily':
            board_game_family_ids.append(item['@id'])
            board_game_family_values.append(item['@value'])
        elif item['@type'] == 'boardgamedesigner':
            board_game_designer_ids.append(item['@id'])
            board_game_designer_values.append(item['@value'])
        elif item['@type'] == 'boardgameartist':
            board_game_artist_ids.append(item['@id'])
            board_game_artist_values.append(item['@value'])
        elif item['@type'] == 'boardgamepublisher':
            board_game_publisher_ids.append(item['@id'])
            board_game_publisher_values.append(item['@value'])



    board_game_category_ids = '|'.join(board_game_category_ids)
    board_game_category_values = '|'.join(board_game_category_values)
    board_game_mechanic_ids = '|'.join(board_game_mechanic_ids)
    board_game_mechanic_values = '|'.join(board_game_mechanic_values)
    board_game_family_ids = '|'.join(board_game_family_ids)
    board_game_family_values = '|'.join(board_game_family_values)
    board_game_designer_ids = '|'.join(board_game_designer_ids)
    board_game_designer_values = '|'.join(board_game_designer_values)
    board_game_artist_ids = '|'.join(board_game_artist_ids)
    board_game_artist_values = '|'.join(board_game_artist_values)
    board_game_publisher_ids = '|'.join(board_game_publisher_ids)
    board_game_publisher_values = '|'.join(board_game_publisher_values)

    #Parse apart statistics data    
    users_rated = game_data['statistics']['ratings']['usersrated']['@value']
    average = game_data['statistics']['ratings']['average']['@value']
    bayes_average = game_data['statistics']['ratings']['bayesaverage']['@value']

    if type(game_data['statistics']['ratings']['ranks']['rank']) == list:
        rank_value = game_data['statistics']['ratings']['ranks']['rank'][0]['@value']
    else:
        rank_value = game_data['statistics']['ratings']['ranks']['rank']['@value']
    if type(game_data['statistics']['ratings']['ranks']['rank']) == list:
        rank_bayes_average = game_data['statistics']['ratings']['ranks']['rank'][0]['@bayesaverage']
    else:
        rank_bayes_average = game_data['statistics']['ratings']['ranks']['rank']['@bayesaverage']

    std_dev = game_data['statistics']['ratings']['stddev']['@value']
    median = game_data['statistics']['ratings']['median']['@value']
    num_comments = game_data['statistics']['ratings']['numcomments']['@value']
    num_weights = game_data['statistics']['ratings']['numweights']['@value']
    average_weight = game_data['statistics']['ratings']['averageweight']['@value']
    

    return bgg_id, name, description, year_published, min_players, max_players, playing_time, min_play_time, \
        max_play_time, min_age, board_game_category_ids, board_game_category_values, board_game_mechanic_ids, \
        board_game_mechanic_values, board_game_family_ids, board_game_family_values, board_game_designer_ids, \
        board_game_designer_values, board_game_artist_ids, board_game_artist_values, board_game_publisher_ids, \
        board_game_publisher_values, users_rated, average, bayes_average, rank_value, rank_bayes_average, \
        std_dev, median, num_comments, num_weights, average_weight