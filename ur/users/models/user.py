#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, JSONField, PositiveBigIntegerField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for OSS.
    """

    id = PositiveBigIntegerField(primary_key=True, verbose_name=_("GitHub ID"))

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    extra: dict = JSONField(default=dict, blank=True)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def get_name(self):
        """Get name of user.

        Returns:
            str: Name of user.

        """
        return self.name or self.username
