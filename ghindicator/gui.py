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

from ghindicator import language
from ghindicator.monitor import GitHubMonitor
from ghindicator.options import ICON_DIR
from ghindicator.options import APPNAME

import logging
logger = logging.getLogger(APPNAME)


def get_icon_file_path(name):
    path = os.path.join(ICON_DIR, name + '.png')
    return path


class GitHubApplet(object):
    def __init__(self, options):
        self.options = options
        self.last_updated = None
        self.monitor = GitHubMonitor(options.username, options.password)
        self.tray = self.create_indicator()
        self.status_menu = None
        self.status_details_menu = None
        self.menu = self.create_menu()
        self.last_events = []

        pynotify.init(APPNAME)

    def create_indicator(self): pass

    def set_icon(self, icon): pass

    def create_menu(self):
        self.status_menu = gtk.MenuItem('Status: Unknown')
        self.status_details_menu = gtk.MenuItem('')
        item_events = gtk.MenuItem('Last events')
        item_events.connect('activate', self.last_events_cb)
        item_prefs = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        item_prefs.connect('activate', self.preferences_cb)
        item_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        item_quit.connect('activate', self.quit_cb)

        menu = gtk.Menu()
        menu.append(self.status_menu)
        menu.append(self.status_details_menu)
        menu.append(gtk.SeparatorMenuItem())
        menu.append(item_events)
        menu.append(gtk.SeparatorMenuItem())
        menu.append(item_prefs)
        menu.append(gtk.SeparatorMenuItem())
        menu.append(item_quit)
        return menu

    def main(self):
        gtk.timeout_add(500, self.update_status)
        gtk.timeout_add(500, self.update_events)
        gtk.main()

    def last_events_cb(self, *args, **kwargs):
        pass

    def preferences_cb(self, *args, **kwargs):
        pass

    def quit_cb(self, *args, **kwargs):
        gtk.main_quit()
        sys.exit()
        raise KeyboardInterrupt

    def update_status(self, *args, **kwargs):
        status = self.monitor.check_status()
        if status is not None:
            title = _('GitHub service status is %(status)s') % status['message']
            message = _('%(body)s\nOn %(created_on)s') % status['message']
            icon = get_icon_file_path(status['message']['status'])
            self.set_icon(icon)
            self.notify(title, message, icon)
            self.status_menu.get_child().set_text(title)
            self.status_details_menu.get_child().set_text(message)
        gtk.timeout_add(self.options.update_time * 1000, self.update_status)

    def update_events(self, *args, **kwargs):
        events = self.monitor.check_events()
        update_menu = False
        for e in reversed(events):
            update_menu = True
            title = _('%(created_at)s - %(type)s') % e
            data = {'actor': e['actor']['login'], 'object': e['repo']['name']}
            message = _('%(actor)s on %(object)s') % data
            icon = self.monitor.get_user_icon(e['actor'])
            self.notify(title, message, icon)
            self.last_events.insert(e)
        if update_menu:
            self.last_events = self.last_events[:5]
        gtk.timeout_add(5 * 60 * 1000, self.update_events)

    def notify(self, title, message, icon):
        logger.debug('%s - %s' % (title, message.replace('\n', ' ')))
        n = pynotify.Notification(title, message, icon)
        n.show()


class GitHubAppIndicator(GitHubApplet):
    def create_indicator(self):
        icon_file = get_icon_file_path('unknown')
        logger.debug(_('Creating appindicator with default icon %s') % icon_file)
        ind = appindicator.Indicator(APPNAME, icon_file,
                                     appindicator.CATEGORY_APPLICATION_STATUS)
        ind.set_status(appindicator.STATUS_ACTIVE)
        return ind

    def create_menu(self):
        menu = super(GitHubAppIndicator, self).create_menu()
        self.tray.set_menu(menu)
        menu.show_all()
        return menu

    def set_icon(self, icon):
        logger.debug(_('Setting icon from file: %s') % icon)
        self.tray.set_icon(icon)


class GitHubStatusIcon(GitHubApplet):
    def create_indicator(self):
        icon_file = get_icon_file_path('unknown')
        logger.debug(_('Creating StatusIcon from file (%s)') % icon_file)
        icon = gtk.status_icon_new_from_file(icon_file)
        if not icon.is_embedded():
            logging.error(_('Notification area not found for Status Icon version'))
        return icon

    def create_menu(self):
        menu = super(GitHubStatusIcon, self).create_menu()
        self.tray.connect('popup-menu', self.popup_menu_cb)
        return men

    def set_icon(self, icon):
        logger.debug(_('Setting icon from file: %s') % icon)
        self.tray.set_from_file(icon)

    def popup_menu_cb(self, widget, button, time):
        if button == 3:
            self.menu.show_all()
            self.menu.popup(None, None, None, 3, time)


def get_app(options):
    if options.status_icon:
        logger.debug(_('Using StatusIcon version'))
        app = GitHubStatusIcon(options)
    else:
        logger.debug(_('Using AppIndicator version'))
        app = GitHubAppIndicator(options)
    return app
