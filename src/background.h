//
// background.cpp  -  Class to draw an icon on the desktop
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

class Background
{
 private:
  Configuration *pconf;
  Window root;
  Visual *vis;
  Colormap cm;
  Pixmap pmap;
  Imlib_Image image;
  unsigned int deskw, deskh;

 public:
  bool running;

 public:
  Background (Configuration *loaded_conf);
  virtual ~Background (void);
  
  bool setup (Display *display);
  bool load (Display *display);
  bool draw (Display *display);

};
