# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Mircea Ulinic. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


class DHCPDefaults:

    CONFIG_FILE = '/etc/dhcp-relay/config.yml'

    DAEMON = True
    MULTIPROCESSING = False

    SERVER_PORT = 67  # can be set by the user
    CLIENT_PORT = 67

    DUMMY_IP_ADDRESS = '172.17.17.1'

    LEASE_TIME = 24 * 3600

    LOGGING_ENABLED = True
    LOG_FILE = '/var/log/dhcp-relay.log'
    LOG_LEVEL = 'warning'
    LOG_FORMAT = '%(asctime)s [%(name)-15s][%(levelname)-8s] %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    DETAILED_LOG = True

    LISTENER_THREADS = 5

    MAX_WAIT = 3  # seconds
