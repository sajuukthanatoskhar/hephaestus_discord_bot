import codecs
import urllib.request
import json

import authpython

job_types = [
    'Something 0',
    'Invention',
    'Something 2',
    'Something 3',
    'Material Efficiency',
    'Something 5',
    'Something 6',
    'Something 7',
    'Manufacturing']



def req_fuzzwork(request):
    """

    :param request: request for fuzzwork blueprint section
    :return:
    """
    wp = urllib.request.urlopen("https://www.fuzzwork.co.uk/blueprint/api/blueprint.php?typeid=%s" % (request))
    return wp

def req_esi(request_esi):
    wp = urllib.request.urlopen("https://esi.evetech.net/v1/" + request_esi)
    return wp

'''
Is reciprocal function of get_typeid
Gives the item name
Input is item input
returns item name as string
'''
def get_name(item_id_input):
    with open("eve_inv_types.etf", mode="r", encoding="utf-8") as sourcefile:
        for line in sourcefile:
            parts_k = line.split()
            item_name = ' '.join(parts_k[1:])
            item_id = parts_k[0]
            # print(str(int(name)))
            # print(str(int(itemname_k)))
            # print("%s %s %s"%(name,itemname_k,typeid_k))
            if int(item_id_input) == int(item_id):
                return item_name

"""
This gets the item_id from the *.etf listed
returns type_id as an integer value
"""
def get_typeid(name: str):
    with open("eve_inv_types.etf", mode="r", encoding="utf-8") as sourcefile:
        for line in sourcefile:
            parts_k = line.split()
            type_id = parts_k[0]
            itemname_k = ' '.join(parts_k[1:])
            if str(name) == str(itemname_k):
                return type_id

"""
Get the blueprint details from fuzzworks
Example - https://www.fuzzwork.co.uk/blueprint/api/blueprint.php?typeid=22457
Input is the name of the blueprint, you have to include the ' Blueprint' or ' Reaction Formula', note the spaces
Output is a JSON blob for the blueprint
"""


def get_blueprint_details(name):
    reader = codecs.getreader("utf-8")
    type_id_request = get_typeid(name)
    js_wp = json.load(reader(req_fuzzwork(type_id_request)))
    return js_wp

def get_assets(corp_id, page):
    "https://esi.evetech.net/latest/corporations/{}/assets/?datasource=tranquility&page={}".format(corp_id,page)





def read_tokens(file):
    """
    Reading the tokens made from the pythonserver.py functions from a file (mostly it should be 'key.key')
    Input is the file
    The file is formatted into two columns, one line
    output are the two tokens
    """
    keys_file = open(file, "r")
    access_token = refresh_token = 0
    for lines in keys_file:
        pw = lines.split(" ")  # [0] is access_token, #[1] is refresh
        access_token = pw[0]  # First column
        refresh_token = pw[1]  # Second Column
    #print(authpython.refresh('1', refresh_token))
    return access_token, refresh_token