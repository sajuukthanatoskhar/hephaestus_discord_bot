
'''
This file contains the integration of trello, discord and eve
It contains all the labels, classes required
'''
import codecs
import json
import urllib

import trello
import discord

import eve_ESI

trello_responsible_group = {
    "Things to Buy": "Procurers",
    "Things Bought": "Packagers",
    "Production Planning Queue": "Leadership",
    "Process - Invention": "Scientist",
    "Process - Manufacturing": "Manufacturing",
    "Manufacturing Complete": "Packagers",
    "Shipping": "Freightering"
}

def status_fabrica(trello_client: trello.TrelloClient) -> dict:
    '''

    :param trello_client: the trello client connection
    :return: dictionary containing how many jobs there are
    '''
    trello_list_dict = dict()
    for trello_lists in trello_client.list_boards()[-2].list_lists():
        if not trello_lists.closed:
            trello_list_dict[trello_lists.name] = trello_lists.cardsCnt()
    return trello_list_dict


def discord_remind_manufacture_administration(discord_bot: discord.client, discord_message: discord.Message, trello_list_dict: dict) -> str:
    guild = discord_bot.guilds[0]
    for list_name in trello_list_dict.keys():
        if trello_list_dict[list_name] > 0:
            modRole = discord.utils.get(guild.roles, name=trello_responsible_group[list_name])
            yield "{} : {} needs attending to (has {})".format(modRole.mention,
                                                               list_name,
                                                               trello_list_dict[list_name])
        else:
            yield "None in {}".format(list_name)


def eve_get_assets(corp_id, location_id_filter = 1028424848158) -> list:
    '''
    Gets assets from a
    :param location_id_filter:
    :param structure_filter:
    :param corp_id:
    :param page:
    :return:
    '''
    access_token, refresh_token = eve_ESI.read_tokens("./keys.key")
    asset_data = []
    data_request = 'https://esi.evetech.net/latest/corporations/{}/assets/?datasource=tranquility&page={}&token={}'.format(corp_id, 1, access_token)
    wp = urllib.request.urlopen(data_request)
    reader = codecs.getreader("utf-8")
    max_page = wp.headers.get('X-Pages')


    for pages in range(1,int(max_page)):
        data_request = 'https://esi.evetech.net/latest/corporations/{}/assets/?datasource=tranquility&page={}&token={}'.format(
            corp_id, pages, access_token)
        wp = urllib.request.urlopen(data_request)
        wp_reader = reader(wp)
        ab = json.load(wp_reader)
        for line in ab:
            if line['location_id'] == location_id_filter and (
                    'CorpSAG' in line['location_flag'] or
                    'Deliveries' in line['location_flag']
            ):
                asset_data.append(line)

    return asset_data


def read_trello_card(trello_card: trello.Card) -> (str, int):
    """

    :param trello_card: Gets trello card for parsing
    :return: parsed item name and qty of trellocard
    """
    itemname = str
    qty = int
    qty = int(trello_card.name.split(' ')[-1])

    no_parts = len(trello_card.name.split(' '))
    itemname = ""
    for parts in range(no_parts-1):
        itemname = "{} {}".format(itemname, trello_card.name.split(' ')[parts])
    itemname = itemname.lstrip()
    return itemname, qty



def check_enough_manufactured_supplies_for_item(trello_card: trello.Card,
                                                corp_id: str,
                                                location_id_filter_list: list) -> bool:

    item_name = str
    qty = int

    item_name, qty = read_trello_card(trello_card) # From trello card, get item name and quantity
    type_id = eve_ESI.get_typeid(item_name)
    producedqty = 0
    assets_list = []
    jobs_list = []

    for location_id_filter in location_id_filter_list:
        assets_list.extend(eve_get_assets(corp_id, location_id_filter))

    for line in assets_list:
        if not line:
            continue
        if int(type_id) == line["type_id"]:
            producedqty += line["quantity"]

    sci_job_qty = check_sci_jobs_qty(trello_card, corp_id)

    return (producedqty + sci_job_qty) > qty


def check_sci_jobs_qty(trellocard: trello.Card, corp_id: str) -> int:
    """
    Checks all science jobs that are running
    :param trellocard: the trellocard that filters out the jobs
    :param corp_id:
    :return:
    """
    scijoblist = eve_get_sci_jobs(corp_id)
    item_name, qty = read_trello_card(trellocard)  # From trello card, get item name and quantity
    type_id = eve_ESI.get_typeid(item_name)
    produced_qty = 0
    for line in scijoblist:
        if int(type_id) == line['product_type_id'] and line['activity_id'] == eve_ESI.job_types.index("Manufacturing"):
            produced_qty += line['runs']
    return int(produced_qty)

def eve_get_sci_jobs(corp_id: str) -> list:
    # todo: get sci jobs
    '''
    Get a list of science jobs
    :param corp_id: corporation id
    :return:
    '''
    access_token, refresh_token = eve_ESI.read_tokens("./keys.key")
    wp = eve_ESI.req_esi(
        "corporations/{}/industry/jobs/?datasource=tranquility&include_completed=false&page=1&language=en-us&token={}".format(
            corp_id,
            access_token))
    reader = codecs.getreader("utf-8")
    wp_reader = reader(wp)
    ab = json.load(wp_reader)
    return ab


def process_cards(trello_client: trello.TrelloClient, corp_id, location_id_filter_list):
    '''
    Main control for the trello board
    :param trello_client:
    :param corp_id:
    :param location_id_filter_list:
    :return:
    '''
    import main
    boardjson = trello_client.get_board(main.corp_Trello_board_id)
    board_labels = boardjson.get_labels()
    #control_board = trello.Board().from_json(trello_client=trello_client,json_obj=boardjson)
    next_stage = 0
    finished_label = 0
    for trello_lists in boardjson.get_lists('open'):
        if 'Process - Manufacturing' in trello_lists.name:
            '''
            Manufacturing Process
            '''

            next_stage = get_list_id_by_name(boardjson, 'Manufacturing Complete')  # todo:  have a state dictionary containing what a) next list for a card and b) what the trigger label will be
            finished_label = get_label_by_name(board_labels, "Completed")

            for card in trello_lists.list_cards("open"):
                for labels in board_labels:
                    card.remove_label(labels)
                if check_enough_manufactured_supplies_for_item(card, corp_id, location_id_filter_list):
                    # card.change_list(next_stage)
                    for labels in board_labels:
                        card.remove_label(labels)
                    card.add_label(finished_label)
                    card.change_list(next_stage)
                else:
                    try:
                        card.add_label(get_label_by_name(board_labels, "Under Construction!"))
                        card.add_label(get_label_by_name(board_labels, "Ongoing"))
                    except trello.exceptions.ResourceUnavailable as e:
                        print(e)
                    # todo:  Need to have a flow of what is causing the holdup in the manufacturing section!


def get_list_id_by_name(boardjson, listname) -> str:
    for sub_trello_lists in boardjson.get_lists('open'):
        if listname in sub_trello_lists.name:
            return sub_trello_lists.id


def get_label_by_name(board_labels, label_name):
    for label in board_labels:
        if label_name == label.name:
            return label





