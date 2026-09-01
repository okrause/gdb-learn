CFLAGS = -g -O0 -Wall

.PHONY: all clean

all: gradebook crash_roster

gradebook: gradebook.c
	$(CC) $(CFLAGS) -o $@ $<

crash_roster: crash_roster.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f gradebook crash_roster
