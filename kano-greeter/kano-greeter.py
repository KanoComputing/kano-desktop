#!/usr/bin/env python

# kano-greeter.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import LightDM
import os

from kano.logging import logger
from kano.gtk3.apply_styles import apply_common_to_screen, \
    apply_styling_to_screen
from kano.gtk3.top_bar import TopBar
from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.application_window import ApplicationWindow
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.buttons import OrangeButton


class GreeterWindow(ApplicationWindow):
    WIDTH = 400
    HEIGHT = -1

    def __init__(self):
        apply_common_to_screen()

        ApplicationWindow.__init__(self, 'Login', self.WIDTH, self.HEIGHT)
        self.connect("delete-event", Gtk.main_quit)

        self.grid = Gtk.Grid()
        self.set_main_widget(self.grid)

        self.grid.set_column_spacing(30)
        self.grid.set_row_spacing(30)

        self.top_bar = TopBar('Login')
        self._remove_top_bar_buttons()
        self.top_bar.set_size_request(self.WIDTH, -1)
        self.grid.attach(self.top_bar, 0, 0, 3, 1)

        self.shutdown_btn = OrangeButton('Shutdown')
        self.shutdown_btn.connect('clicked', self.shutdown)
        align = Gtk.Alignment(xalign=1.0,
                              xscale=0.0)
        align.add(self.shutdown_btn)
        self.grid.attach(align, 1, 2, 1, 1)

        self.grid.attach(Gtk.Label(), 0, 3, 3, 1)

        self.top_bar.set_prev_callback(self._back_cb)

        self.user_list = UserList()

        self.go_to_users()

        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _remove_top_bar_buttons(self):
        self.top_bar.box.remove(self.top_bar.close_button)
        self.top_bar.box.remove(self.top_bar.next_button)

    def set_main(self, wdg):
        child = self.grid.get_child_at(1, 1)
        if child:
            self.grid.remove(child)

        self.grid.attach(wdg, 1, 1, 1, 1)
        self.show_all()

    def go_to_users(self):
        self.set_main(self.user_list)
        self.top_bar.disable_prev()

    def go_to_password(self, user):
        password_view = PasswordView(user)
        self.set_main(password_view)
        self.top_bar.enable_prev()

    def _back_cb(self, event, button):
        self.go_to_users()

    def shutdown(self, *_):
        confirm = KanoDialog(title_text='Are you sure you want to shut down?',
                             button_dict={
                                 'OK': {'return_value': True},
                                 'CANCEL': {'return_value': False}
                             })
        confirm.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        if confirm.run():
            LightDM.shutdown()


class UserList(Gtk.ScrolledWindow):
    HEIGHT = 250
    WIDTH = 250

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.set_size_request(self.WIDTH, self.HEIGHT)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.set_spacing(10)
        self.add(self.box)

        title = Heading('Select Account', 'Log in to which account?')
        self.box.pack_start(title.container, False, False, 0)

        self._populate()

    def _populate(self):
        # Populate list
        user_list = LightDM.UserList()
        for user in user_list.get_users():
            logger.debug('adding user {}'.format(user.get_name()))
            self.add_item(user.get_name())

    def add_item(self, username):
        user = User(username)
        self.box.pack_start(user, False, False, 0)


class User(Gtk.EventBox):
    HEIGHT = 50

    def __init__(self, username):
        Gtk.EventBox.__init__(self)
        self.set_size_request(-1, self.HEIGHT)

        self.username = username

        self.get_style_context().add_class('user')

        label = Gtk.Label(username.title())
        self.add(label)

        self.connect('button-release-event', self._user_select_cb)
        self.connect('enter-notify-event', self._hover_cb)
        self.connect('leave-notify-event', self._unhover_cb)

    def _user_select_cb(self, button, event):
        logger.debug('user {} selected'.format(self.username))

        win = self.get_toplevel()
        win.go_to_password(self.username)

    def _hover_cb(self, widget, event):
        self.get_style_context().add_class('hover')

    def _unhover_cb(self, widget, event):
        self.get_style_context().remove_class('hover')


class PasswordView(Gtk.Grid):
    greeter = LightDM.Greeter()

    def __init__(self, user):
        Gtk.Grid.__init__(self)

        self.get_style_context().add_class('password')
        self.set_row_spacing(10)

        self._reset_greeter()

        self.user = user
        title = Heading('Enter your password',
                        'If you haven\'t changed your password, use \'Kano\'')
        self.attach(title.container, 0, 0, 1, 1)
        self.password = Gtk.Entry()
        self.password.set_visibility(False)
        self.password.set_alignment(0.5)
        self.password.connect('activate', self._login_cb)
        self.attach(self.password, 0, 1, 1, 1)

        self.login_btn = KanoButton('Login')
        self.login_btn.connect('button-release-event', self._login_cb)
        self.attach(self.login_btn, 0, 2, 1, 1)

    def _reset_greeter(self):
        PasswordView.greeter = PasswordView.greeter.new()
        PasswordView.greeter.connect_sync()

        # connect signal handlers to LightDM
        PasswordView.greeter.connect('show-prompt', self._send_password_cb)
        PasswordView.greeter.connect('authentication-complete',
                                     self._authentication_complete_cb)
        PasswordView.greeter.connect('show-message', self._auth_error_cb)

    def _login_cb(self, event=None, button=None):
        logger.debug('Sending username to LightDM')

        self.login_btn.start_spinner()
        PasswordView.greeter.authenticate(self.user)

        if PasswordView.greeter.get_is_authenticated():
            logger.debug('User is already authenticated, starting session')
            start_session()

    def _send_password_cb(self, _greeter, text, prompt_type):
        logger.debug('Need to show prompt: {}'.format(text))
        if _greeter.get_in_authentication():
            logger.debug('Sending password to LightDM')
            _greeter.respond(self.password.get_text())

    def _authentication_complete_cb(self, _greeter):
        logger.debug('Authentication process is complete')

        if not _greeter.get_is_authenticated():
            logger.warn('Could not authenticate user {}'.format(self.user))
            self._auth_error_cb('Incorrect password (The default is Kano)')

            return

        logger.info(
            'The user {} is authenticated. Starting LightDM X Session'
            .format(self.user))

        if not _greeter.start_session_sync('lightdm-xsession'):
            logger.error('Failed to start session')
        else:
            logger.info('Login failed')

    def _auth_error_cb(self, text, message_type=None):
        logger.info('There was an error logging in: {}'.format(text))

        win = self.get_toplevel()
        win.go_to_users()

        error = KanoDialog(title_text='Error Logging In',
                           description_text=text,
                           parent_window=self.get_toplevel())
        error.dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        error.run()


if __name__ == '__main__':
    try:
        # Refresh the wallpaper
        os.system('kdesk -w')

        apply_styling_to_screen(
            '/usr/share/kano-desktop/kano-greeter/kano-greeter.css')

        WIN = GreeterWindow()
        WIN.show_all()

        Gtk.main()
    except Exception as e:
        logger.error(e)
