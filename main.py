# bot.py
import codecs
import datetime
import os
import json
import sys
from time import sleep
from trello import TrelloClient, exceptions
import discord
from dotenv import load_dotenv
import pythonserver
import authpython
import threading
import eve_ESI
TRYRM_corp_id = '98250435'


def status_fabrica():
    a = "```List\t\t\t\t\t\t\t\t\t\t\t\tNumber of cards\n"
    for i in trello_client.list_boards()[-2].list_lists():

        if not i.closed:
            a = a + i.name + "\t\t\t\t\t\t\t\t\t\t\t\t" + str(i.cardsCnt()) + '\n'
    a += "```"
    return a

def get_refreshkey():
    f = open("keys.key", "r")
    refresh_key = f.read().split(" ")[1]
    return refresh_key


def get_accesstoken():
    f = open("keys.key", "r")
    accesstoken = f.read().split(" ")[0]
    return accesstoken


if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    trello_token = os.getenv('TRELLO_TOKEN')
    trello_key = os.getenv('TRELLO_KEY')
    eve_id = os.getenv('EVE_CLIENT_ID')
    eve_secret = os.getenv('EVE_SECRET_KEY')


    trello_client = TrelloClient(
        api_key=trello_key,
        api_secret=trello_token
    )

    # what the fuck is going on here.

    if len(sys.argv) == 1:
        a = pythonserver.run(eve_id)
    else:
        a = authpython.refresh(eve_id, eve_secret, get_refreshkey())
        file_1_write = open("keys.key", "w")
        file_1_write.write("%s %s" % (a['access_token'], a['refresh_token']))
        # file_1_write.write("%s %s" % (pw['token_id'],pw['refresh_id']))
        file_1_write.close()

    reader = codecs.getreader("utf-8")

    client = discord.Client()


    @client.event
    async def on_ready():
        guild = ""
        for guild in client.guilds:
            if guild.name == GUILD:
                break

        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )


    def get_jobs(wp):
        
        fp = json.load(reader(wp))
        joblist = str(fp)
        joblist = (joblist[:1998] + '..') if len(joblist) > 1998 else joblist
        return joblist


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.content == '!status_fabrica':
            response = "Control link established with A5MT Sotiyo Control"
            await message.channel.send(response)
            sleep(0.5)
            await message.channel.send('...\nEstablished! \nFURTHER INPUT REQUIRED!')
            try:
                await message.channel.send('....Trello located\n{}'.format(status_fabrica()))
            except exceptions.ResourceUnavailable:
                await message.channel.send('ERROR! \nhttps://i.imgur.com/a1V5gYj.jpg ')
        if message.content == '!status_fabrica jobs':

            wp = eve_ESI.req_esi("corporations/{}/industry/jobs/".format(
            TRYRM_corp_id) + "?datasource=tranquility&include_completed=false&page=1&language=en-us&token=" +
                             get_accesstoken())
            await message.channel.send(get_jobs(wp))
            # except Exception:
                # await message.channel.send("Beep boop, sorry you just fucked up")
                # sleep(0.5)
                # await message.channel.send("https://i.imgur.com/5IJXLW9.gif")

    client.run(TOKEN)
