APPROX_UTIL_ROOT?=../../utilities
CXX?=g++ -g
LDFLAGS = -lm  
INCLUDE=-I${APPROX_UTIL_ROOT} -I${APPROX_UTIL_ROOT}/metrics/ -I${APPROX_UTIL_ROOT}/common/
TARGET=blackscholes
LIB=${APPROX_UTIL_ROOT}/libutilities.a
req = blackscholes.cpp    
obj= blackscholes.o 
CFLAGS?=


all:$(TARGET) 

$(TARGET): $(req) 
	$(CXX) ${CFLAGS} $(INCLUDE) $(req)  $(LIB) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(obj)  $(TARGET) 
