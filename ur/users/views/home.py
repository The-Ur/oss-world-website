#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.db.models import Case, When
from django.db.models.functions import Length
from django.views.generic import TemplateView

from ur.ecosystem.models import EcosystemApplication
from ur.ecosystem.models.users import EcosystemUser


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["applications"] = (
                EcosystemApplication.objects.filter(
                    user=self.request.user,
                )
                .annotate(
                    admin_reason_length=Length("admin_reason"),
                    admin_pending=Case(
                        When(admin_reason_length=0, then=True), default=False
                    ),
                )
                .only("installation_id", "organization_login", "is_approved", "extra")
            )
            context["ecosystems"] = (
                EcosystemUser.objects.select_related("ecosystem")
                .filter(
                    user_id=self.request.user.id,
                )
                .only("ecosystem_id", "ecosystem__name")
            )

        return context
