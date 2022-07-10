#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

import github
from github import GithubIntegration as BaseGithubIntegration
from github.Installation import Installation
from github.PaginatedList import PaginatedList

from ur.utils.github.vendor.Consts import DEFAULT_PER_PAGE, DEFAULT_TIMEOUT


class GithubIntegration(BaseGithubIntegration):
    def get_installations(self) -> PaginatedList:
        """
        :calls: GET /app/installations <https://docs.github.com/en/rest/reference/apps#list-installations-for-the-authenticated-app>
        :rtype: :class:`github.PaginatedList.PaginatedList[github.Installation.Installation]`
        """
        from ur.utils.github.vendor.Requester import Requester

        return PaginatedList(
            contentClass=Installation,
            requester=Requester(
                login_or_token=None,
                password=None,
                jwt=self.create_jwt(),
                app_id=None,
                app_private_key=None,
                base_url=self.base_url,  # type: ignore
                timeout=DEFAULT_TIMEOUT,
                user_agent="PyGithub/Python",
                per_page=DEFAULT_PER_PAGE,
                verify=True,
                retry=None,
                pool_size=None,
            ),
            firstUrl="/app/installations",
            firstParams=None,
            headers={
                "Authorization": f"Bearer {self.create_jwt()}",
                "User-Agent": "PyGithub/Python",
            },
            list_item="installations",
        )

    def create_client(self, installation_id: int = None) -> github.Github:
        """
        Creates a github.Github client. If no installations are found (most
        likely due a new integration during development).

        :param installation_id: An installation ID. Defaults to using an existing
        installation.
        """
        try:
            if not installation_id:
                installation_id = next(iter(self.get_installations())).id
        except StopIteration:
            return github.Github()
        else:
            token = self.get_access_token(installation_id)
            return github.Github(token.token)
