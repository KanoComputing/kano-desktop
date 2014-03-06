//
// desktop.h
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

//
// TODO: Always keep an eye on libsn upgrades.
// This API library is not officially conformed across different architectures
// See the file:  /usr/include/startup-notification-1.0/libsn/sn-common.h for details
//
#define SN_API_NOT_YET_FROZEN
#include <libsn/sn.h>

class Desktop
{
 private:
  std::map <Window, Icon *> iconHandlers;
  SnDisplay *sn_display;
  SnLauncherContext *sn_context;
  Configuration *pconf;
  bool finish;
  static int error_trap_depth;

 public:
  Desktop(Configuration *loaded_conf);
  virtual ~Desktop(void);

  bool create_icons (Display *display);

  bool notify_startup_load (Display *display, int iconid, Time time);
  bool notify_startup_ready (Display *display);
  void notify_startup_event (Display *display, XEvent *pev);

  bool process_and_dispatch(Display *display);
  bool finalize(void);

};
