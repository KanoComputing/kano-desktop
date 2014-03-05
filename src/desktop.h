//
// desktop.h
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

class Desktop
{
 private:
  std::map <Window, Icon *> iconHandlers;
  SnDisplay *sn_display;
  SnLauncherContext *sn_context;
  Configuration *pconf;
  bool finish;

 public:
  Desktop(Configuration *loaded_conf);
  virtual ~Desktop(void);

  bool create_icons (Display *display);
  bool notify_hourglass_start (Display *display, int iconid, Time time);
  bool notify_hourglass_end (Display *display, int iconid, Time time);
  bool process_and_dispatch(Display *display);
  bool finalize(void);

  /*
  void error_trap_push (SnDisplay *display, Display   *xdisplay);
  void error_trap_pop (SnDisplay *display, Display   *xdisplay);
  */
};
