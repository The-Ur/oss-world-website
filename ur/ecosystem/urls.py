#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.urls import path

from ur.ecosystem.views.application.apply import ApplicationView
from ur.ecosystem.views.application.finalize import (
    EcosystemApplicationView,
    FinalizeView,
)


app_name = "ecosystem"
urlpatterns = [
    path("apply/", ApplicationView.as_view(), name="apply"),
    path(
        "application-status/<int:pk>/",
        EcosystemApplicationView.as_view(),
        name="application-status",
    ),
    path("application-finalize/", FinalizeView.as_view(), name="application-finalize"),
]
