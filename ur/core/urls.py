#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.urls import path

from ur.core.views.webhooks.github import GitHubWebhookView


app_name = "core"
urlpatterns = [
    path(
        "webhoooks/github/main-app/",
        view=GitHubWebhookView.as_view(),
        name="webhook-github-main-app",
    ),
]
