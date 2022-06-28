#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from github import UnknownObjectException
from github.Organization import Organization

from ur.ecosystem.models import EcosystemApplication, InstalledOrganization
from ur.utils.github.client import app_client
from ur.utils.github.vendor.MainClass import Github


class EcosystemApplicationForm(forms.Form):
    organization_slug = forms.SlugField(
        label=_("Organization slug/username"),
        help_text=_(
            "Like a GitHub username, GitHub organizations also have a unique GitHub"
            " username. You can identify this from the URL of the organization's GitHub"
            " profile such as `https://github.com/The-Ur` where The-Ur is the slug."
        ),
    )
    reason = forms.CharField(
        label=_("Why this ecosystem should exist"),
        help_text=_(
            "We are checking whether it's large like a programming language or too "
            "niche like a small web framework without many dedicated packages for "
            "it (Starlette (small) compared to Django (large))."
        ),
        widget=forms.Textarea(),
        min_length=30,
    )

    def __init__(self, *args, **kwargs):
        self.request: HttpRequest = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    github_org: Organization = None

    def clean_organization_slug(self):
        data = self.cleaned_data["organization_slug"]
        try:
            self.github_org = app_client.get_organization(data)
        except UnknownObjectException:
            raise forms.ValidationError(_("Organization not found"))

        if EcosystemApplication.objects.filter(id=self.github_org.id).exists():
            raise forms.ValidationError(
                _(
                    "Organization already applied. If you think this is a mistake, "
                    "please contact %(email)s"
                )
                % {"email": "support@theur.world"}
            )

        try:
            installation = InstalledOrganization.objects.only(
                "id",
                "sender_id",
                "status",
                "installation_id",
            ).get(id=self.github_org.id)
        except InstalledOrganization.DoesNotExist:
            raise forms.ValidationError(_("Organization not installed"))

        if installation.sender_id != self.request.user.id:
            raise forms.ValidationError(
                _(
                    "You may not be the owner of this organization. If you are, then "
                    'suspend the GitHub app "Ur OSS World" in "Integrations" in the'
                    " organization settings and then unsuspend it. Then try re-applying"
                    " here again."
                )
            )
        if (
            installation.status
            == InstalledOrganization.InstallationChoices.SUSPEND.value
        ):
            raise forms.ValidationError(
                _(
                    'Current status of the GitHub app "Ur OSS World" is suspended. '
                    "Please unsuspend the app by heading to your organization's "
                    "settings > Integrations > GitHub Apps > Configure > Unsuspend."
                )
            )
        if (
            installation.status
            == InstalledOrganization.InstallationChoices.DELETED.value
        ):
            raise forms.ValidationError(
                _(
                    'Current status of the GitHub app "Ur OSS World" is deleted. '
                    "Please re-install the app by heading to: %(marketplace_link)s"
                )
                % {"marketplace_link": "https://github.com/apps/ur-oss-world"}
            )

        # Finally, we need to check whether our own user is the owner of the
        # organization for security purposes.

        token = app_client.get_access_token(installation.installation_id)
        if not token:
            raise forms.ValidationError(
                _(
                    "Could not get an access token for the GitHub app "
                    '"Ur OSS World". App could possibly be not installed.'
                )
            )
        github_client = Github(token)
        self.github_org = github_client.get_organization(self.github_org.login)
        members = list(self.github_org.get_members(role="admin"))
        if len(members) == 1:
            if members[0].login != settings.GITHUB_OWNER_USERNAME:
                raise forms.ValidationError(
                    _(
                        "The %(owner)s GitHub security user is not the organization "
                        "owner. Please invite the owner, leave the organization, then"
                        " join back. You will be reinstated as an owner."
                    )
                    % {"owner": settings.GITHUB_OWNER_USERNAME}
                )
        elif len(members) == 0:  # pragma: no cover
            raise forms.ValidationError(
                f"Organization has no owners. Make {settings.GITHUB_OWNER_USERNAME} "
                "the owner."
            )
        else:
            # This owner is to be used for testing whether we have total control
            failed_to_convert = False
            converted_owners = []
            org_owner_missing = True
            for member in members:
                if member.login.upper() == settings.GITHUB_OWNER_USERNAME.upper():
                    org_owner_missing = False
                    continue
                try:
                    converted_owners.append(member)
                    self.github_org.add_to_members(member, role="member")
                except Exception:  # type: ignore
                    for converted_owner in converted_owners:
                        self.github_org.add_to_members(converted_owner, role="admin")
                    raise forms.ValidationError(
                        _("Could not modify a user's ownership in the organization.")
                        + " "
                        + _(
                            "We instate our own organization's owner in each ecosystem"
                            " as the head of the GitHub organization for security "
                            "purposes."
                        )
                    )

            for converted_owner in converted_owners:
                self.github_org.add_to_members(converted_owner, role="admin")
            if org_owner_missing:
                raise forms.ValidationError(
                    _(
                        "Our own organization's owner is not the owner of the "
                        "organization."
                    )
                    + " "
                    + _(
                        "We instate our own organization's owner in each ecosystem"
                        " as the head of the GitHub organization for security "
                        "purposes."
                    )
                )

        return self.github_org.login

    def save(self, commit: bool = True):
        application = EcosystemApplication(
            id=self.github_org.id,
            user=self.request.user,
            organization_slug=self.github_org.login,
            reason=self.cleaned_data["reason"],
        )
        if commit:
            return application.save()
        return application


class ApplicationView(LoginRequiredMixin, FormView):
    template_name = "ecosystem/apply.html"

    def dispatch(self, request, *args, **kwargs):
        data = super().dispatch(request, *args, **kwargs)
        return data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def form_valid(self, form: EcosystemApplicationForm):
        form.save(commit=True)
        messages.success(
            self.request,
            _(
                "Application successfully submitted:) Please wait 3-5 business days "
                "to review your application, and we'll email you with updates."
            ),
        )
        return super().form_valid(form)
