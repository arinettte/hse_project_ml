from pydantic import BaseModel
from datetime import date

from typing import Optional


class Profile(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthday: Optional[date] = None
    fav_artist: Optional[str] = None
    fav_song: Optional[str] = None
    fav_genre: Optional[str] = None
    gender: Optional[int] = None


class Rating(BaseModel):
    id: Optional[int] = None
    user_id: int
    general: int
    service: int
    interface: int


class Review(BaseModel):
    id: Optional[int] = None
    user_id: int
    text: str


class Feedback(BaseModel):
    id: Optional[int] = None
    user_id: int
    text: str
