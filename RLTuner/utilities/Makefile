TARGET=libutilities.a
CC=gcc -g
CXX=g++ -g
cppfiles=datautils.cpp  metrics.cpp  IO.cpp mp_math.cpp
obj=$(cfiles:.c=.o)
obj+=$(cppfiles:.cpp=.o)

all:$(TARGET) quality

$(TARGET): $(obj)
	ar -rcs $@ $^	
%.o: %.cpp
	 $(CXX) $(CFLAGS) $(INCLUDE) -o $@ -c $<
%.o: %.c
	 $(CC) $(CFLAGS) $(INCLUDE) -o $@ -c $<

quality: quality.c $(TARGET)
	$(CXX) $(CFLAGS) $(INCLUDE) -o $@ $< $(TARGET)


clean:
	rm -rf *.o $(TARGET) quality


