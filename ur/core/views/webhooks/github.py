#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ur.utils.github.webhook import WEBHOOK_REGISTRATION


class GitHubWebhookView(APIView):
    http_method_names = ("post",)
    throttle_classes = ()
    permission_classes = ()

    def post(self, request: Request, *args, **kwargs):
        if request.META["HTTP_X_HUB_SIGNATURE_256"] != settings.GITHUB_WEBHOOK_SECRET:
            raise PermissionDenied()
        for fn in WEBHOOK_REGISTRATION.get(request.META["HTTP_X_GITHUB_EVENT"], []):
            fn(request.data)
        return Response()
