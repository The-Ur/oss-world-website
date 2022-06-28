#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.db import models
from django.utils.translation import gettext_lazy as _


class Ecosystem(models.Model):
    """An ecosystem is a GitHub organization"""

    id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name=_("Organization ID from GitHub")
    )
    installation_id = models.PositiveBigIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
