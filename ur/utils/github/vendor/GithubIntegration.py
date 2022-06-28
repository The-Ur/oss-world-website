#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

import github
from github import GithubIntegration as BaseGithubIntegration
from github import Installation, PaginatedList

from ur.utils.github.vendor.Consts import DEFAULT_PER_PAGE, DEFAULT_TIMEOUT


class GithubIntegration(BaseGithubIntegration):
    def get_installations(self):
        """
        :calls: GET /app/installations <https://docs.github.com/en/rest/reference/apps#list-installations-for-the-authenticated-app>
        :rtype: :class:`github.PaginatedList.PaginatedList[github.Installation.Installation]`
        """
        from ur.utils.github.vendor.Requester import Requester

        return PaginatedList.PaginatedList(
            contentClass=Installation.Installation,
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
