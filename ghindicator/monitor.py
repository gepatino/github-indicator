# -*- coding: utf-8 -*-
"""
Class that serves as a GitHub monitor, abstracting the API with some high level methods.

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want
"""

import os

from ghindicator.api import GitHubAPI
from ghindicator.options import CACHE_DIR


class GitHubMonitor(object):
    def __init__(self, username=None, password=None):
        self.last_updated = None
        self.status = None
        self.message = ''
        self.past_events = []
        self.username = username
        self.password = password
        self.api = GitHubAPI(self.username, self.password)

    def check_status(self):
        st = self.api.status()
        if st['last_updated'] != self.last_updated:
            self.last_updated = st['last_updated']
            if self.status != st['status']:
                self.status = st['status']
                msg = self.api.status_last_message()
                self.message = msg['body'].replace('\n', ' ') + ' -- ' + msg['created_on']
                return {'status': st, 'message': msg}

    def check_events(self):
        events = self.api.received_events()
        events = [x for x in reversed(events) if x['id'] not in self.past_events]
        for e in events:
            self.past_events.append(e['id'])
        return events

    def get_user_icon(self, user):
        icon = os.path.join(CACHE_DIR, user['login'] + '.png')
        if not os.path.isfile(icon):
            try:
                res = urllib2.urlopen(user['avatar_url'])
                with open(icon, 'wb') as f:
                    f.write(res.read())
            except Exception:
                icon = None
        return icon
