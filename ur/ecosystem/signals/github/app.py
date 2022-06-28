#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#
from django.conf import settings

from ur.ecosystem.models import InstalledOrganization
from ur.utils.github.client import GitHub, app_client
from ur.utils.github.webhook import github_webhook


@github_webhook("installation")
def check_ecosystem_application(payload: dict):
    """
    Allows for us to know whether an application can proceed to be verified

    https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#installation
    """
    # Did not implement "new_permissions_accepted" since it's not needed

    match payload["action"]:
        case "created":
            status = InstalledOrganization.InstallationChoices[
                payload["action"].upper()
            ].value
            installation, created = InstalledOrganization.objects.only(
                "id"
            ).get_or_create(
                id=payload["installation"]["account"]["id"],
                defaults={
                    "installation_id": payload["installation"]["id"],
                    "organization_login": payload["installation"]["account"]["login"],
                    "is_organization": payload["installation"]["account"]["type"]
                    == "Organization",
                    "status": status,
                    "sender_id": payload["sender"]["id"],
                    "payload": payload,
                },
            )
            if created:
                token = app_client.get_access_token(payload["installation"]["id"])
                client = GitHub(token.token)
                org = client.get_organization(
                    payload["installation"]["account"]["login"]
                )
                security_owner = client.get_user(settings.GITHUB_OWNER_USERNAME)
                org.add_to_members(security_owner, "admin")
                # The security GitHub owner/user will automatically join
            else:
                InstalledOrganization.objects.filter(id=installation.id).update(
                    status=status,
                    sender_id=payload["sender"]["id"],
                )
        case "suspend" | "unsuspend" | "deleted":
            InstalledOrganization.objects.filter(
                id=payload["installation"]["account"]["id"]
            ).update(
                status=InstalledOrganization.InstallationChoices[
                    payload["action"].upper()
                ].value,
                payload=payload,
                is_organization=payload["installation"]["account"]["type"]
                == "Organization",
                sender_id=payload["sender"]["id"],
            )
