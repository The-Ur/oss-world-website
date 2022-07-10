#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.views.generic import ListView
from rest_framework.views import APIView

from ur.ecosystem.models import Ecosystem


class JoinAPIView(APIView):
    """View for joining a new ecosystem"""

    http_method_names = ("post",)

    def post(self, request):
        """
        Join a new ecosystem
        """
        pass


class JoinEcosystemListView(ListView):
    model = Ecosystem
    template_name = "ecosystem/join.html"
    context_object_name = "ecosystems"
    paginate_by = 50
    queryset = Ecosystem.objects.only("id", "name").all()
