# -*- coding: utf-8 -*-
"""
Library to access GitHub API

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want
"""

import json
import os
import urllib2


class GitHubAPI(object):
    def __init__(self, username=None, password=None):
        self.status_api = self._geturl('https://status.github.com/api.json')
        self.cache = {}
        self.user_api = None
        if username and password:
            url = 'https://api.github.com/users/%s' % username
            try:
                self._basic_authentication(url, username, password)
                self.user_api = self._geturl(url)
            except Exception:
                pass

    def status(self):
        data = self._geturl(self.status_api['status_url'])
        return data

    def status_last_message(self):
        data = self._geturl(self.status_api['last_message_url'])
        return data

    def status_messages(self):
        data = self._geturl(self.status_api['messages_url'])
        return data

    def received_events(self):
        if self.user_api is None:
            return []
        data = self._geturl(self.user_api['received_events_url'])
        return data

    def _basic_authentication(self, url, username, password):
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, username, password)
        urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

    def _geturl(self, url):
        data = urllib2.urlopen(url)
        data = json.loads(data.read())
        return data
