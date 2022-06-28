#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EcosystemConfig(AppConfig):
    name = "ur.ecosystem"
    verbose_name = _("Ecosystem")

    def ready(self):
        try:
            import ur.ecosystem.signals  # noqa F401
        except ImportError:
            pass
