# -*- coding: utf-8 -*-
"""
Class that abstracts the GitHub API with some high level methods.

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want
"""

import datetime
import os
import urllib2

from ghindicator.api import GitHubAPI
from ghindicator.options import CACHE_DIR


class GitHubMonitor(object):
    def __init__(self, username=None, password=None):
        self.api = GitHubAPI(username, password)
        self.last_updated = None
        self.status = None
        self.past_events = []
        self._last_notified_event = 0

    def check_status(self):
        try:
            st = self.api.status()
        except (urllib2.URLError, TypeError, ValueError):
            st = {
                'status': 'unknown',
                'last_updated': 'unknown'
            }
        if self.last_updated != st['last_updated']:
            self.last_updated = st['last_updated']
            if self.status != st['status']:
                self.status = st['status']
                try:
                    msg = self.api.status_last_message()
                except (urllib2.URLError, TypeError, ValueError):
                    msg = {
                        'status': 'unknown',
                        'body': 'Cannot access GitHub API',
                        'created_on': 'unknown'
                    }
                return {'status': st, 'message': msg}

    def check_events(self):
        lne = self._get_last_notified_event()
        events = self.api.received_events()
        if lne is None:
            week = datetime.timedelta(7)
            now = datetime.datetime.utcnow()
            start = now - week
            mkdate = datetime.datetime.strptime
            events = [x for x in events if mkdate(x['created_at'], '%Y-%m-%dT%H:%M:%SZ') > start]
        else:
            events = [x for x in events if x['id'] > lne]
        if events:
            self._set_last_notified_event(events[0]['id'])
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

    def _get_last_notified_event(self):
        fname = os.path.join(CACHE_DIR, 'last_notified_event')
        try:
            with open(fname, 'r') as f:
                l = f.read()
                l = l.strip('\n ')
                return l
        except (IOError, ValueError):
            return None

    def _set_last_notified_event(self, value):
        fname = os.path.join(CACHE_DIR, 'last_notified_event')
        with open(fname, 'w') as f:
            f.write(value)
