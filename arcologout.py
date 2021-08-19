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
    cmd_shutdown = "systemctl poweroff"
    cmd_restart = "systemctl reboot"
    cmd_suspend = "systemctl suspend"
    cmd_hibernate = "systemctl hibernate"
    cmd_lock = 'betterlockscreen -l dim -- --time-str="%H:%M"'
    wallpaper = os.path.join(themes_dir, "wallpaper.jpg")
    d_buttons = ['cancel',
                 'shutdown',
                 'restart',
                 'suspend',
                 'hibernate',
                 'lock',
                 'logout']
    binds = {'lock': 'K',
             'restart': 'R',
             'shutdown': 'S',
             'suspend': 'U',
             'hibernate': 'H',
             'logout': 'L',
             'cancel': 'Escape',
             'settings': 'P'}
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

        # self.monitor = 0

        # s = Gdk.Screen.get_default()
        # self.width = s.width()
        # height = s.height()

        # screens = Gdk.Display.get_default()
        # s = screens.get_n_monitors()

        self.width = 0
        # for x in range(s):
        #     sc = screens.get_monitor(x)
        #     rec = sc.get_geometry()
        #     self.width += rec.width

        screen = self.get_screen()

        # monitor = screens.get_monitor(0)
        # rect = monitor.get_geometry()

        # self.single_width = rect.width
        # height = rect.height

        # self.move(0, 0)
        # self.resize(self.width, height)

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


    def on_save_clicked(self, widget):
        try:
            with open(config_file, "r") as f:
                lines = f.readlines()
                f.close()

            pos_opacity = _get_position(lines, "opacity")
            pos_size = _get_position(lines, "icon_size")
            pos_theme = _get_position(lines, "theme=")
            pos_font = _get_position(lines, "font_size=")

            lines[pos_opacity] = "opacity=" + str(int(self.hscale.get_value())) + "\n"
            lines[pos_size] = "icon_size=" + str(int(self.icons.get_value())) + "\n"
            lines[pos_theme] = "theme=" + self.themes.get_active_text() + "\n"
            lines[pos_font] = "font_size=" + str(int(self.fonts.get_value())) + "\n"

            with open(config_file, "w") as f:
                f.writelines(lines)
                f.close()
            self.popover.popdown()
        except Exception as e:
            os.unlink(config_file)
            ensure_config_exists()
            with open(config_file, "r") as f:
                lines = f.readlines()
                f.close()

            pos_opacity = _get_position(lines, "opacity")
            pos_size = _get_position(lines, "icon_size")
            pos_theme = _get_position(lines, "theme=")
            pos_font = _get_position(lines, "font_size=")

            lines[pos_opacity] = "opacity=" + str(int(self.hscale.get_value())) + "\n"
            lines[pos_size] = "icon_size=" + str(int(self.icons.get_value())) + "\n"
            lines[pos_theme] = "theme=" + self.themes.get_active_text() + "\n"
            lines[pos_font] = "font_size=" + str(int(self.fonts.get_value())) + "\n"

            with open(config_file, "w") as f:
                f.writelines(lines)
                f.close()
            self.popover.popdown()


    def on_mouse_in(self, widget, event, data):
        if data == self.binds.get('shutdown'):
            psh = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/shutdown_blur.svg'), self.icon, self.icon)
            self.imagesh.set_from_pixbuf(psh)
            self.lbl1.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Shutdown (S)</span>")
        elif data == self.binds.get('restart'):
            pr = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/restart_blur.svg'), self.icon, self.icon)
            self.imager.set_from_pixbuf(pr)
            self.lbl2.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Reboot (R)</span>")
        elif data == self.binds.get('suspend'):
            ps = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/suspend_blur.svg'), self.icon, self.icon)
            self.images.set_from_pixbuf(ps)
            self.lbl3.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Suspend (U)</span>")
        elif data == self.binds.get('lock'):
            plk = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/lock_blur.svg'), self.icon, self.icon)
            self.imagelk.set_from_pixbuf(plk)
            self.lbl4.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Lock (K)</span>")
        elif data == self.binds.get('logout'):
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/logout_blur.svg'), self.icon, self.icon)
            self.imagelo.set_from_pixbuf(plo)
            self.lbl5.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Logout (L)</span>")
        elif data == self.binds.get('cancel'):
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/cancel_blur.svg'), self.icon, self.icon)
            self.imagec.set_from_pixbuf(plo)
            self.lbl6.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Cancel (ESC)</span>")
        elif data == self.binds.get('hibernate'):
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/hibernate_blur.svg'), self.icon, self.icon)
            self.imageh.set_from_pixbuf(plo)
            self.lbl7.set_markup("<span size=\"" + str(self.font) + "000\" foreground=\"" + self.hover + "\">Hibernate (H)</span>")
        elif data == self.binds.get('settings'):
            pset = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, 'configure_blur.svg'), 48, 48)
            self.imageset.set_from_pixbuf(pset)
        elif data == 'light':
            pset = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, 'light_blur.svg'), 48, 48)
            self.imagelig.set_from_pixbuf(pset)
        event.window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def on_mouse_out(self, widget, event, data):
        if not self.active:
            if data == self.binds.get('shutdown'):
                psh = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/shutdown.svg'), self.icon, self.icon)
                self.imagesh.set_from_pixbuf(psh)
                self.lbl1.set_markup("<span size=\"" + str(self.font) + "000\">Shutdown</span>")
            elif data == self.binds.get('restart'):
                pr = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/restart.svg'), self.icon, self.icon)
                self.imager.set_from_pixbuf(pr)
                self.lbl2.set_markup("<span size=\"" + str(self.font) + "000\">Reboot</span>")
            elif data == self.binds.get('suspend'):
                ps = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/suspend.svg'), self.icon, self.icon)
                self.images.set_from_pixbuf(ps)
                self.lbl3.set_markup("<span size=\"" + str(self.font) + "000\">Suspend</span>")
            elif data == self.binds.get('lock'):
                plk = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/lock.svg'), self.icon, self.icon)
                self.imagelk.set_from_pixbuf(plk)
                self.lbl4.set_markup("<span size=\"" + str(self.font) + "000\">Lock</span>")
            elif data == self.binds.get('logout'):
                plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/logout.svg'), self.icon, self.icon)
                self.imagelo.set_from_pixbuf(plo)
                self.lbl5.set_markup("<span size=\"" + str(self.font) + "000\">Logout</span>")
            elif data == self.binds.get('cancel'):
                plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/cancel.svg'), self.icon, self.icon)
                self.imagec.set_from_pixbuf(plo)
                self.lbl6.set_markup("<span size=\"" + str(self.font) + "000\">Cancel</span>")
            elif data == self.binds.get('hibernate'):
                plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, self.theme + '/hibernate.svg'), self.icon, self.icon)
                self.imageh.set_from_pixbuf(plo)
                self.lbl7.set_markup("<span size=\"" + str(self.font) + "000\">Hibernate</span>")
            elif data == self.binds.get('settings'):
                pset = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, 'configure.svg'), 48, 48)
                self.imageset.set_from_pixbuf(pset)
            elif data == 'light':
                pset = GdkPixbuf.Pixbuf().new_from_file_at_size(
                    os.path.join(themes_dir, 'light.svg'), 48, 48)
                self.imagelig.set_from_pixbuf(pset)

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
        self.shortcut_keys = [self.binds.get('cancel'), self.binds.get('shutdown'), self.binds.get('restart'), self.binds.get('suspend'), self.binds.get('logout'), self.binds.get('lock'), self.binds.get('hibernate'), self.binds.get('settings')]

        for key in self.shortcut_keys:
            if event.keyval == Gdk.keyval_to_lower(Gdk.keyval_from_name(key)):
                self.click_button(widget, key)

    def click_button(self, widget, data=None):
        if not data == self.binds.get('settings') and not data == "light":
            self.active = True
            button_toggled(self, data)
            button_active(self, data, GdkPixbuf)

        if (data == self.binds.get('logout')):
            command = _get_logout()
            os.unlink("/tmp/arcologout.lock")
            os.unlink("/tmp/arcologout.pid")
            self.__exec_cmd(command)
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

        elif (data == self.binds.get('lock')):
            if not os.path.isdir(home_dir + "/.cache/betterlockscreen"):
                if os.path.isfile(self.wallpaper):
                    self.lbl_stat.set_markup("<span size=\"x-large\"><b>Caching lockscreen images for a faster locking next time</b></span>")  # noqa
                    t = threading.Thread(target=cache_bl,
                                         args=(self, GLib, Gtk,))
                    t.daemon = True
                    t.start()
                else:
                    self.lbl_stat.set_markup("<span size=\"x-large\"><b>Choose a wallpaper with arcolinux-betterlockscreen</b></span>")  # noqa
                    self.Ec.set_sensitive(True)
                    self.active = False
            else:
                os.unlink("/tmp/arcologout.lock")
                self.__exec_cmd(self.cmd_lock)
                Gtk.main_quit()
        elif (data == self.binds.get('settings')):
            self.themes.grab_focus()
            self.popover.set_relative_to(self.Eset)
            self.popover.show_all()
            self.popover.popup()
        elif (data == 'light'):
            self.popover2.set_relative_to(self.Elig)
            self.popover2.show_all()
            self.popover2.popup()
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

def _get_position(lists, value):
    data = [string for string in lists if value in string]
    position = lists.index(data[0])
    return position

def _get_themes():
    y = [x for x in os.listdir(themes_dir) if os.path.isdir(os.path.join(themes_dir, x))]
    y.sort()
    return y

def cache_bl(self, GLib, Gtk):
    if os.path.isfile("/usr/bin/betterlockscreen"):
        with subprocess.Popen(["betterlockscreen", "-u", self.wallpaper], shell=False, stdout=subprocess.PIPE) as f:
            for line in f.stdout:
                GLib.idle_add(self.lbl_stat.set_markup, "<span size=\"x-large\"><b>" + line.decode() + "</b></span>")

        GLib.idle_add(self.lbl_stat.set_text, "")
        os.unlink("/tmp/arcologout.lock")
        os.system(self.cmd_lock)
        Gtk.main_quit()
    else:
        print("not installed betterlockscreen.")


def get_config(self, Gdk, Gtk, config):
    try:
        self.parser = configparser.RawConfigParser()
        self.parser.read(config)

        # Set some safe defaults
        self.opacity = 60

        # Check if we're using HAL, and init it as required.
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
            if self.parser.has_option("commands", "lock"):
                self.cmd_lock = str(self.parser.get("commands", "lock"))

        if self.parser.has_section("binds"):
            if self.parser.has_option("binds", "lock"):
                self.binds['lock'] = self.parser.get("binds", "lock").capitalize()
            if self.parser.has_option("binds", "restart"):
                self.binds['restart'] = self.parser.get("binds", "restart").capitalize()
            if self.parser.has_option("binds", "shutdown"):
                self.binds['shutdown'] = self.parser.get("binds", "shutdown").capitalize()
            if self.parser.has_option("binds", "suspend"):
                self.binds['suspend'] = self.parser.get("binds", "suspend").capitalize()
            if self.parser.has_option("binds", "hibernate"):
                self.binds['hibernate'] = self.parser.get("binds", "hibernate").capitalize()
            if self.parser.has_option("binds", "logout"):
                self.binds['logout'] = self.parser.get("binds", "logout").capitalize()
            if self.parser.has_option("binds", "cancel"):
                self.binds['cancel'] = self.parser.get("binds", "cancel").capitalize()
            if self.parser.has_option("binds", "settings"):
                self.binds['settings'] = self.parser.get("binds", "settings").capitalize()

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

def _get_logout():
    out = subprocess.run(["sh", "-c", "env | grep DESKTOP_SESSION"],
                         shell=False, stdout=subprocess.PIPE)
    desktop = out.stdout.decode().split("=")[1].strip()

    print("Your desktop is " + desktop)
    if desktop in ("herbstluftwm", "/usr/share/xsessions/herbstluftwm"):
        return "herbstclient quit"
    elif desktop in ("bspwm", "/usr/share/xsessions/bspwm"):
        return "pkill bspwm"
    elif desktop in ("jwm", "/usr/share/xsessions/jwm"):
        return "pkill jwm"
    elif desktop in ("openbox", "/usr/share/xsessions/openbox"):
        return "pkill openbox"
    elif desktop in ("awesome", "/usr/share/xsessions/awesome"):
        return "pkill awesome"
    elif desktop in ("qtile", "/usr/share/xsessions/qtile"):
        return "pkill qtile"
    elif desktop in ("xmonad", "/usr/share/xsessions/xmonad"):
        return "pkill xmonad"
    #for lxdm
    elif desktop in ("Xmonad", "/usr/share/xsessions/xmonad"):
        return "pkill xmonad"
    elif desktop in ("dwm", "/usr/share/xsessions/dwm"):
        return "pkill dwm"
    elif desktop in ("i3", "/usr/share/xsessions/i3"):
        return "pkill i3"
    elif desktop in ("i3-with-shmlog", "/usr/share/xsessions/i3-with-shmlog"):
        return "pkill i3-with-shmlog"
    elif desktop in ("lxqt", "/usr/share/xsessions/lxqt"):
        return "pkill lxqt"
    elif desktop in ("spectrwm", "/usr/share/xsessions/spectrwm"):
        return "pkill spectrwm"
    elif desktop in ("xfce", "/usr/share/xsessions/xfce"):
        return "xfce4-session-logout -f -l"
    elif desktop in ("sway", "/usr/share/xsessions/sway"):
        return "pkill sway"
    elif desktop in ("icewm", "/usr/share/xsessions/icewm"):
        return "pkill icewm"
    elif desktop in ("icewm-session", "/usr/share/xsessions/icewm-session"):
        return "pkill icewm-session"
    elif desktop in ("cwm", "/usr/share/xsessions/cwm"):
        return "pkill cwm"
    elif desktop in ("fvwm3", "/usr/share/xsessions/fvwm3"):
        return "pkill fvwm3"
    elif desktop in ("stumpwm", "/usr/share/xsessions/stumpwm"):
        return "pkill stumpwm"
    elif desktop in ("leftwm", "/usr/share/xsessions/leftwm"):
        return "pkill leftwm"
    elif desktop in ("gnome", "/usr/share/xsessions/gnome"):
        return "gnome-session-quit --logout --no-prompt"
    elif desktop in ("gnome-xorg", "/usr/share/xsessions/gnome-xorg"):
        return "gnome-session-quit --logout --no-prompt"
    elif desktop in ("gnome-classic", "/usr/share/xsessions/gnome-classic"):
        return "gnome-session-quit --logout --no-prompt"
    return None

def button_active(self, data, GdkPixbuf):
    try:
        if data == self.binds['shutdown']:
            psh = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/shutdown_blur.svg'), self.icon, self.icon)
            self.imagesh.set_from_pixbuf(psh)
            self.lbl1.set_markup("<span foreground=\"white\">Shutdown</span>")
        elif data == self.binds['restart']:
            pr = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/restart_blur.svg'), self.icon, self.icon)
            self.imager.set_from_pixbuf(pr)
            self.lbl2.set_markup("<span foreground=\"white\">Restart</span>")
        elif data == self.binds['suspend']:
            ps = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/suspend_blur.svg'), self.icon, self.icon)
            self.images.set_from_pixbuf(ps)
            self.lbl3.set_markup("<span foreground=\"white\">Suspend</span>")
        elif data == self.binds['lock']:
            plk = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/lock_blur.svg'), self.icon, self.icon)
            self.imagelk.set_from_pixbuf(plk)
            self.lbl4.set_markup("<span foreground=\"white\">Lock</span>")
        elif data == self.binds['logout']:
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/logout_blur.svg'), self.icon, self.icon)
            self.imagelo.set_from_pixbuf(plo)
            self.lbl5.set_markup("<span foreground=\"white\">Logout</span>")
        elif data == self.binds['cancel']:
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/cancel_blur.svg'), self.icon, self.icon)
            self.imagec.set_from_pixbuf(plo)
            self.lbl6.set_markup("<span foreground=\"white\">Cancel</span>")
        elif data == self.binds['hibernate']:
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/hibernate_blur.svg'), self.icon, self.icon)
            self.imageh.set_from_pixbuf(plo)
            self.lbl7.set_markup("<span foreground=\"white\">Hibernate</span>")
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
    elif data == self.binds['lock']:
        self.Elk.set_sensitive(True)
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
