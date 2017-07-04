-include Makefile_$(ARCH)-$(VERSION).inc
-include Makefile.inc

#####################################
## RULES
#####################################
all: $(DISTR)/$(EXEC)

$(DISTR)/$(EXEC): $(BUILD)/main.o
	$(LD) -o $@ $^ $(LDFLAGS)

$(BUILD)/%.o: $(JUBE_HOME)/$(SRC)/%.cpp
	$(CC) $(CFLAGS) -MF "$@.d" -o $@ $<

clean:
	rm -rf $(BUILD)/*

cleaner: clean
	rm -rf $(DISTR)/*

clean_jube:
	rm -rf $(OUTPUT)
	rm -rf $(DISTR_ARCHIVE)
	rm jube-parse.log
