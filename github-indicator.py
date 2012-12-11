#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Show a tray icon to indicate the status of Github service.
Could serve as notification for pull requests, etc, in the future.

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want

"""

import appindicator
import gtk
import json
import os
import pynotify
import sys
import urllib2


icon_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), 'icons'))


def get_icon_file_path(name):
    path = os.path.join(icon_dir, name + '.png')
    return os.path.isfile(path) and path or get_icon_file_path('unknown')


class GitHubAPI(object):
    def __init__(self, apiurl='https://status.github.com/api.json'):
        self.api = self._geturl(apiurl)

    def status(self):
        try:
            data = self._geturl(self.api['status_url'])
        except (urllib2.URLError, TypeError, ValueError):
            data = {
                'status': 'unknown',
                'last_updated': 'unknown'
            }
        return data

    def last_message(self):
        try:
            data = self._geturl(self.api['last_message_url'])
        except (urllib2.URLError, TypeError, ValueError):
            data = {
                'status': 'unknown',
                'body': 'Cannot access GitHub API',
                'created_on': 'unknown'
            }
        return data

    def messages(self):
        data = self._geturl(self.api['messages_url'])
        return data

    def _geturl(self, url):
        data = urllib2.urlopen(url)
        data = json.loads(data.read())
        return data


class GitHubIndicator(object):
    def __init__(self):
        self.tray = self.create_indicator()
        self.menu = self.create_menu()
        self.tray.set_menu(self.menu)
        self.menu.show_all()

        self.api = GitHubAPI()
        self.status = 'unknown'
        self.last_updated = None

        pynotify.init('github-indicator')

    def create_indicator(self):
        ind = appindicator.Indicator("github-indicator",
                                      get_icon_file_path('unknown'),
                                      appindicator.CATEGORY_APPLICATION_STATUS)
        ind.set_status(appindicator.STATUS_ACTIVE)
        return ind

    def create_menu(self):
        menu = gtk.Menu()

        # quit control
        item_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        item_quit.connect('activate', self.quit_cb)
        menu.append(item_quit)

        return menu

    def quit_cb(self, *args, **kwargs):
        gtk.main_quit()
        sys.exit()
        raise KeyboardInterrupt

    def main(self):
        gtk.gdk.threads_init()
        gtk.timeout_add(10 * 1000, self.update_display)
        gtk.main()

    def update_display(self, *args, **kwargs):
        st = self.api.status()
        if st['last_updated'] != self.last_updated:
            self.last_updated = st['last_updated']
            if self.status != st['status']:
                self.status = st['status']
                msg = self.api.last_message()
                self.message = msg['body'] + ' -- ' + msg['created_on']
                self.set_icon()
                self.notify_status()
        return True

    def set_icon(self):
        icon_file = get_icon_file_path(self.status)
        self.tray.set_icon(icon_file)

    def notify_status(self):
        title = 'GitHub status is %s' % self.status
        message = '%s\n%s' % (self.last_updated, self.message)
        icon_file = get_icon_file_path(self.status)
        n = pynotify.Notification(title, message, icon_file)
        n.show()


if __name__ == '__main__':
    try:
        ghi = GitHubIndicator()
        ghi.main()
    except KeyboardInterrupt:
        pass
