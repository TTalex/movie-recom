from flask import Flask, render_template, jsonify, request, url_for
from main import compute, load_films, extract_vector_features
import json
import requests
import re
import os


def get_film_data(imdb_id):
    r = requests.get("http://www.omdbapi.com/?i=" + imdb_id + "&plot=short&r=json")
    film = r.json()
    if film["imdbRating"] == "N/A":
        film["imdbRating"] = 0
    return film

def get_film_id(title):
    title = title.lower()
    title = title.replace(" ", "_")
    print "http://v2.sg.media-imdb.com/suggests/" + title[0] + "/" + title[0:20] + ".json"
    r = requests.get("http://v2.sg.media-imdb.com/suggests/" + title[0] + "/" + title[0:20] + ".json")
    return json.loads(r.text.split("(", 1)[1][:-1])["d"][0]["id"]

def get_film_list():
    r = requests.get("http://x.newshebdo.ugc.fr/ats/msg.aspx?sg1=afd7c7ac43982abdda8598b07d5600b5")
    m = re.findall("/af/([^\.]*)\.JPG", r.text)
    return m

app = Flask(__name__, static_url_path='/static')
films = []
directors = actors = genres = writers = rateds = {}
@app.route('/api/films')
def get_films():
    global films, directors, actors, genres, writers, rateds
    if not films:
        films, directors, actors, genres, writers, rateds = extract_vector_features(load_films())
    return jsonify(films=films)

@app.route('/save')
def save():
    return render_template("compute.html", liked=request.args.get('liked'), liked1=request.args.get('liked1') or [])

@app.route('/api/learn')
def learn():
    global films, directors, actors, genres, writers, rateds
    if not films:
        films = load_films()
    liked = json.loads(request.args.get('liked'))
    liked2 = json.loads(request.args.get('liked1'))
    films_list = get_film_list()
    films_to_add = []
    print films_list
    for k in films_list:
        films_to_add.append(get_film_data(get_film_id(k)))
    films_to_add = sorted(films_to_add, key=lambda f: f["imdbRating"], reverse=True)
    for k in films_to_add:
        liked.append(2)
        liked2.append(2)
        films.append(k)
    films, directors, actors, genres, writers, rateds = extract_vector_features(films)
    print "len(films)", len(films)
    print "len(liked)", len(liked)
    print "len(liked2)", len(liked2)
    filtered_films = [f for (i,f) in enumerate(films) if liked[i] != 0]
    filtered_liked = filter(lambda l: l != 0, liked)
    results1 = compute(filtered_films, directors, actors, genres, writers, rateds, filtered_liked, 6)
    if liked2:
        filtered_films = [f for (i,f) in enumerate(films) if liked2[i] != 0]
        filtered_liked = filter(lambda l: l != 0, liked2)
        results2 = compute(filtered_films, directors, actors, genres, writers, rateds, filtered_liked, len(films_list))
    else:
        results2 = []
    return jsonify(results1=results1, results2=results2, films=films[-len(films_list):])

    
@app.route('/')
def root():
    return render_template("root.html")
@app.route('/generator')
def generator():
    return render_template("index.html")
    
@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)

@app.route('/css')
def css():
    return app.send_static_file('main.css')
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run("0.0.0.0", port=port)