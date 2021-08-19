# =====================================================
#        Authors Brad Heffernan and Erik Dubois
# =====================================================

def GUI(self, Gtk, GdkPixbuf, themes_dir, os, Gdk, get_themes):
    mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    mainbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lblbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    lbl = Gtk.Label(label="")
    self.lbl_stat = Gtk.Label()
    lblbox.pack_start(lbl, True, False, 0)
    lblbox.pack_start(self.lbl_stat, True, False, 0)

    overlayFrame = Gtk.Overlay()
    overlayFrame.add(lblbox)
    overlayFrame.add_overlay(mainbox)

    self.add(overlayFrame)

    self.Esh = Gtk.EventBox()
    self.Esh.connect("button_press_event", self.on_click, self.binds['shutdown'])
    self.Esh.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
    self.Esh.connect("enter-notify-event", self.on_mouse_in, self.binds['shutdown'])
    self.Esh.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
    self.Esh.connect("leave-notify-event", self.on_mouse_out, self.binds['shutdown'])

    self.Er = Gtk.EventBox()
    self.Er.connect("button_press_event", self.on_click, self.binds['restart'])
    self.Er.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
    self.Er.connect("enter-notify-event", self.on_mouse_in, self.binds['restart'])
    self.Er.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
    self.Er.connect("leave-notify-event", self.on_mouse_out, self.binds['restart'])

    self.Es = Gtk.EventBox()
    self.Es.connect("button_press_event", self.on_click, self.binds['suspend'])
    self.Es.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
    self.Es.connect("enter-notify-event", self.on_mouse_in, self.binds['suspend'])
    self.Es.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
    self.Es.connect("leave-notify-event", self.on_mouse_out, self.binds['suspend'])

    self.El = Gtk.EventBox()
    self.El.connect("button_press_event", self.on_click, self.binds['logout'])
    self.El.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
    self.El.connect("enter-notify-event", self.on_mouse_in, self.binds['logout'])
    self.El.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
    self.El.connect("leave-notify-event", self.on_mouse_out, self.binds['logout'])

    self.Ec = Gtk.EventBox()
    self.Ec.connect("button_press_event", self.on_click, self.binds['cancel'])
    self.Ec.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
    self.Ec.connect("enter-notify-event", self.on_mouse_in, self.binds['cancel'])
    self.Ec.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
    self.Ec.connect("leave-notify-event", self.on_mouse_out, self.binds['cancel'])

    self.Eh = Gtk.EventBox()
    self.Eh.connect("button_press_event", self.on_click, self.binds['hibernate'])
    self.Eh.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
    self.Eh.connect("enter-notify-event", self.on_mouse_in, self.binds['hibernate'])
    self.Eh.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
    self.Eh.connect("leave-notify-event", self.on_mouse_out, self.binds['hibernate'])

    for button in self.buttons:
        if button == "shutdown":
            psh = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/shutdown.svg'), self.icon, self.icon)
            self.imagesh = Gtk.Image().new_from_pixbuf(psh)
            self.Esh.add(self.imagesh)
        if button == "cancel":
            pc = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/cancel.svg'), self.icon, self.icon)
            self.imagec = Gtk.Image().new_from_pixbuf(pc)
            self.Ec.add(self.imagec)
        if button == "restart":
            pr = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/restart.svg'), self.icon, self.icon)
            self.imager = Gtk.Image().new_from_pixbuf(pr)
            self.Er.add(self.imager)
        if button == "suspend":
            ps = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/suspend.svg'), self.icon, self.icon)
            self.images = Gtk.Image().new_from_pixbuf(ps)
            self.Es.add(self.images)
        if button == "logout":
            plo = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/logout.svg'), self.icon, self.icon)
            self.imagelo = Gtk.Image().new_from_pixbuf(plo)
            self.El.add(self.imagelo)
        if button == "hibernate":
            ph = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(themes_dir, self.theme + '/hibernate.svg'), self.icon, self.icon)
            self.imageh = Gtk.Image().new_from_pixbuf(ph)
            self.Eh.add(self.imageh)

    self.shutdown_label = Gtk.Label()
    self.shutdown_label.set_markup("<span size=\"" + str(self.font) + "000\">Shutdown (" + self.binds['shutdown'] + ")</span>")
    self.shutdown_label.set_name("lbl")
    self.reboot_label = Gtk.Label()
    self.reboot_label.set_markup("<span size=\"" + str(self.font) + "000\">Reboot (" + self.binds['restart'] + ")</span>")
    self.reboot_label.set_name("lbl")
    self.suspend_label = Gtk.Label()
    self.suspend_label.set_markup("<span size=\"" + str(self.font) + "000\">Suspend (" + self.binds['suspend'] + ")</span>")
    self.suspend_label.set_name("lbl")
    self.logout_label = Gtk.Label()
    self.logout_label.set_markup("<span size=\"" + str(self.font) + "000\">Logout (" + self.binds['logout'] + ")</span>")
    self.logout_label.set_name("lbl")
    self.cancel_label = Gtk.Label()
    self.cancel_label.set_markup("<span size=\"" + str(self.font) + "000\">Cancel (" + self.binds['cancel'] + ")</span>")
    self.cancel_label.set_name("lbl")
    self.hibernate_label = Gtk.Label()
    self.hibernate_label.set_markup("<span size=\"" + str(self.font) + "000\">Hibernate (" + self.binds['hibernate'] + ")</span>")
    self.hibernate_label.set_name("lbl")

    shutdown_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    reboot_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    suspend_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    logout_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    cancel_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    hibernate_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    hbox17 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)

    shutdown_box.pack_start(self.Esh, False, False, 0)
    shutdown_box.pack_start(self.shutdown_label, False, False, 0)
    reboot_box.pack_start(self.Er, False, False, 0)
    reboot_box.pack_start(self.reboot_label, False, False, 0)
    suspend_box.pack_start(self.Es, False, False, 0)
    suspend_box.pack_start(self.suspend_label, False, False, 0)
    logout_box.pack_start(self.El, False, False, 0)
    logout_box.pack_start(self.logout_label, False, False, 0)
    cancel_box.pack_start(self.Ec, False, False, 0)
    cancel_box.pack_start(self.cancel_label, False, False, 0)
    hibernate_box.pack_start(self.Eh, False, False, 0)
    hibernate_box.pack_start(self.hibernate_label, False, False, 0)

    for button in self.buttons:
        if button == "shutdown":
            hbox1.pack_start(shutdown_box, False, False, 20)
        if button == "cancel":
            hbox1.pack_start(cancel_box, False, False, 20)
        if button == "restart":
            hbox1.pack_start(reboot_box, False, False, 20)
        if button == "suspend":
            hbox1.pack_start(suspend_box, False, False, 20)
        if button == "logout":
            hbox1.pack_start(logout_box, False, False, 20)
        if button == "hibernate":
            hbox1.pack_start(hibernate_box, False, False, 20)

    mainbox2.pack_start(hbox1, True, False, 0)
    mainbox.pack_start(hbox17, False, False, 0)
    mainbox.pack_start(mainbox2, True, False, 0)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
    hbox4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
    hbox5 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
    hbox6 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

    vbox.pack_start(hbox, False, True, 10)
    vbox.pack_start(hbox4, False, True, 10)
    vbox.pack_start(hbox6, False, True, 10)
    vbox.pack_start(hbox5, False, True, 10)
