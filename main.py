def load_films():
    file = open("seeds.rb", "r")
    films = []
    for line in file:
        if line[0:4] == "Film":
            film = {}
            movie_array = ("  " + line[12:-2]).split('",')
            for feature in movie_array:
                name, value = feature.split(":", 1)
                film[name[2:]] = value[2:]
            if film["Actors"] != "N/A":
                films.append(film)
    return films

def extract_vector_features(films):
    directors = {}
    directors_count = 0
    actors = {}
    actors_count = 0
    genres = {}
    genres_count = 0
    writers = {}
    writers_count = 0
    rateds = {}
    rateds_count = 0
    for film in films:
        for director in film["Director"].split(", "):
            if director not in directors:
                directors[director] = directors_count
                directors_count += 1
        for actor in film["Actors"].split(", "):
            if actor not in actors:
                actors[actor] = actors_count
                actors_count += 1
        for genre in film["Genre"].split(", "):
            if genre not in genres:
                genres[genre] = genres_count
                genres_count += 1
        for writer in film["Writer"].split(", "):
            writer = writer.split(" (", 1)[0]
            if writer not in writers:
                writers[writer] = writers_count
                writers_count += 1
        for rated in film["Rated"].split(", "):
            if rated not in rateds:
                rateds[rated] = rateds_count
                rateds_count += 1
    return films, directors, actors, genres, writers, rateds

def compute(films, directors, actors, genres, writers, rateds, liked, number_of_films_to_check):
    #print sorted(films, key=lambda f: f["ImdbRating"], reverse=True)[0]
    vectors = []
    for film in films:
        vector = [0]*(len(directors) + len(actors) + len(genres) + len(writers) + len(rateds))
        start = 0
        for director in film["Director"].split(", "):
            vector[start + directors[director]] = 1.5
        start += len(directors)
        for actor in film["Actors"].split(", "):
            vector[start + actors[actor]] = 1.2
        start += len(actors)
        for writer in film["Writer"].split(", "):
            writer = writer.split(" (", 1)[0]
            vector[start + writers[writer]] = 1.5
        start += len(writers)
        for genre in film["Genre"].split(", "):
            vector[start + genres[genre]] = 1
        start += len(genres)
        for rated in film["Rated"].split(", "):
            vector[start + rateds[rated]] = 0.7
        vectors.append(vector)
    # print vectors[0:10]
    import numpy
    from sklearn.neighbors import KNeighborsClassifier
    X = numpy.array(vectors[:-number_of_films_to_check])
    y = numpy.array(liked[:-number_of_films_to_check])
    print "number of neighbors", 0.1*len(vectors[:-number_of_films_to_check])
    nbrs = KNeighborsClassifier(n_neighbors=0.1*len(vectors[:-number_of_films_to_check]), weights="distance", algorithm='auto').fit(X, y)
    print nbrs.predict(numpy.array(vectors[-number_of_films_to_check:]))

    #exit()
    X = numpy.array(vectors)
    from sklearn.neighbors import NearestNeighbors
    nbrs1 = NearestNeighbors(n_neighbors=0.1*len(vectors[:-number_of_films_to_check]), algorithm='auto').fit(X)
    distances, indices = nbrs1.kneighbors(numpy.array(vectors[-number_of_films_to_check:]))
    print distances
    print indices
    k = 0
    for i in indices[0]:
        if films[i]["Actors"] != "N/A":
            print i, distances[0][k], liked[i]
            print "Title", films[i]["Title"]
            print "Director", films[i]["Director"]
            print "Writer", films[i]["Writer"]
            print "Actors", films[i]["Actors"]
            print "Genre", films[i]["Genre"]
            print "Rated", films[i]["Rated"]
            print
        
        k = k + 1
        
    return nbrs.predict_proba(numpy.array(vectors[-number_of_films_to_check:])).tolist()