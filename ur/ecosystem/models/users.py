#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from typing import TYPE_CHECKING, Optional, Type, TypedDict

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from ur.utils.github.webhook import github_webhook


if TYPE_CHECKING:
    from ur.users.models import User as UserModel


User: Type["UserModel"] = get_user_model()


@github_webhook("organization")
def member_added(data: dict):
    """
    Adds an existing user to the ecosystem
    """
    if data["action"] not in ["member_added", "member_removed"]:
        return

    user = data["membership"]["user"]["id"]
    ecosystem = data["organization"]["id"]
    filter_kwargs = {"user_id": user, "ecosystem_id": ecosystem}

    match data["action"]:
        # It's ok that a user joins an ecosystem, so the record already exists
        # This is to catch anyone new who joins the organization that was invited
        # rather than joining through the website
        case "member_added":
            if not EcosystemUser.objects.filter(**filter_kwargs).exists():
                EcosystemUser.objects.create(
                    **filter_kwargs,
                    node_id=data["membership"]["user"]["node_id"],
                    role=EcosystemUser.get_role(data["membership"]["role"]),
                    extra={
                        "name": data["membership"]["user"]["name"],
                        "login": data["membership"]["user"]["login"],
                    },
                )
        case "member_removed":
            EcosystemUser.objects.filter(**filter_kwargs).delete()


# Actual permission handling is done via GitHub such as setting of teams.
# The defaults of this is to have organization owners be owners,
# users in the ecosystem have "write" permission, and leads have "maintainer"
# permission, but not admin since that can be overarching.
# These are the defaults and the owner can change them


class EcosystemUserExtra(TypedDict, total=False):
    """
    Extra data for the EcosystemUser model
    """

    # Data that isn't available since user isn't signed up
    name: str
    login: str


class EcosystemUser(models.Model):
    """
    The purpose of this model is to keep track of which ecosystems a user
    is a part of. This is good for users who might want to keep track of which
    ecosystems they're a part of so that they can leave or just to view statistics.

    Not all users have an actual User model record.
    """

    class GithubOrganizationRole(models.IntegerChoices):
        """
        The roles that a user has in a GitHub organization.
        """

        ADMIN = 0
        MODERATOR = 1
        MEMBER = 2
        BILLING_MANAGER = 3
        SECURITY_MANAGERS = 4

    id = models.BigAutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField(_("Github User ID"))
    node_id = models.CharField(_("Github User Node ID"), max_length=30)
    ecosystem = models.ForeignKey("ecosystem.Ecosystem", on_delete=models.CASCADE)
    # Since we're the owners, we're also the only people who can change who
    # is an owner of the ecosystem. Even though the webhook doesn't catch role changes,
    # we're the only ones who can make those changes to begin with.
    role = models.PositiveSmallIntegerField(
        _("Github Organization Role"), choices=GithubOrganizationRole.choices
    )

    extra: dict = models.JSONField(_("Extra Data"), default=dict, blank=True)

    def get_user(self) -> Optional["UserModel"]:
        """
        Returns the user object for this ecosystem user
        """
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None

    @classmethod
    def get_role(cls, role: str) -> GithubOrganizationRole:
        """
        Get the role from a string
        """
        try:
            return cls.GithubOrganizationRole[role.upper()]
        except KeyError:
            return cls.GithubOrganizationRole.MEMBER
