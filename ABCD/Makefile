include Makefile.inc

#####################################
## DIRECTORIES
#####################################
SRC=src
DISTR=distr
BUILD=build
EXEC=$(DISTR)/abcd_run

#####################################
## RULES
#####################################
all: $(EXEC)

$(EXEC): $(BUILD)/main.o
	mkdir -p $(DISTR)
	$(LD) -o $@ $^ $(LDFLAGS)

$(BUILD)/%.o: $(SRC)/%.cpp
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) -MF "$@.d" -o $@ $<

clean:
	rm -rf $(BUILD)

cleaner: clean
	rm -rf $(DISTR)
	
