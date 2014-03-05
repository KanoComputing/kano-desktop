//
// icons.cpp  -  Place icons on the desktop
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <stdlib.h>

#include <X11/Xlib.h>
#include <Imlib2.h>

#include "logging.h"

void desktop_icons(Display *display)
{
  Window win;
  XSetWindowAttributes attr;
  Visual  *vis;
  Colormap cm;
  Imlib_Updates updates;
  XEvent ev;
  unsigned int w=0, h=0;

  attr.background_pixmap = ParentRelative;
  attr.backing_store = Always;
  attr.event_mask = ExposureMask;
  attr.override_redirect = True;
  log("XCreateWindow");

  int screen_num = DefaultScreen(display);
  w = DisplayWidth(display, screen_num);
  h = DisplayHeight(display, screen_num);

  //w = 500;
  //h = 500;

  win = XCreateWindow( display, DefaultRootWindow(display), 0, 0, w, h, 0,
		     CopyFromParent, CopyFromParent, CopyFromParent,
		     CWBackPixmap|CWBackingStore|CWOverrideRedirect|CWEventMask,
		     &attr );

  if( win == None ) {
    log ("error!");
  }
  else {

    XSelectInput(display, win, ButtonPressMask | ButtonReleaseMask | PointerMotionMask | ExposureMask);
    XMapWindow(display, win);

    imlib_set_cache_size(2048 * 1024);
    imlib_set_font_cache_size(512 * 1024);
    imlib_add_path_to_font_path("./ttfonts");

    vis = DefaultVisual(display, DefaultScreen(display));

    // load bitmap into the screen
    imlib_context_set_display(display);
    imlib_context_set_visual(vis);
    imlib_context_set_colormap(cm);
    imlib_context_set_drawable(win);

    Imlib_Image image;
    image = imlib_load_image("../prototype/xrysa.png");
    imlib_context_set_image(image);

    for (;;)
      {

    do {
      updates = imlib_updates_init();

      XNextEvent(display, &ev);
      switch (ev.type)
	{
	case MotionNotify:
	  break;

	case Expose:
	  log ("motion notify");
	  image = imlib_load_image("../prototype/xrysa.png");
	  imlib_context_set_image(image);
	  w = imlib_image_get_width();
	  h = imlib_image_get_height();
	  /* the old position - so we wipe over where it used to be */
	  imlib_render_image_on_drawable(0, 0);
	  updates = imlib_update_append_rect(updates, 0, 0, w, h);
	  imlib_free_image();
	  break;

	default:
	  /* any other events - do nothing */
	  break;
	}


      if (updates)
	log ("updating...");
	imlib_updates_free(updates);

    } while (XPending(display));

  }


  }
  return;
}
