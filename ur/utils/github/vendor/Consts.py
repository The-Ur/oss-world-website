#
#  Copyright (c) Ur LLC and its affiliates
#
#  This source code is licensed under the Apache 2.0 license found
#  in the LICENSE file in the root directory of this source tree.
#

DEFAULT_BASE_URL = "https://api.github.com"
DEFAULT_STATUS_URL = "https://status.github.com"
# As of 2018-05-17, Github imposes a 10s limit for completion of API requests.
# Thus, the timeout should be slightly > 10s to account for network/front-end
# latency.
DEFAULT_TIMEOUT = 15
DEFAULT_PER_PAGE = 30
