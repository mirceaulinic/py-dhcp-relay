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

# import std lib
import os
import sys
import socket
import logging
from logging.handlers import RotatingFileHandler

# third party libs
import yaml

# import local modules
from dhcp_relay.defaults import DHCPDefaults

log = logging.getLogger(__name__)


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

    PROFILE = logging.PROFILE = 15
    TRACE = logging.TRACE = 5
    GARBAGE = logging.GARBAGE = 1
    QUIET = logging.QUIET = 1000

    LOGGING_LEVELS = {
        'all': logging.NOTSET,
        'debug': logging.DEBUG,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
        'garbage': GARBAGE,
        'info': logging.INFO,
        'profile': PROFILE,
        'quiet': QUIET,
        'trace': TRACE,
        'warning': logging.WARNING,
    }

    ######################

    _config_file_buf = None

    def __init__(self,
                 **kwargs):
        # CLI arguments
        # none of them mandatory
        for karg, warg in kwargs.items():
            arg_name = '_'+karg
            setattr(self, arg_name, warg)
        self._process_logging_vars()
        self._setup_logging()
        self._process_other_args()
        self._process_args()

    def _process_kwargs(self, kargs):
        for arg in kargs:
            attr = arg.upper()
            val = None
            default = getattr(self, arg, None)
            if self._config_file_buf:
                setattr(self, attr, self._config_file_buf.get(arg))
            cli_val = getattr(self, '_'+arg, None)
            if cli_val is not None:
                setattr(self, attr, cli_val)

    def _process_logging_vars(self):
        _logging_vars = (
            'log_file',
            'log_level',
            'log_format',
            'log_date_format',
            'log_full'
        )
        self._process_kwargs(_logging_vars)

    def _setup_logging(self):
        self.LOGGING_LEVEL = self.LOGGING_LEVELS.get(self.LOG_LEVEL.lower(),
                                                     logging.WARNING)
        log_dir = os.path.dirname(self.LOG_FILE)
        if not os.path.exists(log_dir):
            print('Log directory not found,'
                  'trying to create it: {0}'.format(log_dir))
            try:
                os.makedirs(log_dir, mode=0o700)
            except OSError as ose:
                print('Failed to create directory'
                      'for log file: {0} ({1})'.format(log_dir, ose))
                return
        try:
            handler = RotatingFileHandler(self.LOG_FILE,
                                          mode='a',
                                          encoding='utf-8',
                                          delay=0)
        except (IOError, OSError):
            print(
                'Failed to open log file, do you have permission to write to '
                '{0}?'.format(self.LOG_FILE)
            )
            return
        handler.setLevel(self.LOGGING_LEVEL)
        formatter = logging.Formatter(self.LOG_FORMAT,
                                      datefmt=self.LOG_DATE_FORMAT)
        handler.setFormatter(formatter)
        self.LOGGING_HANDLER = handler
        log.addHandler(self.LOGGING_HANDLER)

    def _process_args(self):
        self._config_file_arg()  # mandatory to be processed at the beginning

        self._server_ip_arg()
        self._server_id_arg()
        self._server_port_arg()
        self._client_ip_arg()
        self._client_port_arg()

        self._process_other_args()

    def _config_file_arg(self):
        if self._config_file:
            self.CONFIG_FILE = self._config_file
        try:
            log.debug('Trying to load {cfile} as config file'.format(
                cfile=self.CONFIG_FILE))
            _cfg_file_stream = file(self.CONFIG_FILE, 'r')
            self._config_file_buf = yaml.load(_cfg_file_stream)
        except IOError:
            log.error('Unable to load {cfile}. This may not be critical if '
                      'the server details have been specified as CLI '
                      'arguments.'.format(cfile=self.CONFIG_FILE))

    def _server_ip_arg(self):
        if self._config_file_buf:
            self.SERVER_IP = self._config_file_buf.get('server', {})\
                                                  .get('ip')
        if self._server_ip:
            self.SERVER_IP = self._server_ip
        log.debug('Server IP: {sip}'.format(sip=self.SERVER_IP))

    def _server_id_arg(self):
        if self._config_file_buf:
            self.SERVER_ID = self._config_file_buf.get('server', {})\
                                                  .get('id',
                                                       self.SERVER_IP)
        if self._server_ip:
            self.SERVER_ID = self._server_id
        if not hasattr(self, 'SERVER_ID') or not self.SERVER_ID:
            self.SERVER_ID = self.SERVER_IP
        log.debug('Server ID: {sid}'.format(sid=self.SERVER_ID))

    def _server_port_arg(self):
        if self._config_file_buf:
            self.SERVER_PORT = self._config_file_buf.get('server', {})\
                                                    .get('port',
                                                         self.SERVER_PORT)
        if self._server_port:
            self.SERVER_PORT = self._server_port
        log.debug('Server port: {sport}'.format(sport=self.SERVER_PORT))

    def _get_lo0(self):
        self.CLIENT_IP = socket.gethostbyname(socket.gethostname())

    def _client_ip_arg(self):
        self._get_lo0()  # by default will use the configured lo0
        # on the client server
        if self._config_file_buf:
            self.CLIENT_IP = self._config_file_buf.get('client', {})\
                                                  .get('ip')
        if self._server_ip:
            self.CLIENT_IP = self._server_ip
        log.debug('Client IP: {cip}'.format(cip=self.CLIENT_IP))

    def _client_port_arg(self):
        if self._config_file_buf:
            self.CLIENT_PORT = self._config_file_buf.get('client', {})\
                                                    .get('port',
                                                         self.CLIENT_PORT)
        if self._client_ip:
            self.CLIENT_PORT = self._client_ip
        log.debug('Client port: {cport}'.format(cport=self.CLIENT_PORT))

    def _process_other_args(self):
        _all_other_args = (
            'lease_time',
            'listener_threads',
            'max_wait',
            'ddos_limit'
        )
        self._process_kwargs(_all_other_args)
        if hasattr(self, 'DDOS_LIMIT') and self.DDOS_LIMIT:
            self.PKT_SPLAY = 1.0/self.DDOS_LIMIT  # time between two consecutive
            # DHCP requests when the DDoS limit is configured
