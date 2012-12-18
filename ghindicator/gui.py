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

from ghindicator.monitor import GitHubMonitor
from ghindicator.options import ICON_DIR


def get_icon_file_path(name):
    path = os.path.join(ICON_DIR, name + '.png')
    return path


class GitHubApplet(object):
    def __init__(self, options):
        self.options = options
        self.status = 'unknown'
        self.last_updated = None
        self.monitor = GitHubMonitor(options.username, options.password)
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
        status = self.monitor.check_status()
        if status is not None:
            title = 'GitHub service status is %s' % status['message']['status']
            message = '%s\n%s' % (status['message']['created_on'], status['message']['body'])
            icon = get_icon_file_path(status['message']['status'])
            self.notify(title, message, icon)

        events = self.monitor.check_events()
        for e in reversed(events):
            title = '%s - %s' % (e['created_at'], e['type'])
            message = '%s on %s' % (e['actor']['login'], e['repo']['name'])
            icon = self.monitor.get_user_icon(e['actor'])
            self.notify(title, message, icon)

        gtk.timeout_add(self.options.update_time * 1000, self.update_display)

    def notify(self, title, message, icon):
        if self.options.debug: print('%s - %s' % (title, message.replace('\n', ' ')))
        n = pynotify.Notification(title, message, icon)
        n.show()


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
