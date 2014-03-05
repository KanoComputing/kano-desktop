//
//  icon.h
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <X11/Xlib.h>
#include <X11/Xft/Xft.h>
#include <Imlib2.h>
#include "configuration.h"

class Icon
{
 private:
  Configuration *configuration;
  Window win;
  Imlib_Updates updates;
  Imlib_Image image;
  Visual *vis;
  Colormap cmap;
  XftFont *font;
  XftDraw *xftdraw1, *xftdraw2;
  XftColor xftcolor, xftcolor_shadow;

 public:
  int iconid;

  Icon (Configuration *loaded_conf, int iconidx);
  virtual ~Icon (void);

  int get_iconid();
  bool is_singleton_running (void);
  Window create(Display *display);
  void initialize(Display *display);

  void draw(Display *display, XEvent ev);
  bool blink_icon(Display *display, XEvent ev);
  bool double_click(Display *display, XEvent ev);
  bool motion(Display *display, XEvent ev);

};
