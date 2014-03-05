//
// main.cpp
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <stdlib.h>
#include <getopt.h>

#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xft/Xft.h>

#include <Imlib2.h>

#include "version.h"
#include "main.h"
#include "icon.h"
#include "background.h"
#include "desktop.h"
#include "logging.h"

int main(int argc, char *argv[])
{
  Display *display;
  Configuration conf;
  char *display_name = NULL;
  string strKdeskRC, strKdeskDir, strKdeskUser;
  bool test_mode = false;

  cout << "Kano-Desktop - A desktop Icon Manager" << endl;
  cout << "Version v" << VERSION << endl << endl;

  int c;
  while ((c = getopt(argc, argv, "ht")) != EOF)
    {
      switch (c)
        {
	case 'h':
	  cout << "kano-desktop [ -t | -h ]" << endl;
	  cout << " -t test mode, read configuration files and exit"<< endl;
	  cout << " -h help, this screen" << endl << endl;
	  exit (1);

	case 't':
	  cout << "testing configuration" << endl;
	  test_mode = true;
	  break;

	case '?':
	  exit(1);
        }
    }

  // Load configuration settings from user's home director
  cout << "initializing..." << endl;
  struct passwd *pw = getpwuid(getuid());
  const char *homedir = pw->pw_dir;
  strKdeskRC   = FILE_KDESKRC;
  strKdeskDir  = DIR_KDESKTOP;
  strKdeskUser = homedir + string(DIR_KDESKTOP_USER);

  log1 ("loading configuration file", strKdeskRC.c_str());
  if (!conf.load_conf(strKdeskRC.c_str())) {
    cout << "error reading configuration file" << endl;
    exit(1);
  }
  else {
    log1 ("loading icons from directory", strKdeskDir.c_str());
    conf.load_icons(strKdeskDir.c_str());
    conf.dump();
  }

  if (test_mode == true) {
    cout << "test mode - exiting" << endl;
    exit(0);
  }

  if (conf.get_numicons() == 0) {
    log ("Warning: no icons have been loaded");
  }

  // Connect to the X Server
  display = XOpenDisplay(display_name);
  if (!display) {
    char *env_display = getenv ("DISPLAY");
    cout << "could not connect to X display" << endl;
    cout << "DISPLAY=" << (env_display ? env_display : "null") << endl << endl;
    exit (1);
  }

  // Create and draw the desktop background
  Background bg(&conf);
  bg.setup(display);
  bg.load(display);
  bg.draw(display);

  // startup delay
  //unsigned long ms=1000*2000;
  //usleep(ms);   //1000 microseconds in a millisecond.

  // Create and draw desktop icons, then attend user interaction
  Desktop dsk(&conf);
  int nicons = dsk.create_icons(display);
  log1 ("number of desktop icons created", nicons);

  cout << "processing events..." << endl;
  dsk.process_and_dispatch(display);
  
  cout << "finishing..." << endl;
  exit (0);
}
