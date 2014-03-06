//
// sn_callbacks.cpp
//
// Copyright (C) 2013-2014 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// An app to show and bring life to Kano-Make Desktop Icons.
//

//
// The following module provides for sn_notify framework callback functions
// to handle event errors.
//
// TODO: Always keep an eye on libsn upgrades.
// This API library is not officially conformed across different architectures
// See the file:  /usr/include/startup-notification-1.0/libsn/sn-common.h for details
//

#define SN_API_NOT_YET_FROZEN
#include <libsn/sn.h>

#include "logging.h"

unsigned int error_trap_depth;

void error_trap_push (SnDisplay *display, Display *xdisplay);
void error_trap_pop (SnDisplay *display, Display *xdisplay);

void error_trap_push (SnDisplay *display, Display *xdisplay)
{
  log("error_trap_push incrementing");
  ++error_trap_depth;
}

void error_trap_pop (SnDisplay *display, Display *xdisplay)
{
  log ("error_trap_pop call");
  if (error_trap_depth == 0)
    {
      log("fatal error trap underflow - the x11 event chain is hurt");
    }
  
  XSync (xdisplay, False); /* get all errors out of the queue */
  --error_trap_depth;
}
