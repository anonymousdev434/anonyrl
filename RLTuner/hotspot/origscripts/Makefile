APPROX_UTIL_ROOT?=../../utilities
CXX?=g++ -g
LDFLAGS = -lm  
INCLUDE=-I${APPROX_UTIL_ROOT} -I${APPROX_UTIL_ROOT}/metrics/ -I${APPROX_UTIL_ROOT}/common/
TARGET=hotspot
LIB=${APPROX_UTIL_ROOT}/libutilities.a
req = hotspot_openmp.cpp
obj= hotspot_openmp.o 
CFLAGS?=


all:$(TARGET) 

$(TARGET): $(req) 
	$(CXX) -O3  ${CFLAGS} $(INCLUDE) $(req)  $(LIB) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(obj)  $(TARGET) 
