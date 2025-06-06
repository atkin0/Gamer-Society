import time
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Query
from pydantic import BaseModel, Field, constr
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)

class UserCreateResponse(BaseModel):
    user_id: int

class CreateUser(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., description="Username must be between 3 and 50 characters")
    private: bool 


# False = Public Account
# True = Private Account
class Setting(BaseModel):
    name: str
    privacy_value: bool

class Reviews(BaseModel):
    user_id: int
    game_id: int
    score: int
    text: str



@router.post("/create", response_model=UserCreateResponse)
def create_user(new_user: CreateUser):
    """
    Creates a new User
    """
    start = time.time()
    print(f"NEW USER: {new_user}")
    with db.engine.begin() as connection:
        #Inserts new user info into the username table
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username, account_is_private)
                VALUES (:username, :privacy)
                RETURNING id
                """
            ),
            {"username": new_user.username, "privacy": new_user.private},
        ).scalar_one()

    end = time.time()
    print(end - start)
    return UserCreateResponse(user_id=result)

@router.post("/{user_id}/add",  status_code=status.HTTP_204_NO_CONTENT)
def add_friends(user_id: int, friend_id: int):
    """
    Add a user as a friend.
    """
    start = time.time()
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": friend_id}).first():
            raise HTTPException(status_code=404, detail="Friend doesn't exist")

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO friends (user_adding_id, user_added_id)
                VALUES (:user_adding_id, :user_added_id)
                """
            ),
            {"user_adding_id": user_id, "user_added_id": friend_id}
        )
    end = time.time()
    print(end - start)
        


@router.get("/{user_id}/my_friends", response_model= List[str])
def display_my_friended(user_id: int):
    """
    Display a users list of friends.
    """
    start = time.time()
    friends_list = []
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT users.username
                FROM friends
                JOIN users on friends.user_added_id = users.id
                WHERE friends.user_adding_id = :user_id;
                """
            ),
            {"user_id": user_id}
        )

        for r in results:
            friends_list.append(r.username)

    end = time.time()
    print(end - start)
    return friends_list

@router.get("/{user_id}/friended_me", response_model= List[str])
def display_friended_me(user_id: int):
    """
    Display a users list of friends.
    """
    start = time.time()
    friends_list = []
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT users.username
                FROM friends
                JOIN users on friends.user_adding_id = users.id
                WHERE friends.user_added_id = :user_id;
                """
            ),
            {"user_id": user_id}
        )

        for r in results:
            friends_list.append(r.username)

    end = time.time()
    print(end - start)
    return friends_list

@router.get("/{user_id}/settings", response_model= list[Setting])
def show_settings(user_id: int):
    """
    Display a users settings.
    """
    start = time.time()
    setting_list = []
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT username, account_is_private
                FROM users
                WHERE id = :id
                """
            ),
            {"id": user_id}
        ).fetchall()
        
        for row in results:
            setting_list.append(
                Setting(
                    name=row.username,
                    privacy_value=row.account_is_private
                )
            )
    end = time.time()
    print(end - start)
    return setting_list

@router.patch("/{user_id}/settings/edit", status_code=status.HTTP_204_NO_CONTENT)
def edit_settings(user_id: int, setting: Setting):
    """
    Edit a users settings.
    """ 

    #setting.value should be passed in as true or false

    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")
        connection.execute(
            sqlalchemy.text(
                    """
                    UPDATE users
                    SET account_is_private = :privacy_value, username = :username
                    WHERE id = :id
                    """
            ),
            {"privacy_value": setting.privacy_value, "username": setting.name, "id": user_id}
        )
        
@router.get("/{user_id}/history", response_model=list[Reviews])
def show_history(
    user_id: int, 
    limit: int = Query(10, description="Maximum number of history items to return")
):
    """
    Display a users history.
    """
    start = time.time()
    reviews_list = []
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM reviews
                WHERE user_id = :user_id
                ORDER BY updated_at DESC
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "limit": limit}
        )
        for review in result:
            reviews_list.append(
                Reviews(
                    user_id= user_id,
                    game_id=review.game_id, 
                    score = review.score, 
                    text=review.text
                )
            )
    end = time.time()
    print(end - start)
    return reviews_list


@router.get("/{user_id}/favorite", response_model= list[Reviews])
def show_top(user_id: int):
    """
    Display a users history.
    """
    start = time.time()
    reviews_list = []
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM reviews
                WHERE user_id = :user_id
                ORDER BY score DESC
                LIMIT 5
                """
            ),
            {"user_id": user_id}
        ).fetchall()

    for review in result:
        reviews_list.append(
            Reviews(
                user_id= user_id,
                game_id=review.game_id,
                score = review.score,
                text=review.text
            )
        )
    end = time.time()
    print(end - start)
    return reviews_list

# @router.post("/{user_id}/games_played",  status_code=status.HTTP_204_NO_CONTENT)
# def add_game_played(user_id: int, time_played: int, game_id: int):
#     """
#     Add a game into a user's played history
#     """
#     start = time.time()
#     with db.engine.begin() as connection:
#         if not connection.execute(
#                 sqlalchemy.text("SELECT 1 FROM users where id = :id"),
#                 {"id": user_id}).first():
#             raise HTTPException(status_code=404, detail="User doesn't exist")
#
#         connection.execute(
#             sqlalchemy.text(
#                 """
#                 INSERT INTO history (user_id, game_id, time_played)
#                 VALUES (:user_id, :game_id, :time_played)
#                 ON CONFLICT (user_id, game_id)
#                 DO UPDATE SET
#                 time_played = history.time_played + EXCLUDED.time_played;
#                 """
#             ),
#             {"user_id": user_id, "game_id": game_id, "time_played": time_played}
#         )
#     end = time.time()
#     print(end - start)
#     pass
