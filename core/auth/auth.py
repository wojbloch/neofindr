from typing import Type, Union, Dict, Any, Optional
from django.db import transaction
import requests
import os
from rest_framework.exceptions import ParseError, ValidationError
from core.models import User, InternalUser


env = os.environ.get


# TODO: add code verifier for the challenge later on, when I deal with frontend

class GoogleAuth:
    @staticmethod
    def get_bearer(code: str) -> Optional[str]:
        try:
            token_response = requests.post('https://oauth2.googleapis.com/token', data={
                        'code': code,
                        'client_id': env('GOOGLE_AUTH_CLID'),
                        'client_secret': env('GOOGLE_AUTH_SECRET'),
                        'redirect_uri': env('GOOGLE_CALLBACK_URI'),
                        'grant_type': 'authorization_code'
                    })
            access_token = token_response.json().get("access_token")
        except Exception as e:
            raise ParseError(detail=str(e))
        return access_token

    @staticmethod
    def get_user_info(access_token: str) -> Dict[str, Any]:
        try:
            user_info = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            ).json()
        except Exception as e:
            raise ParseError(detail=str(e))
        return user_info


class GitHubAuth:
    @staticmethod
    def get_bearer(code: str) -> Optional[str]:
        try:
            headers = {
                'Accept': 'application/json'
            }
            token_response = requests.post('https://github.com/login/oauth/access_token', data={
                'code': code,
                'client_id': env('GITHUB_AUTH_CLID'),
                'client_secret': env('GITHUB_AUTH_SECRET'),
                'redirect_uri': env('GITHUB_CALLBACK_URI'),
                'grant_type': 'authorization_code'
                },
                headers=headers
            )
            access_token = token_response.json().get("access_token")
        except Exception as e:
            raise ParseError(detail=str(e))
        return access_token

    @staticmethod
    def get_user_info(access_token: str) -> Dict[str, Any]:
        try:
            headers = {
               'Authorization': f'token {access_token}',
               'Accept': 'application/json'
            }
            user_response = requests.get(
                'https://api.github.com/user',
                headers=headers
            )
            user_response.raise_for_status()
            user_info = user_response.json()
            user_info['email'] = GitHubAuth.get_user_email(access_token)
        except Exception as e:
            raise ParseError(detail=str(e))
        return user_info

    @staticmethod
    def get_user_email(access_token: str) -> Optional[str]:
        try:
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/json'
            }
            email_response = requests.get(
                'https://api.github.com/user/emails',
                headers=headers
            )
        except Exception as e:
            raise ParseError(detail=str(e))
        if email_response.status_code != 200:
            print(f"error: {email_response.status_code} - {email_response.text}")
            return None
        emails = email_response.json()
        for email in emails:
            if email.get('primary') and email.get('verified'):
                return email.get('email')
        for email in emails:
            if email.get('verified'):
                return email.get('email')
        if emails:
            return emails[0].get('email')
        return None

# TODO: LATER, BELOW IS NOT IMPLEMENTED YET

class FacebookAuth:
    @staticmethod
    def get_bearer(code: str) -> Optional[str]:
        try:
            token_response = requests.post('https://graph.facebook.com/oauth/access_token', data={
                'code': code,
                'client_id': env('FACEBOOK_AUTH_CLID'),
                'client_secret': env('FACEBOOK_AUTH_SECRET'),
                'redirect_uri': env('FACEBOOK_CALLBACK_URI'),
                'grant_type': 'authorization_code'
            })
            access_token = token_response.json().get("access_token")
        except Exception as e:
            raise ParseError(detail=str(e))
        return access_token

    @staticmethod
    def get_user_info(access_token: str) -> Dict[str, Any]:
        ...


class LinkedInAuth:
    @staticmethod
    def get_bearer(code: str) -> Optional[str]:
        try:
            token_response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data={
                'code': code,
                'client_id': env('LINKEDIN_AUTH_CLID'),
                'client_secret': env('LINKEDIN_AUTH_SECRET'),
                'redirect_uri': env('LINKEDIN_CALLBACK_URI'),
                'grant_type': 'authorization_code'
            })
            access_token = token_response.json().get("access_token")
        except Exception as e:
            raise ParseError(detail=str(e))
        return access_token

    @staticmethod
    def get_user_info(access_token: str) -> Dict[str, Any]:
        ...


AuthProvider = Union[Type[GoogleAuth], Type[GitHubAuth], Type[FacebookAuth], Type[LinkedInAuth]]

def match_auth_provider(provider: str) -> Type[AuthProvider]:
    provider = provider.lower()
    match provider:
        case "google":
            return GoogleAuth
        case "github":
            return GitHubAuth
        case "facebook":
            return FacebookAuth
        case "linkedin":
            return LinkedInAuth
        case _:
            raise ValidationError(
                detail=f"Unsupported authentication provider: '{provider}'. Supported providers are: google, github, facebook, linkedin."
            )


# might add multiple providers -> singular internal account linking but idk, not a priority as of now

def auth_create_or_update_user(email: str, user_info: Dict[str, Any]) -> User:
    if not email:
        raise ValidationError(detail="Cannot proceed further without email address.")
    with transaction.atomic():
        user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', '')
                }
            )
        if created:
            InternalUser.objects.create(email=email, django_user=user)
    return user
