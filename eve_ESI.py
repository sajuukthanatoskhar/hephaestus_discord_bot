import urllib.request
import json

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
def get_typeid(name):
    with open("eve_inv_types.etf", mode="r", encoding="utf-8") as sourcefile:
        for line in sourcefile:
            parts_k = line.split()
            type_id = parts_k[0]
            itemname_k = ' '.join(parts_k[1:])
            if str(name) == str(itemname_k):
                return type_id

