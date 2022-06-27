#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from ur.users.api.views import UserViewSet


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

if settings.DEBUG or settings.IS_TEST:
    router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls
