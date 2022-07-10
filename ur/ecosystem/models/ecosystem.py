#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.db import models
from django.utils.translation import gettext_lazy as _

from ur.utils.github.webhook import github_webhook


class Ecosystem(models.Model):
    """An ecosystem is a GitHub organization"""

    id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name=_("Organization ID from GitHub")
    )
    node_id = models.CharField(max_length=30, verbose_name=_("Organization node ID"))
    # Used for getting an OAuth token for the GitHub API
    installation_id = models.PositiveBigIntegerField()
    name = models.SlugField(max_length=39, verbose_name=_("Organization login/slug"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


@github_webhook("organization")
def rename_ecosystem(data: dict):
    if data["action"] != "renamed":
        return
    _original_name = data["changes"]["organization"]["login"]["from"]
    Ecosystem.objects.filter(id=data["organization"]["id"]).update(
        name=data["organization"]["login"]
    )
