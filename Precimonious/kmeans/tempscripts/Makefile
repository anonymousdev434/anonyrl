# C compiler
APPROX_UTIL_ROOT?=../../utilities
LIB=${APPROX_UTIL_ROOT}/libutilities.a
CXX?= g++
CXX_FLAGS = -g  -O2 ${CFLAGS} 

all: kmeans

kmeans: kmeans.cpp 
	$(CXX) $(CXX_FLAGS) kmeans.cpp -o kmeans ${LIB} 

clean:
	rm -f *.o *~ kmeans 
