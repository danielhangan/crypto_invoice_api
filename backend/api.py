import os
from dotenv import load_dotenv
import requests
from typing import List
from django.shortcuts import redirect, get_object_or_404
from ninja import NinjaAPI, Schema
from crypto_invoice.models import AppUser

api = NinjaAPI()

load_dotenv()

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI = os.environ["REDIRECT_URI"]


class UserIn(Schema):
    full_name: str
    email: str
    coinbase_id: str


class UserOut(Schema):
    user_id: int
    full_name: str
    email: str
    coinbase_id: str


@api.get("/login")
def login(request, code):

    if code == "auth":
        coinbase_scope = "wallet:user:email,wallet:user:read,wallet:addresses:read"

        data = {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": coinbase_scope,
        }

        return redirect(
            f"https://www.coinbase.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={coinbase_scope}"
        )

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }

    r = requests.post("https://api.coinbase.com/oauth/token", data=data)

    user_data = requests.get(
        "https://api.coinbase.com/v2/user",
        headers={"Authorization": f"Bearer {r.json()['access_token']}"},
    ).json()

    # Check if the user already exists
    try:
        check_user = AppUser.objects.get(coinbase_id=user_data["data"]["id"])
    except:
        check_user = AppUser.objects.create(
            full_name=user_data["data"]["name"],
            email=user_data["data"]["email"],
            coinbase_id=user_data["data"]["id"],
        )
    finally:
        return {
            "status_code": r.status_code,
            "status_reason": r.reason,
            "response": r.text,
            "user_data": user_data,
            "check_user": check_user.user_id,
        }


@api.post("/users")
def create_user(request, user_data: UserIn):
    user = AppUser.objects.create(**user_data.dict())

    return {"id": user.user_id}


@api.get("/users/{user_id}", response=UserOut)
def get_user(request, user_id: int):
    return get_object_or_404(AppUser, user_id=user_id)


@api.get("/users", response=List[UserOut])
def list_users(request):
    return AppUser.objects.all()


@api.put("/users/{user_id}")
def update_user(request, user_id: int, payload: UserIn):
    user = get_object_or_404(AppUser, user_id=user_id)
    for attr, value in payload.dict().items():
        setattr(user, attr, value)
    user.save()
    return {"success": True}


@api.delete("/users/{user_id}")
def delete_user(request, user_id: int):
    user = get_object_or_404(AppUser, user_id=user_id)
    user.delete()
    return {"success": True}
