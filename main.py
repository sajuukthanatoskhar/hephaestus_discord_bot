# bot.py
import asyncio
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
import trello_discord_eve_int

# todo: Fix this and put it in env
corp_Trello_board_id = "54eedff17c7956435a32dc06"

TRYRM_corp_id = '98250435'
manufacturing_admin = 712327259368980480  # for discord
A5MT_sotiyo = 1028387211434 # sotiyo in a5mt (for build jobs)
A5MT_sotiyo_buildhangar = 1028424848158 # Sotiyo in A5MT
D_P_Pyongyang = 1024956767814 # Keepstar in D-PNP9
# A5MT_Tatara =

location_id_filter_list = [A5MT_sotiyo, D_P_Pyongyang]  # Expand as needed

def status_fabrica():
    a = "```List\t\t\t\t\t\t\t\t\t\t\t\tNumber of cards\n"
    for i in trello_client.list_boards()[-2].list_lists():

        if not i.closed:
            a = a + i.name + "\t\t\t\t\t\t\t\t\t\t\t\t" + str(i.cardsCnt()) + '\n'
    a += "```"
    return a

# def get_refreshkey():
#     f = open("keys.key", "r")
#     refresh_key = f.read().split(" ")[1]
#     return refresh_key





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

    if len(sys.argv) == 1:
        # If we need to make a new api key
        a = pythonserver.run(eve_id)
    else:
        # if we dont need to (we made one <1200 seconds)
        refreshed_keys = authpython.refresh(eve_id,
                                            eve_secret,
                                            pythonserver.get_refreshkey())
        pythonserver.write_new_keys_file(refreshed_keys)  # todo: could be moved to authpython, under authpython.refresh

    refresh_key_thread = threading.Thread(target=pythonserver.refresh_keys, args=(eve_id, eve_secret), daemon=True)
    refresh_key_thread.start()
    reader = codecs.getreader("utf-8")
    client = discord.Client()


    async def trello_status():
        channel = client.get_channel(manufacturing_admin) # This is manufacturing-administration
        while True:
            await asyncio.sleep(21600)
            for msg in trello_discord_eve_int.discord_remind_manufacture_administration(client,
                                                                                        channel,
                                                                                        trello_discord_eve_int.status_fabrica(
                                                                                            trello_client)):
                await channel.send(msg)



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

        client.loop.create_task(trello_status())

    def get_trello_jobs():
        """
        Gets trello jobs
        :return:
        """
        return

    def get_jobs_long(wp):
        """

        :param wp:
        :return:
        """
        fp = json.load(reader(wp))
        joblist = str(fp)
        return joblist

    def get_jobs(wp):
        """

        :param wp:
        :return: list of jobs being run in corp
        """
        fp = json.load(reader(wp))
        joblist = str(fp)
        joblist = (joblist[:1998] + '..') if len(joblist) > 1998 else joblist
        return joblist


    def get_delivery_jobs():
        pass


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.content == '!status_fabrica':
            await message.channel.send("Control link established with A5MT Sotiyo Control")
            await message.channel.send("Checking Trello tasks")
            try:
                for msg in trello_discord_eve_int.discord_remind_manufacture_administration(client,
                                                                                            message,
                                                                                            trello_discord_eve_int.status_fabrica(trello_client)):
                    await message.channel.send(msg)
            except exceptions.ResourceUnavailable:
                await message.channel.send('ERROR! \nhttps://i.imgur.com/a1V5gYj.jpg ')
        # if message.content == '!status_fabrica jobs':
        #     wp = eve_ESI.req_esi("corporations/{}/industry/jobs/".format(corp_id) +
        #                          "?datasource=tranquility&include_completed=false&page=1&language=en-us&token=" +
        #                          authpython.get_accesstoken())
        #     await message.channel.send(get_jobs(wp))
        if message.content == '!status_fabrica freight':
            if get_delivery_jobs():
                await message.channel.send("Oi, get that stuff shipped, @Freightering!")
            else:
                pass
        if message.content == '!card_cleanup':
            pass


            # except Exception:
                # await message.channel.send("Beep boop, sorry you just fucked up")
                # sleep(0.5)
                # await message.channel.send("https://i.imgur.com/5IJXLW9.gif")

    client.run(TOKEN)
