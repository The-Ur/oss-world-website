#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

import datetime
import logging
from typing import Optional

from github.Requester import Requester as BaseRequester

from ur.utils.github.vendor.GithubIntegration import GithubIntegration


# For App authentication, time remaining before token expiration to request a new one
ACCESS_TOKEN_REFRESH_THRESHOLD_SECONDS = 20


class Requester(BaseRequester):
    def __init__(
        self,
        app_id: int | str | None = None,
        app_private_key: str | None = None,
        *args,
        **kwargs,
    ):
        self.__installation_authorization = None
        self.__app_id = app_id
        self.__app_private_key = app_private_key

        if self.__app_id is not None and self.__app_private_key is not None:
            self._refresh_token()

        super().__init__(*args, **kwargs)

    def _must_refresh_token(self) -> bool:
        """Check if it is time to refresh the API token gotten from the GitHub app installation"""
        if not self.__installation_authorization:
            return False
        return (
            self.__installation_authorization.expires_at
            < datetime.datetime.utcnow()
            + datetime.timedelta(seconds=ACCESS_TOKEN_REFRESH_THRESHOLD_SECONDS)
        )

    def _get_installation_authorization(self):
        assert self.__app_id is not None and self.__app_private_key is not None
        integration = GithubIntegration(self.__app_id, self.__app_private_key)
        installation_id = integration.get_installations()[0].id
        return integration.get_access_token(installation_id)

    def _refresh_token_if_needed(self) -> None:
        """Get a new access token from the GitHub app installation if the one we have is about to expire"""
        if not self.__installation_authorization:
            return
        if self._must_refresh_token():
            logging.debug("Refreshing access token")
            self._refresh_token()

    def _refresh_token(self) -> None:
        """In the context of a GitHub app, refresh the access token"""
        assert self.__app_id is not None and self.__app_private_key is not None
        self.__installation_authorization = self._get_installation_authorization()
        self.__authorizationHeader = f"token {self.__installation_authorization.token}"

    def __authenticate(self, url, requestHeaders, parameters):
        self._refresh_token_if_needed()
        if self.__authorizationHeader is not None:
            requestHeaders["Authorization"] = self.__authorizationHeader
