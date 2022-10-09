import sys

from arcgis.gis import GIS
from configparser import ConfigParser
from arcgis.features import FeatureLayer
from arcgis.features import FeatureLayerCollection
from IPython.display import display

sys.dont_write_bytecode = True

# Lettura file di config

cfg = ConfigParser()
cfg.read('./CONFIG.ini')
url_gis = cfg.get('PORTAL','INDIRIZZO_PORTAL')
#print(url_gis)

user = cfg.get('PORTAL', 'UTENTE')
#print(user)

pwd = cfg.get('PORTAL', 'PASSWORD')
#print(pwd)

try:
     print('Connessione al portal ....')
     gis = GIS(url_gis, user, pwd)
except Exception:
     print('Errore di connessione al portal ....')
     e = sys.exc_info()[1]
     print(e.args[0])
     exit(0)

# url_id = gis.content.get('73e971dfad68481fa370a20b993d7b73')
# print(url_id)
#
# dict_items = url_id.items()
#
# for k, v in dict_items:
#      print(k, ' : ', v)

#search_results = gis.content.search('a8195280674244f3827fad97ae6fb2ac')
search_results = gis.content.search('title: Cavità artificiali v3.1C owner:mroma', item_type='Feature Layer')

if len(search_results) > 0:
     print("Oggetto trovato ...")
     cavita_item = search_results[0]
     #print(cavita_item)

     # print("list items ...")
     # dict_items = cavita_item.items()
     # for k, v in dict_items:
     #      print(k, ' : ', v)

     #get layers
     print("list layers ...")
     cavita_layers = cavita_item.layers
     for lyr in cavita_layers:
          print(lyr.properties.name)

     cavita = cavita_item.layers[0]

     # list attach per oid
     # print("list attach ...")
     # attach = cavita.attachments.get_list(oid=10)
     # print(attach)

     #list fields
     # print("list fields ..."
     # print(cavita.properties.extent)
     # for f in cavita.properties.fields:
     #      print(f['name'])

     #query
     query_result1 = cavita.query(where='comune = \'Arzano\'',out_fields='codice_identificativo_della_cav')
     print("Trovate " + str(len(query_result1.features)) + " cavità")
     if len(query_result1.features) >0:
          for f in query_result1.features:
               print(f)

          feature = cavita[0]
          print(feature)
     else:
          print("Non trovo nulla ...")
else:
     print("Oggetto non trovato ...")




