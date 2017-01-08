import requests
import re
import json
def get_film_id(title):
    r = requests.get("http://www.imdb.com/find?s=all&q=" + title)
    m = re.search("/title/([^/]*)/", r.text)
    if m:
        return m.group(1)

def get_film_id_new(title):
    title = title.lower()
    title = title.replace(" ", "_")
    print "http://v2.sg.media-imdb.com/suggests/" + title[0] + "/" + title[0:20] + ".json"
    r = requests.get("http://v2.sg.media-imdb.com/suggests/" + title[0] + "/" + title[0:20] + ".json")
    print json.loads(r.text.split("(", 1)[1][:-1])["d"][0]["id"]
def get_film_list():
    r = requests.get("http://x.newshebdo.ugc.fr/ats/msg.aspx?sg1=afd7c7ac43982abdda8598b07d5600b5")
    m = re.findall("/af/([^\.]*)\.JPG", r.text)
    print m
print get_film_id_new("QUELQU")
 