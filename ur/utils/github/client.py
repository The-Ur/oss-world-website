#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

"""
How to utilize the GitHub clients

app_client is a GitHub client that is authenticated for Ur OSS World GitHub App.
Its primary usage is to grab an access token for REST API requests like this:

```python
installation = app.get_installation(owner, repo)
token = app_client.get_access_token(installation.id)
```

Then, you can import the main GitHub client:
```python
from ur.utils.github.client import GitHub

client = GitHub(token.token)
```
"""

from django.conf import settings
from github import enable_console_debug_logging

from ur.utils.github.vendor.GithubIntegration import GithubIntegration
from ur.utils.github.vendor.MainClass import Github as GitHub


__all__ = ("app_client", "GitHub")


app_client = GithubIntegration(settings.GITHUB_APP_ID, settings.GITHUB_APP_PRIVATE_KEY)


if settings.DEBUG:
    enable_console_debug_logging()
