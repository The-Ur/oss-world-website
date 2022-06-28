#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

from github import Github as BaseGithub

from ur.utils.github.vendor.Consts import (
    DEFAULT_BASE_URL,
    DEFAULT_PER_PAGE,
    DEFAULT_TIMEOUT,
)
from ur.utils.github.vendor.Requester import Requester


class Github(BaseGithub):
    def __init__(
        self,
        login_or_token=None,
        password=None,
        jwt=None,
        app_id=None,
        app_private_key=None,
        base_url=DEFAULT_BASE_URL,
        timeout=DEFAULT_TIMEOUT,
        user_agent="PyGithub/Python",
        per_page=DEFAULT_PER_PAGE,
        verify=True,
        retry=None,
        pool_size=None,
    ):
        kwargs = dict(
            login_or_token=login_or_token,
            password=password,
            jwt=jwt,
            base_url=base_url,
            timeout=timeout,
            user_agent=user_agent,
            per_page=per_page,
            verify=verify,
            retry=retry,
            pool_size=pool_size,
        )
        super().__init__(**kwargs)
        self.__requester = Requester(app_id, app_private_key, **kwargs)
