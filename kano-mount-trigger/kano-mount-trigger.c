//
// kano-mount-trigger.c
//
// Copyright (C) 2015 Kano Computing Ltd.
// License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
//
// A short program which triggers an action when sent a signal
//
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

void null_handle(int _) {}

int main(int argc,char *argv[]) {

    if(argc<2){
      fprintf(stderr, "Usage: kano-mount-trigger <command>\n");
      exit(1);
    }

    // we want to exit from sleeping when signalled
    // but the signal handler need not do anything
    signal(SIGUSR1, null_handle);

    while(1) {
        int count=sleep(60*60);
        if(!count) continue; // count ran out

        // if we got here, we were signalled
        system(argv[1]);
    }

    return 0;
}
