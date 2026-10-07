"""Completed Movie class from the Complex Python lesson."""

from datetime import date


class Movie:
    """Store and manipulate data about a movie."""

    def __init__(self, name, release_year=None):
        self.movie_name = name
        self.directors = []
        self.release_year = release_year
        self.age = 0
        self.sequels = []
        self.prequels = []

    def add_directors(self, directors):
        """Add one director or a list of directors."""

        if isinstance(directors, list) is False:
            directors = [directors]
        self.directors.extend(directors)

    def add_release_year(self, year):
        """Store the movie's release year as an integer."""

        self.release_year = int(year)

    def calculate_movie_age(self):
        """Calculate the movie's age from its release year."""

        self.age = date.today().year - self.release_year

    def add_sequel(self, sequel, release_year):
        """Create a Movie instance and add it as a sequel."""

        self.sequels.append(Movie(sequel, release_year))

    def add_prequel(self, prequel, release_year):
        """Create a Movie instance and add it as a prequel."""

        self.prequels.append(Movie(prequel, release_year))

    def get_movie_info(self):
        """Print the movie's attributes."""

        for key, value in self.__dict__.items():
            if key in ["sequels", "prequels"]:
                print(f"{key}: {[movie.movie_name for movie in value]}")
            else:
                print(f"{key}: {value}")

    def calculate_movie_order(self):
        """Return the related movie names ordered by release year."""

        all_movies = [self] + self.sequels + self.prequels
        all_movies.sort(key=lambda movie: movie.release_year)
        return [movie.movie_name for movie in all_movies]

    def save_movie_info(self, file_name):
        """Save the movie's information to a text file."""

        with open(file_name, "w", encoding="utf-8") as file:
            file.write(f"Movie Name: {self.movie_name}\n")
            file.write(f"Directors: {', '.join(self.directors)}\n")
            file.write(f"Release Year: {self.release_year}\n")
            file.write(f"Age: {self.age}\n")
            file.write(
                f"Sequels: {', '.join([movie.movie_name for movie in self.sequels])}\n"
            )
            file.write(
                f"Prequels: {', '.join([movie.movie_name for movie in self.prequels])}\n"
            )


a_movie = Movie("The Matrix I")
a_movie.add_directors(["Lana Wachowski", "Lilly Wachowski"])
a_movie.add_release_year(1999)
a_movie.add_sequel("The Matrix II", 2003)
a_movie.add_sequel("The Matrix III", 2003)
a_movie.add_sequel("The Matrix IV", 2021)
a_movie.add_prequel("The Matrix 0", 1998)
a_movie.calculate_movie_age()
a_movie.get_movie_info()
print(a_movie.calculate_movie_order())
a_movie.save_movie_info("movie_info.txt")
