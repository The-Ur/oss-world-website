#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_field
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpRequest

from ur.users.models import User
from ur.utils.github.client import github_client


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user_id = data["id"]
        try:
            # Username already exists, so the other user must've changed usernames
            dup_user = User.objects.only("id", "username").get(
                username=data["username"]
            )
            dup_user.username = github_client.get_user_by_id(user_id)["login"]
            dup_user.save(update_fields=["username"])
        except User.DoesNotExist:
            pass
        user_field(user, "name", data.get("name"))
        user_field(user, "id", user_id)
        return user
