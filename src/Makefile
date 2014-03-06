#
# Build kano-desktop
#
#  $ make - builds the release version
#  $ make debug - with debug logs to console
#
# Requirements:
#
#  libx11-dev, libxft-dev, libstartup-notification0-dev
#

DEBUGGING:=

LIBS:=-lXft -lImlib2 -lstdc++ `pkg-config --libs libstartup-notification-1.0`
XFTINC:=-I/usr/include/freetype2
SNINC=-I/usr/include/startup-notification-1.0

TARGET=kdesk

all: $(TARGET)

debug:
	make all DEBUGGING="-ggdb -O3 -DDEBUG"

$(TARGET): main.o icon.o background.o configuration.o desktop.o
	g++ $(LIBS) $^ -o $(TARGET)

icon.o: icon.cpp icon.h logging.h configuration.h
	g++ -c $(DEBUGGING) $(XFTINC) icon.cpp

main.o: main.cpp main.h configuration.h logging.h version.h
	g++ -c $(DEBUGGING) $(XFTINC) $(SNINC) main.cpp

background.o: background.cpp logging.h
	g++ -c $(DEBUGGING) background.cpp

configuration.o: configuration.cpp configuration.h logging.h
	g++ -c $(DEBUGGING) configuration.cpp

desktop.o: desktop.cpp desktop.h logging.h configuration.h sn_callbacks.cpp
	g++ -c $(DEBUGGING) $(XFTINC) $(SNINC) desktop.cpp
