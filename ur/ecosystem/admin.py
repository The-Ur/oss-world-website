#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.contrib import admin

from ur.ecosystem.models import EcosystemApplication, InstalledOrganization
from ur.ecosystem.views.application.apply import EcosystemApplicationForm


@admin.register(InstalledOrganization)
class InstalledOrganizationAdmin(admin.ModelAdmin):
    actions = None
    list_display = ["organization_login", "status"]
    search_fields = ["organization_login"]


@admin.register(EcosystemApplication)
class EcosystemApplicationAdmin(admin.ModelAdmin):
    list_display = ["organization_login", "is_approved"]
    list_filter = list_display
    search_fields = ["organization_login"]
    readonly_fields = ("id", "reason", "is_approved")

    add_form = EcosystemApplicationForm

    def approve_application(self, request, queryset):
        obj = queryset.get()
