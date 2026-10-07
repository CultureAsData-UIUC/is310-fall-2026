"""Completed example from the Advanced Python refresher lesson."""

favorite_movies = [
    {
        "name": "The Matrix I",
        "release_year": 1999,
        "sequels": ["The Matrix II", "The Matrix III", "The Matrix IV"],
    },
    {
        "name": "Star Wars IV",
        "release_year": 1977,
        "sequels": ["Star Wars V", "Star Wars VI", "Star Wars VII"],
        "prequels": ["Star Wars I", "Star Wars II", "Star Wars III"],
    },
]

print(favorite_movies)
print("How many total favorite movies do we have?", len(favorite_movies))
print(type(favorite_movies), type(favorite_movies[0]))

favorite_movies[0]["long_description"] = (
    "The Matrix is a 1999 science fiction action film written and directed "
    "by the Wachowskis. It is the first installment in The Matrix film series."
)
split_description = favorite_movies[0]["long_description"].split(" ")
favorite_movies[0]["short_description"] = " ".join(split_description[:10])
edited_description = favorite_movies[0]["long_description"].replace(
    "the Wachowskis", "Lana and Lilly Wachowski"
)

print(split_description)
print("Description length:", len(split_description))
print("Short description:", favorite_movies[0]["short_description"])
print("Edited description:", edited_description)

for movie in favorite_movies:
    print(movie["name"])

individual_movie = favorite_movies[0]
for key, value in individual_movie.items():
    print(key, value)


def format_movie_name_and_year(movie):
    """Return a sentence containing a movie's name and release year."""

    movie_data = movie["name"] + " was released in " + str(movie["release_year"])
    return movie_data


for movie in favorite_movies:
    print(format_movie_name_and_year(movie))

if favorite_movies[0]["release_year"] > favorite_movies[1]["release_year"]:
    print(favorite_movies[0]["name"], "is newer")
else:
    print(favorite_movies[1]["name"], "is newer")

if "Matrix" in favorite_movies[0]["name"]:
    print("This movie belongs to the Matrix series")
else:
    print("This is another movie")

recent_favorite_movie = input("Enter your favorite movie from the last year: ")
print("Your favorite movie from the last year is:", recent_favorite_movie)
