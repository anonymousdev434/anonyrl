APPROX_UTIL_ROOT?=../../utilities
CXX?=g++ -g
LDFLAGS = -lm  
INCLUDE=-I${APPROX_UTIL_ROOT} -I${APPROX_UTIL_ROOT}/metrics/ -I${APPROX_UTIL_ROOT}/common/
TARGET=euler3d
LIB=${APPROX_UTIL_ROOT}/libutilities.a
req = pre_euler3d_cpu.cpp    
obj= pre_euler3d_cpu.o 


all:$(TARGET) 

$(TARGET): $(req) 
	$(CXX) -O3 $(INCLUDE) $(req) -o $(TARGET) $(LIB) $(LDFLAGS)

clean:
	rm -f $(obj)  $(TARGET) 
