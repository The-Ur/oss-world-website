#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.urls import path

from ur.ecosystem.views.application.apply import ApplicationView


app_name = "ecosystem"
urlpatterns = [path("apply/", ApplicationView.as_view(), name="apply")]
