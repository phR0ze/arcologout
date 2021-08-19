#!/usr/bin/python3

# =====================================================
#        Authors Brad Heffernan and Erik Dubois
# =====================================================
import cairo
import gi
import shutil
import GUI
import os
import signal
import subprocess
import shutil
import threading
import configparser

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Gtk, GdkPixbuf, Gdk, Wnck, GLib, GdkX11  # noqa

# Derive the themes directory from where the script is located
working_dir = os.path.dirname(os.path.realpath(__file__))
themes_dir = os.path.join(working_dir, "themes/")

# Prefer the user's config file and seed from global if doesn't exist
global_config = "/etc/arcologout.conf"
dev_config = os.path.join(working_dir, "config/arcologout.conf")
home_dir = os.path.expanduser("~") 
config_dir = os.path.join(home_dir, ".config/arcologout")
config_file = os.path.join(config_dir, "arcologout.conf")

class TransparentWindow(Gtk.Window):
    cmd_logout = "pkill -SIGTERM -f lxsession"
    cmd_shutdown = "systemctl poweroff"
    cmd_restart = "systemctl reboot"
    cmd_suspend = "systemctl suspend"
    cmd_hibernate = "systemctl hibernate"
    wallpaper = os.path.join(themes_dir, "wallpaper.jpg")
    d_buttons = ['cancel',
                 'shutdown',
                 'restart',
                 'suspend',
                 'hibernate',
                 'logout']
    binds = {'restart': 'R',
             'shutdown': 'S',
             'suspend': 'U',
             'hibernate': 'H',
             'logout': 'L',
             'cancel': 'Escape'}
    theme = "white"
    hover = "#ffffff"
    icon = 64
    font = 11
    buttons = None
    active = False
    opacity = 0.8

    def __init__(self):
        super(TransparentWindow, self).__init__(type=Gtk.WindowType.TOPLEVEL, title="ArcoLogout")
        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_size_request(300, 220)
        self.connect('delete-event', self.on_close)
        self.connect('destroy', self.on_close)
        self.connect('draw', self.draw)
        self.connect("key-press-event", self.on_keypress)
        self.connect("window-state-event", self.on_window_state_event)
        self.set_decorated(False)

        self.width = 0
        screen = self.get_screen()

        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        get_config(self, Gdk, Gtk, config_file)

        if self.buttons is None or self.buttons == ['']:
            self.buttons = self.d_buttons

        self.fullscreen()
        self.set_app_paintable(True)
        self.present()

        GUI.GUI(self, Gtk, GdkPixbuf, themes_dir, os, Gdk, _get_themes)
        if not os.path.isfile("/tmp/arcologout.lock"):
            with open("/tmp/arcologout.lock", "w") as f:
                f.write("")

    def on_mouse_in(self, widget, event, data):
        if data == self.binds.get('shutdown'):
            psh = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/shutdown_blur.svg'), self.icon, self.icon)
            self.imagesh.set_from_pixbuf(psh)
            self.shutdown_label.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Shutdown (" + data + ")</span>")
        elif data == self.binds.get('restart'):
            pr = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/restart_blur.svg'), self.icon, self.icon)
            self.imager.set_from_pixbuf(pr)
            self.reboot_label.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Reboot (" + data + ")</span>")
        elif data == self.binds.get('suspend'):
            ps = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/suspend_blur.svg'), self.icon, self.icon)
            self.images.set_from_pixbuf(ps)
            self.suspend_label.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Suspend (" + data + ")</span>")
        elif data == self.binds.get('logout'):
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/logout_blur.svg'), self.icon, self.icon)
            self.imagelo.set_from_pixbuf(plo)
            self.logout_label.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Logout (" + data + ")</span>")
        elif data == self.binds.get('cancel'):
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/cancel_blur.svg'), self.icon, self.icon)
            self.imagec.set_from_pixbuf(plo)
            self.cancel_label.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Cancel (" + data + ")</span>")
        elif data == self.binds.get('hibernate'):
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/hibernate_blur.svg'), self.icon, self.icon)
            self.imageh.set_from_pixbuf(plo)
            self.hibernate_label.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Hibernate (" + data + ")</span>")
        event.window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def on_mouse_out(self, widget, event, data):
        if not self.active:
            if data == self.binds.get('shutdown'):
                psh = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/shutdown.svg'), self.icon, self.icon)
                self.imagesh.set_from_pixbuf(psh)
                self.shutdown_label.set_markup("<span size=\"" + str(self.font) + "000\">Shutdown (" + data + ")</span>")
            elif data == self.binds.get('restart'):
                pr = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/restart.svg'), self.icon, self.icon)
                self.imager.set_from_pixbuf(pr)
                self.reboot_label.set_markup("<span size=\"" + str(self.font) + "000\">Reboot (" + data + ")</span>")
            elif data == self.binds.get('suspend'):
                ps = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/suspend.svg'), self.icon, self.icon)
                self.images.set_from_pixbuf(ps)
                self.suspend_label.set_markup("<span size=\"" + str(self.font) + "000\">Suspend (" + data + ")</span>")
            elif data == self.binds.get('logout'):
                plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/logout.svg'), self.icon, self.icon)
                self.imagelo.set_from_pixbuf(plo)
                self.logout_label.set_markup("<span size=\"" + str(self.font) + "000\">Logout (" + data + ")</span>")
            elif data == self.binds.get('cancel'):
                plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/cancel.svg'), self.icon, self.icon)
                self.imagec.set_from_pixbuf(plo)
                self.cancel_label.set_markup("<span size=\"" + str(self.font) + "000\">Cancel (" + data + ")</span>")
            elif data == self.binds.get('hibernate'):
                plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/hibernate.svg'), self.icon, self.icon)
                self.imageh.set_from_pixbuf(plo)
                self.hibernate_label.set_markup("<span size=\"" + str(self.font) + "000\">Hibernate (" + data + ")</span>")

    def on_click(self, widget, event, data):
        self.click_button(widget, data)

    def on_window_state_event(self, widget, ev):
        self.__is_fullscreen = bool(ev.new_window_state & Gdk.WindowState.FULLSCREEN)  # noqa

    def draw(self, widget, context):
        context.set_source_rgba(0, 0, 0, self.opacity)
        context.set_operator(cairo.OPERATOR_SOURCE)
        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)

    def on_keypress(self, widget=None, event=None, data=None):
        self.shortcut_keys = [self.binds.get('cancel'), self.binds.get('shutdown'), self.binds.get('restart'), self.binds.get('suspend'), self.binds.get('logout'), self.binds.get('hibernate')]

        for key in self.shortcut_keys:
            if event.keyval == Gdk.keyval_to_lower(Gdk.keyval_from_name(key)):
                self.click_button(widget, key)

    def click_button(self, widget, data=None):
        if (data == self.binds.get('logout')):
            os.unlink("/tmp/arcologout.lock")
            os.unlink("/tmp/arcologout.pid")
            self.__exec_cmd(self.cmd_logout)
            Gtk.main_quit()

        elif (data == self.binds.get('restart')):
            os.unlink("/tmp/arcologout.lock")
            os.unlink("/tmp/arcologout.pid")
            self.__exec_cmd(self.cmd_restart)
            Gtk.main_quit()

        elif (data == self.binds.get('shutdown')):
            os.unlink("/tmp/arcologout.lock")
            os.unlink("/tmp/arcologout.pid")
            self.__exec_cmd(self.cmd_shutdown)
            Gtk.main_quit()

        elif (data == self.binds.get('suspend')):
            os.unlink("/tmp/arcologout.lock")
            os.unlink("/tmp/arcologout.pid")
            self.__exec_cmd(self.cmd_suspend)
            Gtk.main_quit()

        elif (data == self.binds.get('hibernate')):
            os.unlink("/tmp/arcologout.lock")
            os.unlink("/tmp/arcologout.pid")
            self.__exec_cmd(self.cmd_hibernate)
            Gtk.main_quit()

        else:
            os.unlink("/tmp/arcologout.lock")
            os.unlink("/tmp/arcologout.pid")
            Gtk.main_quit()

    def modal_close(self, widget, signal):
        print(self.state)

    def __exec_cmd(self, cmdline):
        os.system(cmdline)

    def on_close(self, widget, data):
        os.unlink("/tmp/arcologout.lock")
        os.unlink("/tmp/arcologout.pid")            
        Gtk.main_quit()

    def message_box(self, message, title):
        md = Gtk.MessageDialog(parent=self,
                               message_type=Gtk.MessageType.INFO,
                               buttons=Gtk.ButtonsType.YES_NO,
                               text=title)
        md.format_secondary_markup(message)  # noqa

        result = md.run()
        md.destroy()

        if result in (Gtk.ResponseType.OK, Gtk.ResponseType.YES):
            return True
        else:
            return False

def ensure_config_exists():
    if not os.path.isfile(config_file):
        os.makedirs(config_dir, exist_ok=True)

        # Use the development if run from github project
        if not os.path.isfile(global_config):
            shutil.copy(dev_config, config_file)
        else:
            shutil.copy(global_config, config_file)

def _get_themes():
    y = [x for x in os.listdir(themes_dir) if os.path.isdir(os.path.join(themes_dir, x))]
    y.sort()
    return y

def get_config(self, Gdk, Gtk, config):
    try:
        self.parser = configparser.RawConfigParser()
        self.parser.read(config)

        # Set some safe defaults
        self.opacity = 60

        if self.parser.has_section("settings"):
            if self.parser.has_option("settings", "opacity"):
                self.opacity = int(self.parser.get("settings", "opacity"))/100
            if self.parser.has_option("settings", "buttons"):
                self.buttons = self.parser.get("settings", "buttons").split(",")
            if self.parser.has_option("settings", "icon_size"):
                self.icon = int(self.parser.get("settings", "icon_size"))
            if self.parser.has_option("settings", "font_size"):
                self.font = int(self.parser.get("settings", "font_size"))

        if self.parser.has_section("commands"):
            if self.parser.has_option("commands", "hibernate"):
                self.cmd_shutdown = str(self.parser.get("commands", "hibernate"))
            if self.parser.has_option("commands", "logout"):
                self.cmd_shutdown = str(self.parser.get("commands", "logout"))
            if self.parser.has_option("commands", "restart"):
                self.cmd_shutdown = str(self.parser.get("commands", "restart"))
            if self.parser.has_option("commands", "shutdown"):
                self.cmd_shutdown = str(self.parser.get("commands", "shutdown"))
            if self.parser.has_option("commands", "suspend"):
                self.cmd_shutdown = str(self.parser.get("commands", "suspend"))

        if self.parser.has_section("binds"):
            if self.parser.has_option("binds", "restart"):
                self.binds['restart'] = self.parser.get("binds", "restart").upper()
            if self.parser.has_option("binds", "shutdown"):
                self.binds['shutdown'] = self.parser.get("binds", "shutdown").upper()
            if self.parser.has_option("binds", "suspend"):
                self.binds['suspend'] = self.parser.get("binds", "suspend").upper()
            if self.parser.has_option("binds", "hibernate"):
                self.binds['hibernate'] = self.parser.get("binds", "hibernate").upper()
            if self.parser.has_option("binds", "logout"):
                self.binds['logout'] = self.parser.get("binds", "logout").upper()
            if self.parser.has_option("binds", "cancel"):
                self.binds['cancel'] = self.parser.get("binds", "cancel").upper()

        if self.parser.has_section("themes"):
            if self.parser.has_option("themes", "theme"):
                self.theme = self.parser.get("themes", "theme")

        if len(self.theme) > 1:
            style_provider = Gtk.CssProvider()
            style_provider.load_from_path(themes_dir + self.theme + '/theme.css')

            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
    except Exception as e:
        print(e)
        os.unlink(config_file)
        ensure_config_exists()

def button_active(self, data, GdkPixbuf):
    try:
        if data == self.binds['shutdown']:
            psh = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/shutdown_blur.svg'), self.icon, self.icon)
            self.imagesh.set_from_pixbuf(psh)
            self.shutdown_label.set_markup("<span foreground=\"white\">Shutdown</span>")
        elif data == self.binds['restart']:
            pr = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/restart_blur.svg'), self.icon, self.icon)
            self.imager.set_from_pixbuf(pr)
            self.reboot_label.set_markup("<span foreground=\"white\">Restart</span>")
        elif data == self.binds['suspend']:
            ps = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/suspend_blur.svg'), self.icon, self.icon)
            self.images.set_from_pixbuf(ps)
            self.suspend_label.set_markup("<span foreground=\"white\">Suspend</span>")
        elif data == self.binds['logout']:
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/logout_blur.svg'), self.icon, self.icon)
            self.imagelo.set_from_pixbuf(plo)
            self.logout_label.set_markup("<span foreground=\"white\">Logout</span>")
        elif data == self.binds['cancel']:
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/cancel_blur.svg'), self.icon, self.icon)
            self.imagec.set_from_pixbuf(plo)
            self.cancel_label.set_markup("<span foreground=\"white\">Cancel</span>")
        elif data == self.binds['hibernate']:
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/hibernate_blur.svg'), self.icon, self.icon)
            self.imageh.set_from_pixbuf(plo)
            self.hibernate_label.set_markup("<span foreground=\"white\">Hibernate</span>")
    except:
        pass

def button_toggled(self, data):
    self.Esh.set_sensitive(False)
    self.Er.set_sensitive(False)
    self.Es.set_sensitive(False)
    self.Elk.set_sensitive(False)
    self.El.set_sensitive(False)
    self.Ec.set_sensitive(False)
    self.Eh.set_sensitive(False)

    if data == self.binds['shutdown']:
        self.Esh.set_sensitive(True)
    elif data == self.binds['restart']:
        self.Er.set_sensitive(True)
    elif data == self.binds['suspend']:
        self.Es.set_sensitive(True)
    elif data == self.binds['logout']:
        self.El.set_sensitive(True)
    elif data == self.binds['cancel']:
        self.Ec.set_sensitive(True)
    elif data == self.binds['hibernate']:
        self.Eh.set_sensitive(True)

def file_check(file):
    if os.path.isfile(file):
        return True

def signal_handler(sig, frame):
    print('\narcologout is Closing.')
    os.unlink("/tmp/arcologout.lock")
    os.unlink("/tmp/arcologout.pid")
    Gtk.main_quit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if not os.path.isfile("/tmp/arcologout.lock"):
        with open("/tmp/arcologout.pid", "w") as f:
            f.write(str(os.getpid()))
            f.close()
        ensure_config_exists()

        w = TransparentWindow()
        w.show_all()
        Gtk.main()
    else:
        print("arcolinux-logout did not close properly. Remove /tmp/arcologout.lock with sudo.")
