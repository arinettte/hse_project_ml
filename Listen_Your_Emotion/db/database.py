import sqlite3
from db.models import Profile, Rating, Review, Feedback

from datetime import date
from typing import Optional, List

from settings import DB_FILE


class Database:
    def __init__(self, file=DB_FILE) -> None:
        self.connection = sqlite3.connect(file)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            birthday DATE,
            fav_artist TEXT,
            fav_song TEXT,
            fav_genre TEXT,
            gender INTEGER
        )
        """)
        self.connection.commit()

        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    user_id INTEGER,
                    general INTEGER,
                    service INTEGER,
                    interface INTEGER,
                    FOREIGN KEY (user_id) REFERENCES Profile (id)
                )
                """)

        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    user_id INTEGER,
                    text TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Profile (id)
                )
                """)

        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Feedbacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    user_id INTEGER,
                    text TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES Profile (id)
                )
                """)

        self.connection.commit()

    def is_username_taken(self, username: str) -> bool:
        self.cursor.execute("SELECT COUNT(*) as count FROM Profile WHERE username=?", (username,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def get_profile(self, id: int) -> Profile:
        self.cursor.execute("SELECT * FROM Profile WHERE id=?", (id,))
        row = self.cursor.fetchone()
        if row:
            profile = Profile(**dict(row))
            return profile

    def get_profile_by_username(self, username: str) -> Optional[Profile]:
        self.cursor.execute("SELECT * FROM Profile WHERE username=?", (username,))
        row = self.cursor.fetchone()
        if row:
            return Profile(**dict(row))

    def add_profile(self, profile: Profile):
        self.cursor.execute("""
        INSERT INTO Profile (username, password, first_name, last_name, birthday, fav_artist, fav_song, fav_genre, gender)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.username,
            profile.password,
            profile.first_name,
            profile.last_name,
            profile.birthday,
            profile.fav_artist,
            profile.fav_song,
            profile.fav_genre,
            profile.gender
        ))
        self.connection.commit()

    def edit_profile(self, id: int, profile: Profile):
        self.cursor.execute("""
        UPDATE Profile
        SET username=?, password=?, first_name=?, last_name=?, birthday=?, fav_artist=?, fav_song=?, fav_genre=?, gender=?
        WHERE id=?
        """, (profile.username, profile.password, profile.first_name, profile.last_name, profile.birthday,
              profile.fav_artist, profile.fav_song, profile.fav_genre, profile.gender, id))
        self.connection.commit()

    def insert_rating(self, rating: Rating):
        self.cursor.execute("""
            INSERT INTO Ratings (user_id, general, service, interface)
            VALUES (?, ?, ?, ?)
        """, (rating.user_id, rating.general, rating.service, rating.interface))

        self.connection.commit()
        return self.cursor.lastrowid

    #for tests
    def get_all_ratings(self) -> List[Rating]:
        self.cursor.execute("SELECT * FROM Ratings")
        rows = self.cursor.fetchall()
        return [Rating(**dict(row)) for row in rows]

    def insert_review(self, review: Review):
        self.cursor.execute("""
            INSERT INTO Reviews (user_id, text)
            VALUES (?, ?)
        """, (review.user_id, review.text))

        self.connection.commit()
        return self.cursor.lastrowid

    #for tests
    def get_all_reviews(self) -> List[Review]:
        self.cursor.execute("SELECT * FROM Reviews")
        rows = self.cursor.fetchall()
        return [Review(**dict(row)) for row in rows]

    def insert_feedback(self, feedback: Feedback):
        self.cursor.execute("""
            INSERT INTO Feedbacks (user_id, text)
            VALUES (?, ?)
        """, (feedback.user_id, feedback.text))

        self.connection.commit()
        return self.cursor.lastrowid

    #for tests
    def get_all_feedback(self) -> List[Feedback]:
        self.cursor.execute("SELECT * FROM Feedbacks")
        rows = self.cursor.fetchall()
        return [Feedback(**dict(row)) for row in rows]

    def close(self):
        self.connection.close()


database = Database()
