import pytest
import datetime

from unittest.mock import MagicMock, patch
from db.database import Database
from db.models import Profile, Rating, Review, Feedback

#one-time creating db
@pytest.fixture
def db():
    db_instance = Database(":memory:")  # Use in-memory database for testing
    yield db_instance
    db_instance.close()

def test_table_creation(db):
    # Query the SQLite master table to check for table existence
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Profile'")
    profile_table = db.cursor.fetchone()
    
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Ratings'")
    ratings_table = db.cursor.fetchone()
    
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Reviews'")
    reviews_table = db.cursor.fetchone()
    
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Feedbacks'")
    feedbacks_table = db.cursor.fetchone()
    
    assert profile_table is not None
    assert ratings_table is not None
    assert reviews_table is not None
    assert feedbacks_table is not None

def test_add_profile_minimal(db):
    profile = Profile(
        username='testuser',
        password='123'
    )

    db.add_profile(profile)

    profile1 = db.get_profile(1)
    profile2 = db.get_profile_by_username('testuser')

    assert profile1 == profile2

    assert profile1.username == 'testuser'
    assert profile1.password == '123'

# for addings
def test_add_profile_full(db):
    profile = Profile(
        username='testuser',
        password='123',
        first_name='Test',
        last_name='Test',
        birthday=datetime.date(2000, 10, 5),
        fav_artist='Artist',
        fav_song='Song',
        fav_genre='Genre',
        gender=1
    )
    db.add_profile(profile)

    profile1 = db.get_profile(1)
    profile2 = db.get_profile_by_username('testuser')

    assert profile1 == profile2

    assert profile1.username == 'testuser'
    assert profile1.password == '123'
    assert profile1.first_name == 'Test'
    assert profile1.last_name == 'Test'
    assert profile1.birthday == datetime.date(2000, 10, 5)
    assert profile1.fav_artist == 'Artist'
    assert profile1.fav_song == 'Song'
    assert profile1.fav_genre == 'Genre'
    assert profile1.gender == 1


# for editing 
def test_edit_profile(db):
    profile = Profile(
        username='testuser',
        password='123',
        first_name='Test',
        last_name='Test',
        birthday=datetime.date(2000, 10, 5),
        fav_artist='Artist',
        fav_song='Song',
        fav_genre='Genre',
        gender=1
    )
    db.add_profile(profile)

    updated_profile = Profile(
        username='updateduser',
        password='456',
        first_name='Updated',
        last_name='User',
        birthday=datetime.date(1990, 1, 1),
        fav_artist='New Artist',
        fav_song='New Song',
        fav_genre='New Genre',
        gender=2
    )
    db.edit_profile(1, updated_profile)

    profile1 = db.get_profile(1)
    profile2 = db.get_profile_by_username('updateduser')

    assert profile1 == profile2

    assert profile1.username == 'updateduser'
    assert profile1.password == '456'
    assert profile1.first_name == 'Updated'
    assert profile1.last_name == 'User'
    assert profile1.birthday == datetime.date(1990, 1, 1)
    assert profile1.fav_artist == 'New Artist'
    assert profile1.fav_song == 'New Song'
    assert profile1.fav_genre == 'New Genre'
    assert profile1.gender == 2
    
# functions about rating, review and feedback
def test_insert_rating(db):
    profile = Profile(
        username='testuser',
        password='123'
    )
    db.add_profile(profile)

    rating = Rating(
        user_id=1,
        general=5,
        service=4,
        interface=3
    )
    rating_id = db.insert_rating(rating)

    ratings = db.get_all_ratings()
    assert len(ratings) == 1
    assert ratings[0].id == rating_id
    assert ratings[0].user_id == 1
    assert ratings[0].general == 5
    assert ratings[0].service == 4
    assert ratings[0].interface == 3

def test_insert_review(db):
    profile = Profile(
        username='testuser',
        password='123'
    )
    db.add_profile(profile)

    review = Review(
        user_id=1,
        text='This is a review'
    )
    db.insert_review(review)

    reviews = db.get_all_reviews()
    assert len(reviews) == 1
    assert reviews[0].user_id == 1
    assert reviews[0].text == 'This is a review'

def test_insert_feedback(db):
    profile = Profile(
        username='testuser',
        password='123'
    )
    db.add_profile(profile)

    feedback = Feedback(
        user_id=1,
        text='This is feedback'
    )
    feedback_id = db.insert_feedback(feedback)

    feedbacks = db.get_all_feedback()
    assert len(feedbacks) == 1
    assert feedbacks[0].user_id == 1
    assert feedbacks[0].text == 'This is feedback'
    
# existing 
def test_is_username_taken(db):
    profile = Profile(
        username='testuser',
        password='123'
    )
    db.add_profile(profile)

    assert db.is_username_taken('testuser') is True
    assert db.is_username_taken('nonexistentuser') is False
