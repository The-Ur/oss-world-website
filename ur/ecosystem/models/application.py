#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from django.db import models
from django.utils.translation import gettext_lazy as _

from ur.utils.github.webhook import github_webhook


class InstalledOrganization(models.Model):
    """Organizations that installed the GitHub app."""

    id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name=_("Organization ID from GitHub")
    )
    node_id = models.CharField(max_length=30, verbose_name=_("Organization node ID"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # Original installation id
    installation_id = models.PositiveBigIntegerField()
    organization_login = models.SlugField(
        _("Organization slug/username"),
        max_length=39,
        help_text=_(
            "Like a GitHub username, GitHub organizations also have a unique GitHub"
            " username. You can identify this from the URL of the organization's GitHub"
            " profile such as `https://github.com/The-Ur` where The-Ur is the slug."
        ),
    )
    sender_id = models.PositiveBigIntegerField()
    is_organization = models.BooleanField(default=True)

    class InstallationChoices(models.IntegerChoices):
        CREATED = 0
        DELETED = 1
        SUSPEND = 2
        UNSUSPEND = 3

    status = models.PositiveSmallIntegerField(choices=InstallationChoices.choices)

    payload: dict = models.JSONField(
        default=dict, blank=True, verbose_name=_("GitHub Webhook Payload")
    )
    extra: dict = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.organization_login} ({self.id})"


@github_webhook("organization")
def rename_ecosystem(data: dict):
    if data["action"] != "renamed":
        return
    _original_name = data["changes"]["organization"]["login"]["from"]
    InstalledOrganization.objects.filter(id=data["organization"]["id"]).update(
        organization_login=data["organization"]["login"]
    )
    EcosystemApplication.objects.filter(
        installation_id=data["organization"]["id"]
    ).update(organization_login=data["organization"]["login"])


class EcosystemApplication(models.Model):
    """User-filled application to create an ecosystem on Ur OSS World"""

    installation = models.OneToOneField(
        InstalledOrganization,
        primary_key=True,
        on_delete=models.CASCADE,
        verbose_name=_("Organization ID from GitHub"),
        to_field="id",
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # For organizational purposes in the admin
    organization_login = models.SlugField(
        _("Organization slug/username"),
        max_length=39,
        help_text=_(
            "Like a GitHub username, GitHub organizations also have a unique GitHub"
            " username. You can identify this from the URL of the organization's GitHub"
            " profile such as `https://github.com/The-Ur` where The-Ur is the slug."
        ),
    )
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    reason = models.TextField(
        verbose_name=_("Reason to join"),
        help_text=_("Why should this ecosystem exist?"),
    )

    # Admin
    admin_reason = models.TextField(
        verbose_name=_("Accept/Rejection Reason"),
        help_text=_(
            "(Admin only) Reasons to accept include a vibrant community or enough "
            "dedicated packages for a community to organize around. Rejection "
            "reasons can range from duplicate to too niche."
        ),
    )
    is_approved = models.BooleanField(default=False)

    extra = models.JSONField(default=dict, blank=True)

    @property
    def status_text(self):
        if self.is_approved:
            return _("Approved")
        if hasattr(self, "admin_pending"):
            return _("Pending") if self.admin_pending else _("Rejected")  # type: ignore
        return _("Rejected") if self.admin_reason else _("Pending")

    @property
    def is_pending(self):
        if self.is_approved:
            return False
        if hasattr(self, "admin_pending"):
            return self.admin_pending
        return not self.admin_reason
