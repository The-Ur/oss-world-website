#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest, ValidationError
from django.db.models import Case, When
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from github.Organization import Organization
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ur.ecosystem.models import (
    Ecosystem,
    EcosystemApplication,
    EcosystemUser,
    InstalledOrganization,
)
from ur.ecosystem.views.application.apply import validate_owner
from ur.utils.github.client import app_client


class EcosystemApplicationView(LoginRequiredMixin, DetailView):
    template_name = "ecosystem/application_status.html"
    object: EcosystemApplication

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        client = app_client.create_client(
            InstalledOrganization.objects.only("installation_id")
            .get(id=self.object.installation_id)
            .installation_id
        )
        data["base_permission"] = client.get_organization(
            self.object.organization_login
        ).default_repository_permission
        if self.object.is_approved:
            data["ecosystem_exists"] = Ecosystem.objects.filter(
                id=self.object.installation_id
            ).exists()

        return data

    def get_queryset(self):
        return EcosystemApplication.objects.annotate(
            admin_reason_length=Length("admin_reason"),
            admin_pending=Case(When(admin_reason_length=0, then=True), default=False),
        ).filter(user=self.request.user)


class FinalizeView(APIView):
    """Formally accepts an application for an ecosystem to join"""

    installation: InstalledOrganization
    application: EcosystemApplication
    organization: Organization

    def accept(self) -> dict:
        ecosystem, _created = Ecosystem.objects.get_or_create(
            id=self.installation.id,
            defaults={
                "installation_id": self.installation.installation_id,
                "name": self.installation.organization_login,
                "node_id": self.installation.node_id,
            },
        )
        # We need to collect all members of the organization and add them to the
        # ecosystem user management table.
        # https://docs.github.com/en/rest/orgs/members#list-organization-members
        _users = []
        for x in ["member", "admin", "billing_manager"]:
            _users.extend(
                EcosystemUser(
                    ecosystem=ecosystem,
                    user_id=user.id,
                    node_id=user.node_id,
                    role=EcosystemUser.get_role(x),
                    extra={
                        "name": user.name,
                        "login": user.login,
                        "inviter": user.inviter.id if user.inviter else None,
                    },
                )
                for user in self.organization.get_members(role=x)
            )
        EcosystemUser.objects.bulk_create(_users, ignore_conflicts=True)
        # Package registration is not handled automatically here in the case
        # there are some packages that shouldn't be registered.

        self.application.extra = self.application.extra | {"finalized": True}
        self.application.save(update_fields=["extra"])

        return {"message": _("Success")}

    def post(self, request: Request):
        try:
            organization_id = request.data["organization_id"]
            organization_slug = request.data["organization_slug"]
        except KeyError:
            return Response({"error": "Missing required fields"}, status=400)
        if Ecosystem.objects.filter(id=organization_id).exists():
            raise BadRequest("Organization already accepted")
        try:
            self.application = EcosystemApplication.objects.get(
                installation_id=organization_id
            )
        except EcosystemApplication.DoesNotExist:
            raise BadRequest("Organization not found")
        if not self.application.is_approved:
            raise BadRequest("Organization not approved")
        self.installation = InstalledOrganization.objects.get(id=organization_id)
        # The user should invite the user at any time. The Django admin should then
        # accept an invitation. We'll let the user know to make them the owner.
        try:
            self.organization = validate_owner(
                self.installation.installation_id, organization_slug
            )
        except ValidationError as e:
            raise BadRequest(e.message)

        # Now we accept them into the organization.
        return Response(self.accept())
