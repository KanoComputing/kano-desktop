# Kano Desktop

*Kano Desktop* is a package that draws together many packages to provide
an integrated desktop experience, built on Raspbian's LXDE. Most of the actual code resides in its
dependencies; what is provided directly are configuration files and integration scripts.


## *kano-uixinit*

This script is run by the LXDE autostart file and performs a number of functions:

 * On first login:
  * Runs [*kano-tutorial*](https://github.com/KanoComputing/kano-init-flow/tree/master/kano_tutorial) to
introduce the user to their computer 
  * Runs [*kano-init-flow*](https://github.com/KanoComputing/kano-init-flow) to and prompt them to make configuration choices via [*kano-settings*](https://github.com/KanoComputing/kano-settings)
  * Shows an introductory [video](https://github.com/KanoComputing/kano-video-files/blob/master/videos/os_intro.mp4)
  * Account setup using [*kano-init*](https://github.com/KanoComputing/kano-init) and [*kano-login*](https://github.com/KanoComputing/kano-profile/blob/master/bin/kano-login)
 
 * On each login, sets up the desktop.
 * Acts as a point at which other packages which need notification of login are called, eg [*kano-init*](https://github.com/KanoComputing/kano-init) and [*kano-updater*](https://github.com/KanoComputing/kano-updater)
 * Syncs state for apps integrated with Kano World via [*kano-sync*](https://github.com/KanoComputing/kano-profile/blob/master/bin/kano-sync)
 * Configures: screensaver, audio  (alsa-utils), keyboard, mouse, and kano-vnc
 * Starts lxpanel, kano-mount-trigger, kdesk, and kano-feedback-widget

## Configuration files

This repo contains configuration files for
  * [LXDE](https://github.com/lxde/lxsession/blob/master/data/desktop.conf.exampledcon)
  * [lxpanel](http://wiki.lxde.org/en/LXPanel#Main_Config_File)
  * [openbox](http://openbox.org/wiki/Help:Configuration)
  * [chromium](https://www.chromium.org/administrators/configuring-other-preferences)
  * [gtk file chooser](https://developer.gnome.org/gtk2/stable/GtkFileChooser.html)
  * libfm (automatically generated, should be changed via preferences dialog)
  * pcmanfm (automatically generated, should be changed via preferences dialog)
  * rxvt - see `man rxvt`
  * lxterminal
  * dconf (a binary file which is edited using gconftool-2)

Plus a default `.bashrc`


## Keyboard integration

Kano supply a custom keyboard; support for which is in this repo.
 * kano-uixinit detects the keyboard and starts xbindkeys, with one of two configurations to be found in `config/keyboard`.
 * The script bin/kano-screenshot-hotkey is triggered from Ctrl-Alt-Equal on the KANO keyboard or Control-Print on normal keyboard. This causes a screenshot to be taken and placed in `~/Screenshots/`
 * Save, Load, Make and Share keys on the Kano keyboard trigger certain actions via [*kano-signal*](https://github.com/KanoComputing/kano-toolset/blob/master/bin/kano-signal)
 * Volume up and down keys via [*kano-volume*](https://github.com/KanoComputing/kano-toolset/blob/master/bin/kano-volume)
 * Support for switching to vertual terminals by presing Ctrl-1,Ctrl-2 on the Kano keyboard.

## Desktop integration

[kdesk](https://github.com/KanoComputing/kdesk) is configured here. Its icons can be found in the `icons/`, wallpapers in `wallpapers/` and configuration in `kdesk`.

A particularly important script is `kdesk/icon_hooks.sh`. This allows dynamic configuration of the icons on the desktop. It is currently used to:
 * Display information from the users profile via [kano-profile](https://github.com/KanoComputing/kano-profile) and 
 * Display online/offline status and information about notifications on (Kano World)[http://world.kano.me)
 * Trigger actions when the screensaver kicks in. (This is a convenient time to run [*kano-sync*](https://github.com/KanoComputing/kano-profile/blob/master/bin/kano-sync) and [*kano-updater*](https://github.com/KanoComputing/kano-updater))
 