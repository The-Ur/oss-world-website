#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.db import models
from django.utils.translation import gettext_lazy as _

from ur.utils.github.webhook import github_webhook


@github_webhook("repository")
def _repository_management(data: dict):
    match data["action"]:
        case "renamed":
            _original_name = data["changes"]["repository"]["name"]["from"]
            Repository.objects.filter(id=data["organization"]["id"]).update(
                name=data["repository"]["name"]
            )


@github_webhook("installation_repositories")
def add_remove_repositories(data: dict):
    match data["action"]:
        case "removed":
            Repository.objects.filter(
                id__in=[x["id"] for x in data["repositories_removed"]]
            ).delete()
        case "added":
            ecosystem_id = data["installation"]["account"]["id"]
            Repository.objects.bulk_create(
                [
                    Repository(
                        id=x["id"],
                        node_id=x["node_id"],
                        name=x["name"],
                        ecosystem_id=ecosystem_id,
                    )
                    for x in data["repositories_added"]
                ],
                ignore_conflicts=True,
            )


class Repository(models.Model):
    id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name=_("Repository ID from GitHub")
    )
    node_id = models.CharField(max_length=30, verbose_name=_("Repository node ID"))
    ecosystem = models.ForeignKey("ecosystem.Ecosystem", on_delete=models.CASCADE)
    name = models.SlugField(
        max_length=255,
        verbose_name=_("Repository slug"),
        help_text=_("Repository name without organization name"),
    )
    is_package = models.BooleanField(default=False)
