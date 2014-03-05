//
// background.cpp  -  Class to draw an icon on the desktop
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <X11/Xlib.h>
#include <Imlib2.h>

#include <cmath>

#include "logging.h"
#include "configuration.h"
#include "background.h"

Background::Background (Configuration *loaded_conf)
{
  running = false;
  pconf = loaded_conf;
}

Background::~Background (void)
{
}

bool Background::setup(Display *display)
{
  int i, screen;

  // Setup X resources
  screen = DefaultScreen (display);
  vis = DefaultVisual (display, screen);
  cm = DefaultColormap (display, screen);
  root = RootWindow (display, screen);
  XSelectInput (display, root, StructureNotifyMask);

  deskw = DisplayWidth(display, screen);
  deskh = DisplayHeight(display, screen);

  // Bind resources to Imlib2
  imlib_context_set_display(display);
  imlib_context_set_visual(vis);
  imlib_context_set_colormap(cm);

  pmap = XCreatePixmap (display, root, deskw, deskh, DefaultDepth (display, DefaultScreen (display)));
  if (!pmap) {
    log ("error creating pixmap for desktop background");
    return false;
  }

  return true;
}

bool Background::load (Display *display)
{
  int i, w, h, nx, ny, nh, nw, tmp;
  float ratio, dist43, dist169;
  double factor;
  string background_file;
  Imlib_Image tmpimg, buffer;
  bool bsuccess=false;

  buffer = imlib_create_image (deskw, deskh);
  if (!buffer)
    {
      log ("error creating an image surface for the backgroun");
    }
  else
    {
      ratio = (deskw *1.0) / (deskh);
      dist43 = std::abs (ratio - 4.0/3.0);
      dist169 = std::abs (ratio - 16.0/9);

      // Decide which image to load depending on screen aspect/ratio
      if (dist43 < dist169) {
	background_file = pconf->get_config_string ("background.file-4-3");
	log1 ("loading 4:3 background image", background_file);
      }
      else {
	background_file = pconf->get_config_string ("background.file-16-9");
	log1 ("loading 16:9 background image", background_file);
      }

      image = imlib_load_image_without_cache(background_file.c_str());
      if (!image) {
	bsuccess = false;
	log1 ("error loading background", background_file);
      }

      // Prepare imlib2 drawing spaces
      imlib_context_set_image(buffer);
      imlib_context_set_color(0,0,0,0);
      imlib_image_fill_rectangle(0, 0, deskw, deskh);
      imlib_context_set_blend(1);
      
      imlib_context_set_image(image);
      w = imlib_image_get_width();
      h = imlib_image_get_height();
      if (!(tmpimg = imlib_clone_image())) {
	bsuccess = false;
	log ("error cloning the desktop background image");
      }
      else {
	imlib_context_set_image(tmpimg);
	imlib_context_set_image(buffer);

	int screen_num = DefaultScreen(display);
	int nw = DisplayWidth(display, screen_num);
	int nh = DisplayHeight(display, screen_num);

	imlib_blend_image_onto_image(tmpimg, 0, 0, 0, w, h, 0, 0, nw, nh);
	imlib_context_set_image(tmpimg);
	imlib_free_image();

	imlib_context_set_blend(0);
	imlib_context_set_image(buffer);
	imlib_context_set_drawable(root);
	imlib_render_image_on_drawable(0, 0);
	imlib_context_set_drawable(pmap);
	imlib_render_image_on_drawable(0, 0);
	XSetWindowBackgroundPixmap(display, root, pmap);
	imlib_context_set_image(buffer);
	imlib_free_image_and_decache();
	XFreePixmap(display, pmap);

	bsuccess = true;
	log1 ("desktop background created successfully", image);
      }
    }

  return bsuccess;
}

bool Background::draw(Display *display)
{
	XEvent ev;

	for(;;) {
	  //updategeom();
	  //drawbg(display);
	  if(!running)
	    break;
	  imlib_flush_loaders();
	  XNextEvent(display, &ev);
	  if(ev.type == ConfigureNotify) {
	    deskw = ev.xconfigure.width;
	    deskh = ev.xconfigure.height;
	    imlib_flush_loaders();
	  }
	}
}
