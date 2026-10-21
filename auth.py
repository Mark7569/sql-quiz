import os
from getpass import getpass
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).with_name(".env"))


def new_auth_client():
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_PUBLISHABLE_KEY"],
    )


def register(email, password):
    client = new_auth_client()
    return client.auth.sign_up(
        {
            "email": email,
            "password": password,
        }
    )


def login(email, password):
    client = new_auth_client()
    response = client.auth.sign_in_with_password(
        {
            "email": email,
            "password": password,
        }
    )

    if response.session is None:
        raise ValueError("Login did not return a session.")

    return response.session


def require_user(access_token):
    if not access_token:
        raise PermissionError("Please sign in first.")

    client = new_auth_client()
    response = client.auth.get_user(access_token)

    if response.user is None:
        raise PermissionError("Your session is invalid. Please sign in again.")

    return response.user


def main():
    action = input("Enter register or login: ").strip().lower()

    if action not in {"register", "login"}:
        print("Please enter register or login.")
        return

    email = input("Email: ").strip()
    password = getpass("Quiz account password: ")

    if action == "register":
        confirmation = getpass("Confirm password: ")
        if password != confirmation:
            print("Passwords do not match.")
            return

        response = register(email, password)

        if response.session:
            print("Registration successful. You can now log in.")
        else:
            print(
                "Registration request submitted. "
                "Check your email for a confirmation link, "
                "then run this script again and choose login."
            )
    else:
        session = login(email, password)
        user = require_user(session.access_token)
        print(f"Login successful! Verified user: {user.email}")


if __name__ == "__main__":
    main()
