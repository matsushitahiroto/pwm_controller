from init    import Singleton, SetPin
from display import Display

class Tetris(Singleton):

    __pin     = SetPin()
    __display = Display()


    def run(self) -> None :
        self.__pin.oled.fill( 0 )
        self.__pin.oled.rect(0,0,128,64,1)
        self.__pin.oled.text('TETRIS' , 32, 60 )
        self.__pin.oled.show()
