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

# third party libs
import yaml

# import local modules
from dhcp_relay.defaults import DHCPDefaults


class DHCPGlobals(DHCPDefaults):

    SERVER_IP = None
    SERVER_IDENTIFIER = None  # by default will be the SERVER_IP
    CLIENT_IP = None  # if not specified will take lo0
    DDOS_LIMIT = None
    PKT_SPLAY = None  # only if DDoS rate is set

    ######################
    # DO NOT MODIFY THIS:
    ######################

    DHCPLIB_CONSTANTS = {
        'DHCPDISCOVER': {
            'op': 1,
            'dhcp_message_type': 1
        },
        'DHCPREQUEST': {
            'op': 1,
            'dhcp_message_type': 3
        },
        'DHCPRELEASE': {
            'op': 1,
            'dhcp_message_type': 7
        }
    }

    ######################

    _config_file_buf = None

    def __init__(self,
                 config_file=None,
                 server_ip=None,
                 server_id=None,
                 server_port=None,
                 client_ip=None,
                 client_port=None,
                 lease_time=None,
                 listener_threads=None,
                 max_wait=None,
                 log_level=None,
                 log_file=None,
                 log_full=None,
                 log_date_format=None,
                 daemon=None,
                 multiprocessing=None):
        # CLI arguments
        # none of them mandatory
        self._config_file = config_file
        self._server_ip = server_ip
        self._server_port = server_port
        self._server_id = server_id
        self._client_ip = client_ip
        self._client_port = client_port
        self._lease_time = lease_time
        self._listener_threads = listener_threads
        self._max_wait = max_wait
        self._ddos_limit = ddos_limit
        self._log_level = log_level
        self._log_file = log_file
        self._log_full = log_full
        self._log_date_format = log_date_format
        self._daemon = daemon
        self._multiprocessing = multiprocessing

        self._process_args()

    def _process_args(self):
        self._config_file_arg()  # mandatory to be processed at the beginning

        self._server_ip_arg()
        self._server_id_arg()
        self._server_port_arg()
        self._client_ip_arg()
        self._client_port_arg()

        self._other_args()

    def _config_file_arg(self):
        if self._config_file:
            self.CONFIG_FILE = self._config_file
        try:
            _cfg_file_stream = file(self.CONFIG_FILE, 'r')
            self._config_file_buf = yaml.load(_cfg_file_stream)
        except IOError:
            # no cfg file, no problem
            pass

    def _server_ip_arg(self):
        if self._config_file_buf:
            self.SERVER_IP = self._config_file_buf.get('server', {})\
                                                  .get('ip')
        if self._server_ip:
            self.SERVER_IP = self._server_ip

    def _server_id_arg(self):
        if self._config_file_buf:
            self.SERVER_ID = self._config_file_buf.get('server', {})\
                                                  .get('id',
                                                       self.SERVER_IP)
        if self._server_ip:
            self.SERVER_ID = self._server_id

    def _server_port_arg(self):
        if self._config_file_buf:
            self.SERVER_PORT = self._config_file_buf.get('server', {})\
                                                    .get('port',
                                                         self.SERVER_PORT)
        if self._server_ip:
            self.SERVER_PORT = self._server_ip

    def _client_ip_arg(self):
        if self._config_file_buf:
            self.CLIENT_IP = self._config_file_buf.get('client', {})\
                                                  .get('ip')
        if self._server_ip:
            self.CLIENT_IP = self._server_ip

    def _client_port_arg(self):
        if self._config_file_buf:
            self.CLIENT_PORT = self._config_file_buf.get('client', {})\
                                                    .get('port',
                                                         self.CLIENT_PORT)
        if self._client_ip:
            self.CLIENT_PORT = self._client_ip

    def _other_args(self):
        _all_other_args = (
            'lease_time',
            'listener_threads',
            'max_wait',
            'ddos_limit',
            'log_file',
            'log_level',
            'log_date_format',
            'log_full'
        )
        for arg in _all_other_args:
            attr = arg.upper()
            val = None
            default = getattr(self, arg, None)
            if self._config_file_buf:
                setattr(self, attr, self._config_file_buf.get(arg))
            cli_val = getattr(self, '_'+arg, None)
            if cli_val is not None:
                setattr(self, attr, cli_val)
