from machine import ADC
from time import sleep

class RS_2688_0112() :
    __mascon = None
    def __init__(self, mascon) :
        self.__mascon = mascon

    def value (self) :
        position = self.__mascon.read_u16() / 65535 * 100
        if position <  4 : return 12
        if position < 12 : return 11
        if position < 20 : return 10
        if position < 30 : return  9
        if position < 37 : return  8
        if position < 45 : return  7
        if position < 55 : return  6
        if position < 65 : return  5
        if position < 75 : return  4
        if position < 85 : return  3
        if position < 95 : return  2
        else             : return  1

if __name__ == '__main__':
    app = RS_2688_0112(ADC( 2 ))
    while True :
        print(str(app.value()))
        sleep(1)