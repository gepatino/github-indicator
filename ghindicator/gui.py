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
import os
import pynotify
import sys
import urllib2

from ghindicator.api import GitHubAPI
from ghindicator.options import ICON_DIR
from ghindicator.options import CACHE_DIR


def get_icon_file_path(name):
    path = os.path.join(ICON_DIR, name + '.png')
    return path


class GitHubApplet(object):
    def __init__(self, options):
        self.options = options
        self.api = GitHubAPI(options.username, options.password)
        self.status = 'unknown'
        self.last_updated = None

        self.tray = self.create_indicator()
        self.menu = self.create_menu()
        self.past_events = []

        pynotify.init('github-indicator')

    def create_indicator(self): pass

    def set_icon(self): pass

    def create_menu(self):
        menu = gtk.Menu()

        # quit control
        item_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        item_quit.connect('activate', self.quit_cb)
        menu.append(item_quit)

        return menu

    def main(self):
        gtk.gdk.threads_init()
        if self.options.debug: print('Initial status check.')
        self.update_display()
        if self.options.debug: print('Starting gtk main.')
        gtk.main()

    def quit_cb(self, *args, **kwargs):
        gtk.main_quit()
        sys.exit()
        raise KeyboardInterrupt

    def update_display(self, *args, **kwargs):
        self._check_status()
        self._check_events()
        gtk.timeout_add(self.options.update_time * 1000, self.update_display)

    def notify_status(self):
        title = 'GitHub service status is %s' % self.status
        message = '%s\n%s' % (self.last_updated, self.message)
        icon_file = get_icon_file_path(self.status)
        self.notify(title, message, icon_file)

    def notify(self, title, message, icon):
        if self.options.debug: print('%s - %s' % (title, message.replace('\n', ' ')))
        n = pynotify.Notification(title, message, icon)
        n.show()

    def _check_status(self):
        if self.options.debug: print('Fetching GitHub API Status')
        st = self.api.status()
        if st['last_updated'] != self.last_updated:
            self.last_updated = st['last_updated']
            if self.status != st['status']:
                self.status = st['status']
                if self.options.debug: print('\tNew Status: %s.' % (self.status))
                msg = self.api.status_last_message()
                self.message = msg['body'].replace('\n', ' ') + ' -- ' + msg['created_on']
                self.set_icon()
                self.notify_status()
            else:
                if self.options.debug: print('\tStatus unchanged.')
        else:
            if self.options.debug: print('\tNothing changed.')

    def _check_events(self):
        if self.options.debug: print('Fetching users events')
        events = self.api.received_events()
        if self.options.debug: print '\t%s events found.' % len(events)
        events = [x for x in reversed(events) if x['id'] not in self.past_events]
        if self.options.debug: print '\t%s new events.' % len(events)
        for e in events:
            self.past_events.append(e['id'])
            title = '%s - %s' % (e['created_at'], e['type'])
            message = '%s on %s' % (e['actor']['login'], e['repo']['name'])
            icon = self._get_user_icon(e['actor'])
            self.notify(title, message, icon)

    def _get_user_icon(self, user):
        icon = os.path.join(CACHE_DIR, user['login'] + '.png')
        if not os.path.isfile(icon):
            try:
                res = urllib2.urlopen(user['avatar_url'])
                with open(icon, 'wb') as f:
                    f.write(res.read())
            except Exception:
                icon = None
        return icon


class GitHubAppIndicator(GitHubApplet):
    def create_indicator(self):
        icon_file = get_icon_file_path('unknown')
        if self.options.debug: print('Creating appindicator with default icon %s' % icon_file)
        ind = appindicator.Indicator('github-indicator', icon_file,
                                     appindicator.CATEGORY_APPLICATION_STATUS)
        ind.set_status(appindicator.STATUS_ACTIVE)
        return ind

    def create_menu(self):
        menu = super(GitHubAppIndicator, self).create_menu()
        self.tray.set_menu(menu)
        menu.show_all()
        return menu

    def set_icon(self):
        icon_file = get_icon_file_path(self.status)
        if self.options.debug: print('Setting icon from file: %s' % icon_file)
        self.tray.set_icon(icon_file)


class GitHubStatusIcon(GitHubApplet):
    def create_indicator(self):
        icon_file = get_icon_file_path(self.status)
        if self.options.debug: print('Creating StatusIcon from file (%s)' % icon_file)
        icon = gtk.status_icon_new_from_file(icon_file)
        if self.options.debug and not icon.is_embedded(): print('\tCouldn\'t find a notification area')
        return icon

    def create_menu(self):
        menu = super(GitHubStatusIcon, self).create_menu()
        self.tray.connect('popup-menu', self.popup_menu_cb)
        return menu

    def set_icon(self):
        icon_file = get_icon_file_path(self.status)
        if self.options.debug: print('Setting icon from file: %s' % icon_file)
        self.tray.set_from_file(icon_file)

    def popup_menu_cb(self, widget, button, time):
        if button == 3:
            self.menu.show_all()
            self.menu.popup(None, None, None, 3, time)


def get_app(options):
    if options.status_icon:
        if options.debug: print('Using StatusIcon version')
        app = GitHubStatusIcon(options)
    else:
        if options.debug: print('Using AppIndicator version')
        app = GitHubAppIndicator(options)
    return app
