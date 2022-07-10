#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#
from datetime import datetime

from django.conf import settings
from django.contrib import admin
from github.GithubException import GithubException

from ur.ecosystem.models import (
    EcosystemApplication,
    EcosystemUser,
    InstalledOrganization,
)
from ur.ecosystem.views.application.apply import (
    EcosystemApplicationForm,
    validate_organization,
    validate_owner,
)
from ur.users.models import User
from ur.utils.github.client import app_client


@admin.register(InstalledOrganization)
class InstalledOrganizationAdmin(admin.ModelAdmin):
    actions = None
    list_display = ["organization_login", "status"]
    search_fields = ["organization_login"]


admin.site.register(EcosystemUser)


@admin.register(EcosystemApplication)
class EcosystemApplicationAdmin(admin.ModelAdmin):
    list_display = ["organization_login", "is_approved"]
    list_filter = list_display
    search_fields = ["organization_login"]
    readonly_fields = (
        "installation",
        "reason",
        "created",
        "updated",
    )
    # https://github.com/orgs/github-community/discussions/10906

    add_form = EcosystemApplicationForm

    def save_model(self, request, obj: EcosystemApplication, form, change):
        field = "is_approved"
        # When we approve, we'll manually accept the invite to join the organization
        # since we don't want to join random organizations (and also since we don't
        # use SES for inbound emails yet :P).
        # This is only the first step in the approval process.

        # This approval is just that: an approval. For final confirmation, the user
        # needs to pass the ownership test which will be on another screen.
        if change and field in form.changed_data and form.cleaned_data.get(field):
            installation, slug = validate_organization(obj.organization_login)
            slug = validate_owner(installation.installation_id, slug).login
            obj.organization_login = slug
            obj.extra = obj.extra | {
                "approved": datetime.utcnow().isoformat(),
                "finalized": False,
            }
            client = app_client.create_client(installation.installation_id)
            try:
                client.get_organization(slug).invite_user(
                    client.get_user(settings.GITHUB_OWNER_USERNAME),
                    role="admin",
                )
            except GithubException:
                pass
            try:
                user = User.objects.get(obj.installation.sender_id)
            except User.DoesNotExist:
                pass
            else:
                user.email_user(
                    "[Ur OSS World] Application Status",
                    f"Hi {user.get_name()},\n\nYour application for "
                    f"{obj.organization_login} was accepted! To continue, view your "
                    f"organization's page to begin the next steps. Acceptance reason:"
                    f"\n\n{obj.admin_reason}\n\nIf you have any questions, please let "
                    "us know via support@theur.world.\n\nThank you!",
                )
        elif (
            change
            and "admin_reason" in form.changed_data
            and not form.cleaned_data.get(field)
            and not obj.is_approved
        ):
            # Application was rejected
            try:
                user = User.objects.get(obj.installation.sender_id)
            except User.DoesNotExist:
                pass
            else:
                user.email_user(
                    "[Ur OSS World] Application Status",
                    f"Hi {user.get_name()},\n\nYour application for "
                    f"{obj.organization_login} was rejected for the following reason:"
                    f"\n\n{obj.admin_reason}\n\nIf you have any questions, please let "
                    "us know via support@theur.world.\n\nThank you!",
                )
        super().save_model(request, obj, form, change)
