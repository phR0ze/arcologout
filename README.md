# ArcoLogout

### Quick links
* [Usage](#usage)
  * [Configuration](#configuration)
* [Packaging](#packaging)
* [Backlog](#backlog)
* [Changelog](#changelog)

---

# Usage <a name="usage"/></a>

## Configuration <a name="configuration"/></a>
***arcologout*** can be configured with the global config at `/etc/arcologout.conf` or using the user
override at `~/.config/arcologout/arcologout`.

* `[settings]`
  * `opacity=80`
  * `icon_size=200`
  * `font_size=40`
  * `buttons` is a comma delimited list of buttons to show in the overlay. It supports `cancel`,
  `logout`, `restart`, `shutdown`, `suspend`, and `hibernate` however the default config drops
  `cancel` as escape to cancel is automatic for most people.

* `[themes]`
  * `theme=white`

* `[commands]`
  * `shutdown=systemctl poweroff`
  * `hibernate=systemctl hibernate`
  * `logout=pkill -SIGTERM -f lxsession`
  * `restart=systemctl reboot`
  * `shutdown=systemctl poweroff`
  * `suspend=systemctl suspend`

* `[binds]` each command can have a hot key assigned to it. the hot key will always be lower a single
lower case character
  * `shutdown=S`
  * `restart=R`
  * `suspend=U`
  * `hibernate=H`
  * `logout=L`

# Packaging <a name="packaging"/></a>
[PKGBUILD suitable for the AUR](https://github.com/phR0ze/cyberlinux-aur/tree/master/arcologout)

---

# Backlog <a name="backlog"/></a>
* Text is not being accounted for in the visual weight on the screen. We need to adjust everything up

# Changelog <a name="changelog"/></a>
* The hot key for the options should always be visible to avoid bouncing and flickering
* Removed lock, cancel, settings to clean up the display
* Decouple BetterScreenLock from arcologout
