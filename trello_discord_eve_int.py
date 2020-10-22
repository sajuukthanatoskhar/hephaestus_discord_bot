
'''
This file contains the integration of trello, discord and eve
It contains all the labels, classes required
'''
import trello
import discord
trello_responsible_group = {
    "Things to Buy": "Procurers",
    "Things Bought": "Packagers",
    "Production Planning Queue": "Leadership",
    "Process - Invention": "Scientist",
    "Process - Manufacturing": "Manufacturing",
    "Manufacturing Complete": "Packagers",
    "Shipping": "Freightering"
}

def get_trello_jobs() -> list:
    '''
    Gets the
    :return: list
    '''
    joblist = []

    # todo: get list

    return joblist


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
