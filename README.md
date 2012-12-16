github-indicator
================

An indicator applet that reports github status, and show some notifications.

If started with -u and -p arguments (username and password), the app will try
to access your user's suscribed events and show them as notifications. So far
the password is not stored anyway and could be seen from a 'ps', so it's not
secure to use it in shared environments.


Install
-------

Run setup.py and optionally specify your app prefix:

./setup.py install -prefix ~/local


Hey, we also have a freenode channel: #github-indicator, feel free to join!
