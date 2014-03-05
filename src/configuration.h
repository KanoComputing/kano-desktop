//
// config.h
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <fstream>
#include <iostream>
#include <map>
#include <vector>

#define MAX_ICONS 12

class Configuration
{
 protected:
  std::ifstream ifile;
  std::map <std::string, std::string> configuration;
  std::map<int,std::map<std::string,std::string> > icons;
  int numicons;
  Configuration *pconf;

 public:
  Configuration ();
  virtual ~Configuration (void);
  bool load_conf (const char *filename);
  bool load_icons (const char *directory);
  void dump (void);

  std::string get_config_string(std::string item);
  unsigned int get_config_int(std::string item);
  std::string get_icon_string(int iconid, std::string key);
  int get_icon_int(int iconid, std::string key);
  int get_numicons(void);  
};
