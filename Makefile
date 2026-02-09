# Makefile for 2HDMC

# Choose your C++ compiler here (in general g++ on Linux systems):
CC = g++
LDFLAGS=-lgsl -lgslcblas

#Optimisation level, eg: -O3
OPT=-O3
#OR debug level: -g(n=1,2,3)
DEBUG=

VPATH=src

CFLAGS= -std=c++11 -Wall -fopenmp $(DEBUG) $(OPT)

OBJDIR=lib
LIBDIR=$(OBJDIR)
BINDIR=bin
SOURCES=THDM.cpp SM.cpp DecayTable.cpp Constraints.cpp Util.cpp
OBJECTS=$(SOURCES:.cpp=.o)
LIB=lib2HDMC.a
LDFLAGS+=-L$(LIBDIR) -l2HDMC -lgsl -lgslcblas -lm
#LDFLAGS+=-L$(LIBDIR) -l2HDMC
LIBS=
PROG=$(addprefix $(BINDIR)/, CalcPhys CalcGen CalcHiggs CalcHybrid CalcHMSSM CalcMSSM CalcInert CalcLH Demo ScanBR)
INCLUDE=

# To use HiggsBounds/HiggsSignals for Higgs constraints, set both of the
# following path variables to the corresponding build directories.
# Requires HiggsBounds>=5.7.0 and HiggsSignals>=2.4.0
#HiggsBounds_DIR=higgsbounds/build
#HiggsSignals_DIR=higgssignals/build

ifdef HiggsBounds_DIR
ifdef HiggsSignals_DIR
CFLAGS+=-DHiggsBounds
LDFLAGS+=-L$(HiggsBounds_DIR)/lib -L$(HiggsSignals_DIR)/lib -lHS -lHB -lgfortran
INCLUDE+=-I$(HiggsBounds_DIR)/../include -I$(HiggsSignals_DIR)/../include
SOURCES+=HBHS.cpp
endif
endif


#CFLAGS+=-DHiggsBounds
#LDFLAGS+=-L$(LIBDIR) -lHS -lHB -lgfortran
#SOURCES+=HBHS.cpp

.PHONY: lib clean distclean ScanBR CalcPhys CalcGen CalcHiggs CalcHybrid CalcHMSSM CalcMSSM CalcInert CalcLH Demo

all: lib $(PROG)

$(OBJDIR)/%.o : %.cpp %.h
	$(CC) $(CFLAGS) $(INCLUDE) -c $< -o $@

lib: $(addprefix $(LIBDIR)/, $(LIB))

$(addprefix $(LIBDIR)/, $(LIB)): $(addprefix $(OBJDIR)/, $(OBJECTS))
	@ echo "Making library $@"
	@ ar rcs $@ $(addprefix $(OBJDIR)/, $(OBJECTS))

$(BINDIR)/%: src/%.cpp $(addprefix $(LIBDIR)/, $(LIB)) | $(BINDIR)
	@ echo $(CC) $< -Isrc $(CFLAGS) $(LDFLAGS) $(addprefix $(LIBDIR)/, $(LIBS)) -o $@
	@ $(CC) $< -Isrc $(CFLAGS) $(LDFLAGS) $(addprefix $(LIBDIR)/, $(LIBS)) -o $@

$(BINDIR):
	@ mkdir -p $(BINDIR)

# Convenience: allow "make ScanBR" etc. without bin/ prefix
ScanBR CalcPhys CalcGen CalcHiggs CalcHybrid CalcHMSSM CalcMSSM CalcInert CalcLH Demo: %: $(BINDIR)/%

clean:
	@ echo "Cleaning library"
	@ rm -f $(addprefix $(OBJDIR)/, *.o)
	@ rm -f $(addprefix $(LIBDIR)/, $(LIB))

distclean:
	@ make -s clean
	@ echo "Cleaning programs"
	@ rm -f $(PROG)
	@ rm -rf $(BINDIR)
