//
// desktop.cpp
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xft/Xft.h>

//
// TODO: Always keep an eye on libsn upgrades.
// This API library is not officially conformed across different architectures
// See the file:  /usr/include/startup-notification-1.0/libsn/sn-common.h for details
//
#define SN_API_NOT_YET_FROZEN
#include <libsn/sn.h>

#include <unistd.h>
#include <map>

#include "icon.h"
#include "desktop.h"
#include "logging.h"

Desktop::Desktop(Configuration *loaded_conf)
{
  pconf = loaded_conf;
  finish = false;
}

Desktop::~Desktop(void)
{
  // Free all allocated icon handlers in the map
  std::map <Window, Icon *>::iterator it;
  for (it=iconHandlers.begin(); it != iconHandlers.end(); ++it)
    {
      delete it->second;
    }
}

bool Desktop::create_icons (Display *display)
{
  int nicon=0;

  // Create and draw all icons, save a mapping of their window IDs -> handlers
  // so that we can dispatch events to each one in turn later on.
  for (nicon=0; nicon < pconf->get_numicons(); nicon++)
    {
      Icon *pico = new Icon(pconf, nicon);
      Window wicon = pico->create(display);
      if (wicon) {
	XEvent emptyev;
	iconHandlers[wicon] = pico;
	pico->draw(display, emptyev);
      }
      else {
	log1 ("Warning: error creating icon", pconf->get_icon_string(nicon, "filename"));
	delete pico;
      }
    }

  // returns true if at least one icon is available on the desktop
  return (bool) (nicon > 0);
}


/*
static void Desktop::error_trap_push (SnDisplay *display, Display   *xdisplay){ ++error_trap_depth;}
static void Desktop::error_trap_pop (SnDisplay *display, Display   *xdisplay){
  if (error_trap_depth == 0)
    {
      fprintf (stderr, "Error trap underflow!\n");
      exit (1);
    }

  XSync (xdisplay, False); 
  --error_trap_depth;
}
*/


bool Desktop::notify_hourglass_start (Display *display, int iconid, Time time)
{
  bool bsuccess;
  string command = pconf->get_icon_string (iconid, "filename");

  sn_display = sn_display_new (display, NULL, NULL);
  sn_context = sn_launcher_context_new (sn_display, DefaultScreen (display));
  if ((sn_context != NULL) && !sn_launcher_context_get_initiated (sn_context))
    {
      sn_launcher_context_set_name (sn_context, command.c_str());
      sn_launcher_context_set_description (sn_context, command.c_str());
      sn_launcher_context_set_binary_name (sn_context, command.c_str());
      sn_launcher_context_set_icon_name(sn_context, command.c_str());
      sn_launcher_context_initiate (sn_context, command.c_str(), command.c_str(), time);
      bsuccess = true;

      // test application load
      //usleep (1000*3000);
    }

  return bsuccess;
}

bool Desktop::notify_hourglass_end (Display *display, int iconid, Time time)
{
  if (sn_context != NULL) {
    sn_launcher_context_setup_child_process (sn_context);
    sn_launcher_context_unref (sn_context);
    sn_context = 0;
    if (sn_display)
      {
	sn_display_unref (sn_display);
	sn_display = 0;
      }
  }

  return true;
}

bool Desktop::process_and_dispatch(Display *display)
{
  // Process X11 events and dispatch them to each icon handler for processing
  static unsigned long last_click=0, last_dblclick=0;
  static bool bstarted = false;
  int iGrace = 500;
  XEvent ev;
  Window wtarget = 0;

  do 
    {
      XNextEvent(display, &ev);
      wtarget = ev.xany.window;

      if (sn_display != NULL) {
	sn_display_process_event (sn_display, &ev);
      }

      switch (ev.type)
	{
	case ButtonPress:
	  // A double click event is defined by the time elapsed between 2 clicks: "clickdelay"
	  // And a grace time period to protect nested double clicks: "clickgrace"
	  // Note we are listening for both left and right mouse click events.

	  log3 ("ButtonPress event to window and time ms", wtarget, ev.xbutton.time, last_click);
	  if (ev.xbutton.time - last_click < pconf->get_config_int("clickdelay")) 
	    {
	      log ("DOUBLE CLICK!");
	      last_dblclick = ev.xbutton.time;
	      
	      // Tell the icon a mouse double click needs processing
	      bstarted = iconHandlers[wtarget]->double_click (display, ev);
	      notify_hourglass_start (display, iconHandlers[wtarget]->iconid, ev.xbutton.time);
	      notify_hourglass_end (display, iconHandlers[wtarget]->iconid, ev.xbutton.time);
	    }
	  break;

	case ButtonRelease:
	  log2 ("ButtonRelease event to window and time ms", wtarget, ev.xbutton.time);
	  last_click = ev.xbutton.time;
	  break;

	case MotionNotify:
	  iconHandlers[wtarget]->motion(display, ev);
	  break;

	case EnterNotify:
	  log1 ("EnterNotify event to window", wtarget);
	  iconHandlers[wtarget]->blink_icon(display, ev);
	  break;

	case LeaveNotify:
	  log1 ("LeaveNotify event to window", wtarget);
	  iconHandlers[wtarget]->draw(display, ev);
	  break;

	case Expose:
	  iconHandlers[wtarget]->draw(display, ev);
	  break;
	  
	default:
	  break;
	}

    } while (!finish);

  return true;
}

bool Desktop::finalize(void)
{
  finish = true;
}
