#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = "ur.core"
    verbose_name = _("Core")

    def ready(self):
        try:
            import ur.core.signals  # noqa F401
        except ImportError:
            pass
