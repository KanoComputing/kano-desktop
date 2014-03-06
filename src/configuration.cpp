//
// config.cpp
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

#include <dirent.h>
#include <sstream>
#include <stdlib.h>

#include "configuration.h"
#include "logging.h"

Configuration::Configuration()
{
  numicons=0;
}

Configuration::~Configuration()
{
  ifile.close();
}

bool Configuration::load_conf(const char *filename)
{
  string token, value;

  ifile.open (filename, std::ifstream::in);
  if (!ifile.is_open()) {
    return false;
  }

  // separate parameter - value tokens
  // in the form "Parameter: Value", one per line
  while (ifile >> token)
    {
      if (token == "FontName:") {
	ifile >> value;
	configuration["fontname"] = value;
      }
      
      if (token == "FontSize:") {
	ifile >> value;
	configuration["fontsize"] = value;
      }
      
      if (token == "Bold:") {
	ifile >> value;
	configuration["bold"] = value;
      }

      if (token == "ShadowX:") {
	ifile >> value;
	configuration["shadowx"] = value;
      }
      
      if (token == "ShadowY:") {
	ifile >> value;
	configuration["shadowy"] = value;
      }

      if (token == "Background.File-4-3:") {
	ifile >> value;
	configuration["background.file-4-3"] = value;
      }

      if (token == "Background.File-16-9:") {
	ifile >> value;
	configuration["background.file-16-9"] = value;
      }

      if (token == "ClickDelay:") {
	ifile >> value;
	configuration["clickdelay"] = value;
      }

      if (token == "IconStartDelay:") {
	ifile >> value;
	configuration["iconstartdelay"] = value;
      }
    }
 
  ifile.close();
  return true;
}

bool Configuration::load_icons(const char *directory)
{
  string fpath, lnk_extension = ".lnk";
  struct dirent **files;
  int numfiles, count;

  numfiles = scandir (directory, &files, 0, 0);
  for (count=0; count < numfiles; count++)
    {
      string f = files[count]->d_name;

      // Only read kano-desktop LNK files.
      if (std::equal(lnk_extension.rbegin(), lnk_extension.rend(), f.rbegin()))
	{
	  fpath = directory;
	  fpath += "/";
	  fpath += f.c_str();
	  ifile.open (fpath.c_str(), std::ifstream::in);
	  if (!ifile.is_open()) {
	    log1 ("could not open icon file", fpath);
	  }
	  else {
	    log1 ("parsing icon file", fpath);

	    // Process line-by-line tokens
	    // In the form "Parameter: some values"
	    icons[numicons]["filename"] = f;
	    std::string line;
	    while (std::getline(ifile, line))
	      {
		std::istringstream iss(line);
		std::string temp, value, token;

		// Collect the key name aka "token"
		iss >> token;

		// Then collec the token's value, up to EOL
		while (!iss.eof()) {
		  iss >> temp;
		  value += temp;
		  if (!iss.eof()) value += " ";
		}
		
		if (token == "AppID:") {
		  icons[numicons]["appid"] = value;
		}

		if (token == "Command:") {
		  icons[numicons]["command"] = value;
		}

		if (token == "Icon:") {
		  icons[numicons]["icon"] = value;
		}

		if (token == "Caption:") {

		  // caption supports environment variable expansion
		  if (value[0] == '$') {
		    value = getenv (&value[1]);
		  }

		  icons[numicons]["caption"] = value;
		}

		if (token == "X:") {
		  icons[numicons]["x"] = value;
		}

		if (token == "Y:") {
		  icons[numicons]["y"] = value;
		}

		if (token == "Width:") {
		  icons[numicons]["width"] = value;
		}

		if (token == "Height:") {
		  icons[numicons]["height"] = value;
		}

		if (token == "Singleton:") {
		  icons[numicons]["singleton"] = value;
		}

		if (token == "Relative-To:") {
		  icons[numicons]["relative-to"] = value;
		}

	      }
	  }

	  ifile.close();
	  numicons++;
	  if (numicons == MAX_ICONS) {
	    log1 ("Warning! Max icons reached:", MAX_ICONS);
	    break;
	  }
	}
    }

  log1 ("Number of icons loaded", numicons);
  return (bool) (count > 0);
}

string Configuration::get_config_string(string item)
{
  string value = configuration[item];
  return value;
}

unsigned int Configuration::get_config_int(string item)
{
  string value = configuration[item];
  return atoi(value.c_str());
}

std::string Configuration::get_icon_string(int iconid, std::string key)
{
  string value = icons[iconid][key];
  return value;
}

int Configuration::get_icon_int(int iconid, std::string key)
{
  string value = icons[iconid][key];
  return atoi(value.c_str());
}

int Configuration::get_numicons(void)
{
  return numicons;
}

void Configuration::dump()
{
  log ("dumping MAP configuration values");
  std::map<string,string>::iterator it;
  for (it=configuration.begin(); it != configuration.end(); ++it)
    {
      log2 ("configuration item", it->first, it->second);
    }

  log1 ("dumping all loaded icons:", numicons);
  for (int c=0; c < numicons; c++) {
    log1 ("dumping icon file:", icons[c]["filename"]);
    for (it=icons[c].begin(); it != icons[c].end(); ++it)
      {
	log2 ("icon key", it->first, it->second);
      }

  }
}
