"""Examples from the Python Foundations lesson."""

movie_title = "The Matrix"
release_year = 1999
rating = 8.7
is_science_fiction = True

print(movie_title)
print(type(movie_title))
print(type(release_year))
print(type(rating))
print(type(is_science_fiction))

current_year = 2026
movie_age = current_year - release_year
print(movie_age)
print(release_year < 2000)
print(rating >= 8)

sequels = ["The Matrix Reloaded", "The Matrix Revolutions", "The Matrix Resurrections"]
print(sequels)
print(sequels[0])
print(sequels[:2])

matrix = {
    "name": movie_title,
    "release_year": release_year,
    "rating": rating,
    "sequels": sequels,
}

star_wars = {
    "name": "Star Wars IV",
    "release_year": 1977,
    "sequels": ["Star Wars V", "Star Wars VI"],
    "prequels": ["Star Wars I", "Star Wars II", "Star Wars III"],
}

favorite_movies = [matrix, star_wars]
print(favorite_movies)
print(favorite_movies[0]["name"])
