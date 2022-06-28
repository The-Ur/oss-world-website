#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.urls import path

from ur.users.views import user_detail_view, user_redirect_view, user_update_view


app_name = "package"
urlpatterns = []
