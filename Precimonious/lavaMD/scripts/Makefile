APPROX_UTIL_ROOT?=../../utilities
CXX?=g++
OMP_LIB = -lgomp
OMP_FLAG = -fopenmp
LIB=${APPROX_UTIL_ROOT}/libutilities.a
all: lavaMd 

lavaMd:	lava_util.o main.cpp  
	$(CXX)	main.cpp lava_util.o  -o lavaMD $(LIB) -lm
# compile function files into objects (binaries)

lava_util.o: lava_util.cpp
	g++ -c lava_util.cpp 

clean:
	rm -rf	*.o lavaMD
