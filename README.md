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

* `[binds]`
  * `shutdown=S`
  * `restart=R`
  * `suspend=U`
  * `hibernate=H`
  * `logout=L`
  * `cancel=Escape`
  * `settings=P`

# Packaging <a name="packaging"/></a>
The core files are all intended to be installed at `/usr/share/arcologout`

* `config/arcologout` is intended to be installed at `/usr/bin`
* `config/arcologout.conf` is intended to be installed at `/etc/arcologout.conf`
* `themes` is intended to be installed at `/usr/share/arcologout/themes`

---

# Backlog <a name="backlog"/></a>
* Decouple BetterScreenLock from arcologout
* The hot key for the options should always be visible to avoid bouncing and flickering
* Text is not being accounted for in the visual weight on the screen. We need to adjust everything up

# Changelog <a name="changelog"/></a>
