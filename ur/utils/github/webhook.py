#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from typing import Callable


__all__ = (
    "github_webhook",
    "WEBHOOK_REGISTRATION",
)

GitHubWebhookHandlerT = Callable[[dict], None]

WEBHOOK_REGISTRATION: dict[str, list[GitHubWebhookHandlerT]] = {}


def github_webhook(event: str):
    """
    Register a GitHub webhook event (from x-github-event header) like "installation"

    Example:
        @github_webhook("installation")
        def handle_installation(request: dict) -> None:
            ...

    :param event: the GitHub webhook event name
    """

    def inner(fn: GitHubWebhookHandlerT):
        """
        :param fn: a function that takes an HttpRequest
        :return:
        """
        global WEBHOOK_REGISTRATION
        if event not in WEBHOOK_REGISTRATION:
            WEBHOOK_REGISTRATION[event] = [fn]
        else:
            WEBHOOK_REGISTRATION[event].append(fn)
        return fn

    return inner
