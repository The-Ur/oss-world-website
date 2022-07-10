#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from typing import Optional

from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.signals import social_account_added, social_account_updated
from github import Github


# from github.Installation import Installation
#
# from ur.ecosystem.models import Ecosystem, EcosystemUser
# from ur.utils.github.client import app_client


def discover_ecosystems(sociallogin: SocialLogin, **_kwargs):
    """
    TODO Finds ecosystems to add to user-ecosystem M2M
    """
    client: Github | None = getattr(sociallogin, "github_client", None)
    if not client:
        return

    # for x in app_client.get_installations():
    #     x: Installation
    #     github_client = Github(app_client.get_access_token(x.id))
    #     github_client.get_organization(x)
    # for x in Ecosystem.objects.values_list("installation_id"):
    #     installations = app_client.get_installations()
    #     installations
    #
    # ecosystem_user = EcosystemUser.objects.get_or_create(user=sociallogin.user)[0]
    # ecosystem_user.ecosystems.add(sociallogin.account.provider)
    # ecosystem_user.save()


social_account_added.connect(discover_ecosystems)
social_account_updated.connect(discover_ecosystems)
