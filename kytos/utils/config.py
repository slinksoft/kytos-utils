"""Kytos Configuration."""
# This file is part of kytos-utils.
#
# Copyright (c) 2016 Kytos Team
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#
# kytos-utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kytos-utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
from configparser import ConfigParser

log = logging.getLogger(__name__)


class KytosConfig():
    def __init__(self, config_file='~/.kytosrc'):
        self.config_file = os.path.expanduser(config_file)
        self.debug = False

        # allow_no_value=True is used to keep the comments on the config file.
        self.config = ConfigParser(allow_no_value=True)

        # Parse the config file. If no config file was found, then create some
        # default sections on the config variable.
        self.config.read(self.config_file)
        self.check_sections(self.config)

        if not os.path.exists(self.config_file):
            log.warning("Config file %s not found.", self.config_file)
            log.warning("Creating a new empty config file.")
            with open(self.config_file, 'w') as output_file:
                os.chmod(self.config_file, 0o0600)
                self.config.write(output_file)

        self.set_env_or_defaults()

    def set_env_or_defaults(self):
        """Read some environment variables and set them on the config.

        If no environment variable is found and the config section/key is
        empty, then set some default values.
        """
        napps_uri = os.environ.get('NAPPS_API_URI')
        user = os.environ.get('NAPPS_USER')
        token = os.environ.get('NAPPS_TOKEN')
        napps_path = os.environ.get('NAPPS_PATH')

        self.config.set('global', 'debug', self.debug)

        if user is not None:
            self.config.set('auth', 'user', user)

        if token is not None:
            self.config.set('auth', 'token', token)

        if napps_uri is not None:
            self.config.set('napps', 'uri', napps_uri)
        elif not self.config.has_option('napps', 'uri'):
            self.config.set('napps', 'uri', 'https://napps.kytos.io/api/')

        # Set paths if NAPPS_PATH is given or if not found in config
        if napps_path or not self.config.has_option('napps', 'enabled_path'):
            if not napps_path:  # default paths
                base = os.environ.get('VIRTUAL_ENV') or '/'
                napps_path = os.path.join(base, 'var', 'lib', 'kytos', 'napps')
            self.config.set('napps', 'enabled_path', napps_path)
            self.config.set('napps', 'installed_path',
                            os.path.join(napps_path, '.installed'))

    @staticmethod
    def check_sections(config):
        """Create a empty config file."""
        default_sections = ['global', 'auth', 'napps']
        for section in default_sections:
            if not config.has_section(section):
                config.add_section(section)

    def save_token(self, user, token):
        self.config.set('auth', 'user', user)
        self.config.set('auth', 'token', token)
        # allow_no_value=True is used to keep the comments on the config file.
        new_config = ConfigParser(allow_no_value=True)

        # Parse the config file. If no config file was found, then create some
        # default sections on the config variable.
        new_config.read(self.config_file)
        self.check_sections(new_config)

        new_config.set('auth', 'user', user)
        new_config.set('auth', 'token', token)
        filename = os.path.expanduser(self.config_file)
        with open(filename, 'w') as out_file:
            os.chmod(filename, 0o0600)
            new_config.write(out_file)


    def clear_token(self):
        # allow_no_value=True is used to keep the comments on the config file.
        new_config = ConfigParser(allow_no_value=True)

        # Parse the config file. If no config file was found, then create some
        # default sections on the config variable.
        new_config.read(self.config_file)
        self.check_sections(new_config)

        new_config.remove_option('auth', 'user')
        new_config.remove_option('auth', 'token')
        filename = os.path.expanduser(self.config_file)
        with open(filename, 'w') as out_file:
            os.chmod(filename, 0o0600)
            new_config.write(out_file)
