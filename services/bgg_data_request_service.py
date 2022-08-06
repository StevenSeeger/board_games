from typing import List
from xmlrpc.client import ResponseError
import requests
import re

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
    rank = rank_pattern.search(response_stats).group(0)
    rank = int(re.search(r'\d+', rank).group())

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
