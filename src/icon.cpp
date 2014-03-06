//
// Icon.cpp  -  Class to draw an icon on the desktop
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xft/Xft.h>

#include <Imlib2.h>

#include <unistd.h>
#include <sys/wait.h>
#include <errno.h>

#include "icon.h"
#include "logging.h"

Icon::Icon (Configuration *loaded_conf, int iconidx)
{
  configuration = loaded_conf;
  iconid = iconidx;
  win = 0;
}

Icon::~Icon (void)
{
}

int Icon::get_iconid()
{
  return iconid;
}

bool Icon::is_singleton_running (void)
{
  bool bAppRunning=false;
  string appid = configuration->get_icon_string (iconid, "appid");
  string singleton = configuration->get_icon_string (iconid, "singleton");

  if (singleton == "true" && appid.size())
    {
      unsigned int rc=0, exitstatus=0;
      char cmdpgrep[512];

      log1 ("searching for singleton app", appid);
      memset(cmdpgrep, 0, sizeof(cmdpgrep));

      sprintf (cmdpgrep, "pgrep -fl '%s'", appid.c_str());
      rc = system (cmdpgrep);
      exitstatus = WEXITSTATUS(rc);
      cout << "pgrep: system rc=" << rc << " exitstatus=" << exitstatus << endl;

      if (exitstatus == 0) {
	bAppRunning = true;
	cout << "app " << appid << " is running" << endl;
      }
      else {
	bAppRunning = false;
	cout << "app " << appid << " is NOT running" << endl;
      }
    }
  return bAppRunning;
}

Window Icon::create (Display *display)
{
  unsigned int rc=0;
  int border, iconx=0, icony=0, iconw=0, iconh=0;

  vis = DefaultVisual(display, DefaultScreen(display));
  cmap = DefaultColormap(display, DefaultScreen(display));

  int fontsize = configuration->get_config_int ("fontsize");
  string fontname = configuration->get_config_string ("fontname");
  string fontbold = configuration->get_config_string ("bold");

  if (fontbold.size()) {
    fontname += " bold";
  }

  log2 ("opening font name and point size", fontname, fontsize);
  font = XftFontOpen (display, DefaultScreen(display),
  		      XFT_FAMILY, XftTypeString, fontname.c_str(),
  		      XFT_SIZE, XftTypeDouble, (float) 14,
  		      NULL);

  if (!font) {
    log("Could not create font!");
  }
  else{
    log("font loaded");
    rc = XftColorAllocName(display, DefaultVisual(display,0), DefaultColormap(display,0), "white", &xftcolor);
    rc = XftColorAllocName(display, DefaultVisual(display,0), DefaultColormap(display,0), "black", &xftcolor_shadow);
    log1 ("XftColorAllocName bool", rc);
  }

  XSetWindowAttributes attr;

  attr.background_pixmap = ParentRelative;
  attr.backing_store = Always;
  attr.event_mask = ExposureMask | EnterWindowMask | LeaveWindowMask;
  attr.override_redirect = True;

  int screen_num = DefaultScreen(display);
  int w = DisplayWidth(display, screen_num);
  int h = DisplayHeight(display, screen_num);

  iconx = configuration->get_icon_int (iconid, "x");
  icony = configuration->get_icon_int (iconid, "y");
  iconw = configuration->get_icon_int (iconid, "width");
  iconh = configuration->get_icon_int (iconid, "height");

  // Decide which icon positioning to use
  if (configuration->get_icon_string(iconid, "relative-to") == "bottom-centre") {
    iconx = w / 2 + iconx;
    icony = h + icony;
  }

  // In debug version, icons are drawn with a black frame
  #ifdef DEBUG
  border = 1;
  #else
  border = 0;
  #endif

  log4 ("icon placement (x,y,w,h): @", iconx, icony, iconw, iconh);
  win = XCreateWindow (display, DefaultRootWindow(display), iconx, icony, iconw, iconh, border,
		       CopyFromParent, CopyFromParent, CopyFromParent,
		       CWBackPixmap|CWBackingStore|CWOverrideRedirect|CWEventMask,
		       &attr );

  XLowerWindow(display, win);
  xftdraw1 = XftDrawCreate(display, win, DefaultVisual(display,0),DefaultColormap(display,0));
  log1("xftdraw1 is", xftdraw1);
  if( win == None ) {
    log ("error creating windows");
  }
  else {
    XSelectInput(display, win, ButtonPressMask | ButtonReleaseMask | PointerMotionMask | ExposureMask | EnterWindowMask | LeaveWindowMask);
    XMapWindow(display, win);
  }
  
  return win;
}

void Icon::initialize (Display *display)  // to be removed!
{
  return;
}

void Icon::draw(Display *display, XEvent ev)
{
  imlib_context_set_display(display);
  imlib_context_set_visual(vis);
  imlib_context_set_colormap(cmap);
  imlib_context_set_drawable(win);

  string ficon1 = configuration->get_icon_string (iconid, "icon");

  log1 ("drawing icon", ficon1);
  imlib_context_set_drawable(win);
  image = imlib_load_image(ficon1.c_str());

  Imlib_Color_Modifier cmHighlight;
  cmHighlight = imlib_create_color_modifier();
  imlib_context_set_color_modifier(cmHighlight);
  imlib_modify_color_modifier_brightness(0);

  imlib_context_set_anti_alias(1);
  imlib_context_set_blend(1);
  imlib_context_set_image(image);
  int w = imlib_image_get_width();
  int h = imlib_image_get_height();

  /* the old position - so we wipe over where it used to be */
  imlib_render_image_on_drawable(0, 0);
  //updates = imlib_update_append_rect(updates, 0, 0, w, h);
  updates = imlib_update_append_rect(updates, 0, 0, w, h);
  imlib_free_image();

  string caption = configuration->get_icon_string (iconid, "caption");
  // We render the caption twice to create a shadow
  XftDrawStringUtf8(xftdraw1, &xftcolor_shadow, font, 1, font->ascent + 1, (XftChar8 *) caption.c_str(), caption.size());
  XftDrawStringUtf8(xftdraw1, &xftcolor, font, 0, font->ascent, (XftChar8 *) caption.c_str(), caption.size());
}

bool Icon::blink_icon(Display *display, XEvent ev)
{
  string filename = configuration->get_icon_string (iconid, "filename");
  log1 ("blinking image on icon", filename);
  return true;
}

bool Icon::motion(Display *display, XEvent ev)
{
  return true;
}

bool Icon::double_click(Display *display, XEvent ev)
{
  bool success = false;
  string filename = configuration->get_icon_string (iconid, "filename");
  string command  = configuration->get_icon_string (iconid, "command");
  
  bool isrunning = is_singleton_running();
  if (isrunning == true) {
    log1 ("not starting app - it's a running singleton", filename);
  }
  else
    {
      // Launch the icon's appplication asynchronously,
      // Set the status to starting, so that icons get disabled
      // Until the app is up and running
      pid_t pid = fork();
      if (pid == 0) {
	// we are in the new forked process
	setsid ();
	int rc = execl ("/bin/sh", "/bin/sh", "-c", command.c_str(), 0);
	if (rc == -1)
	  {
	    log2 ("error starting app (rc, command)", rc, command.c_str());
	    exit(1);
	  }
	
	log1 ("app has finished", filename);
	exit(0);
      }
      else if (pid == -1) {
	log1 ("fork call failed, could not start app (errno)", errno);
      }
      else {
	// we are in the parent process, wait for it to 
	success = true;
	log2 ("app has been started (pid, icon)", pid, filename);
      }
    }

  return success;
}
