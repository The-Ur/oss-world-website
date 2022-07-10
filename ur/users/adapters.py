#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from typing import Any

import requests
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount import app_settings as allauth_app_settings
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.github import views as github_views
from django.conf import settings
from django.http import HttpRequest
from github import Github

from ur.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return False


# We need to grab the OAuth token from the GitHub provider
class GitHubOAuth2Adapter(github_views.GitHubOAuth2Adapter):
    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"token {token.token}"}
        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()
        if allauth_app_settings.QUERY_EMAIL and not extra_data.get("email"):
            extra_data["email"] = self.get_email(headers)
        extra_data["token"] = token.token
        return self.get_provider().sociallogin_from_response(request, extra_data)


github_views.GitHubOAuth2Adapter = GitHubOAuth2Adapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(self, request, sociallogin, data):
        data = data | sociallogin.account.extra_data
        access_token = data.pop("token", None)
        client = Github(access_token)
        setattr(sociallogin, "github_client", client)

        user = super().populate_user(request, sociallogin, data)
        user.id = data["id"]
        try:
            # Username already exists, so the other user must've changed usernames
            dup_user = User.objects.only("id", "username").get(
                username=data["username"]
            )
            real_username = client.get_user_by_id(dup_user.id).login
            if real_username != dup_user.username and user.id != dup_user.id:
                dup_user.username = real_username
                dup_user.save(update_fields=["username"])
        except User.DoesNotExist:
            pass
        user.name = data["name"] or ""
        extra = user.extra
        if not extra:
            extra = {}
        # clean data
        extra["github_profile"] = {
            k: v for k, v in data.items() if not k.endswith("url")
        }
        user.extra = extra
        return user
