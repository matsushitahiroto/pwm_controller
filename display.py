from init import Singleton, Config, SetPin, AppStatus
from time import sleep
import lang
import framebuf

# oled.pixel(x,y,c)    x,yにdotを表示します。c=1で表示、c=0で消去です。
# oled.hline(x,y,w,c) 　x,yを始点として長さwの水平な線を引きます。
# oled.vline(x,y,h,c) 　x,yを始点として長さwの垂直な線を引きます。
# oled.line(x1,y1,x2,y2,c)　x1,y1からx2,y2まで線を引きます。
# oled.rect(x,y,w,h,c) 　x,yを始点（左上）として、幅w、高さhの四角形を描きます。
# oled.fill_rect (x,y,w,h,c) 　x,yを始点（左上）として、幅w、高さhの四角形を描き、中を塗りつぶします。
# oled.fill(c)　画面全体をc色で塗りつぶします。つまり、c=0で全画面クリア、c=1で全画面白になります。
# blit：別のframebufのコンテンツを描画します

class Display(Singleton):

    __pin    = SetPin()
    __status = AppStatus()

    def __init__(self) :
        fbuf = self.__loadPBM(Config.MAIN_THUMBNAIL, 64, 64)
        self.__pin.oled.fill(0)
        self.__pin.oled.blit(fbuf,32,0)
        self.__pin.oled.show()
        sleep(0.5)


    def __loadPBM(self, arq, tamX, tamY):
        with open(arq, 'rb') as f:
            f.readline() # Magic number
            f.readline() # Creator comment
            f.readline() # Dimensions
            data = bytearray(f.read())
        return framebuf.FrameBuffer(data, tamX, tamY, framebuf.MONO_HLSB)


    def __org_str(self, str_array, sx : int, sy : int) :
        for y, line in enumerate(str_array) :
            for x, dot in enumerate(line) :
                self.__pin.oled.pixel(x + sx,y + sy,dot)


    def app_select(self) -> None :
        app_id = self.__status.app_id
        select_mode = Config.APP[app_id]
        self.__pin.oled.fill(0)
        self.__org_str( lang.LEFT , 3, 30 )
        self.__org_str( lang.RIGHT , 125, 30 )
        if app_id == Config.BLOCK_APP :
            self.__pin.oled.text( select_mode , 45, 3 )
            fbuf = self.__loadPBM(Config.BLOCK_THUMBNAIL, 40, 40)
            self.__pin.oled.blit(fbuf,44,24)
        elif app_id == Config.TETRIS_APP :
            self.__pin.oled.text( select_mode , 41, 3 )
            fbuf = self.__loadPBM(Config.TETRIS_THUMBNAIL, 40, 40)
            self.__pin.oled.blit(fbuf,44,24)
        else :
            self.__pin.oled.text( select_mode , 45, 3 )
            fbuf = self.__loadPBM(Config.TRAIN_THUMBNAIL, 88, 40)
            self.__pin.oled.blit(fbuf,20,24)

        self.__pin.oled.show()


    def sleep(self) -> None :
        fbuf = self.__loadPBM(Config.MAIN_THUMBNAIL, 64, 64)
        self.__pin.oled.fill(0)
        self.__pin.oled.blit(fbuf,32,0)
        self.__pin.oled.show()


    def deep_sleep(self) -> None :
        self.__pin.oled.fill(0)
        self.__pin.oled.show()


    def app_drive(self, mascon_pos : int, type : str, max : int, order_spd : int, speed : int) -> None :
        # 枠作成
        self.__pin.oled.fill(0)
        self.__pin.oled.rect(0, 0, 124, 64, 1)
        self.__org_str( lang.RIGHT , 125, 30 )

        # ノッチグラフ作成
        self.__pin.oled.vline(4, 3, 58, 1)
        self.__pin.oled.vline(5, 3, 58, 1)
        for num in range(0, 6) :
            hy = 6  + 4 * num
            hw = 24 - 3 * num
            vx = 29 - 3 * num
            vy = 4  + 4 * num - (1 if num == 0 else 0)
            vh = 4 if num == 0 else 3
            self.__pin.oled.hline( 6, hy, hw, 1)
            self.__pin.oled.vline(vx, vy, vh, 1)
        self.__pin.oled.fill_rect(6, 29, 24, 11, 1)
        self.__pin.oled.text( Config.MASCON_POS[mascon_pos] , 9, 31, 0 )
        for num in range(0, 5) :
            hy = 44 + 4 * num
            hw =  9 + 3 * num
            vx = 14 + 3 * num
            vy = 42 + 4 * num
            self.__pin.oled.hline( 6, hy, hw, 1)
            self.__pin.oled.vline(vx, vy, 3, 1)
        if mascon_pos < Config.MC_N :
            if mascon_pos == Config.MC_EB :
                self.__pin.oled.fill_rect(6, 3, 24, 3, 1)
            for num in range(0, Config.MC_N - mascon_pos) :
                y = 24 - 4 * num
                w =  9 + 3 * num
                self.__pin.oled.fill_rect(6, y, w, 3, 1)
        if mascon_pos > Config.MC_N :
            for num in range(0, mascon_pos - Config.MC_N) :
                y = 42 + 4 * num
                w =  9 + 3 * num
                self.__pin.oled.fill_rect(6, y, w, 3, 1)

        # タイプ表示
        self.__pin.oled.text( type , 34, 6, 1 )

        # オーダー速度表示
        self.__org_str( lang.ORD , 37, 20 )
        for i, num in enumerate(list(f'{order_spd:03}')) :
            if i == 0 and num == '0' : continue
            if list(f'{speed:03}')[0] == '0' and i == 1 and num == '0' : continue
            self.__pin.oled.text( num, 58 + 8 * i, 20, 1 )

        # 最高速表示
        self.__org_str( lang.MAX , 37, 32 )
        self.__pin.oled.text( str(max) , 58, 32, 1 )

        # 現在速度表示
        for i, num in enumerate(list(f'{speed:03}')) :
            if i == 0 and num == '0' : continue
            if list(f'{speed:03}')[0] == '0' and i == 1 and num == '0' : continue
            self.__org_str( lang.BIG_NUM[num], 55 + 10 * i, 45 )
        self.__pin.oled.text( 'km/h' , 86, 50, 1 )

        # 描画
        self.__pin.oled.show()


    def app_drive_select_mode(self, type_list : list, cursor : int, selected : int) :
        # 枠作成
        self.__pin.oled.fill(0)
        self.__pin.oled.rect(4, 0, 124, 64, 1)
        self.__org_str( lang.LEFT , 0, 30 )

        # リスト描画
        show_list = {
            0 : None,
            1 : None,
            2 : cursor,
            3 : None,
            4 : None,
        }
        for num in range(1, 3) :
            index = cursor - num
            if index < 0 : index = len(type_list) + index
            show_list[2 - num] = index
        for num in range(1, 3) :
            index = cursor + num
            if index >= len(type_list) : index = index - len(type_list)
            show_list[2 + num] = index

        for i in range(len(show_list)):
            if show_list[i] is None : continue
            if i == 2 :
                c = 0
                self.__pin.oled.fill_rect(4, 28, 124, 12, 1)
            else :
                c = 1

            if selected == show_list[i] : self.__pin.oled.text( '*' , 21, 6 + (i * 12), c )
            self.__pin.oled.text( type_list[show_list[i]]['name'] , 30, 6 + (i * 12), c )

        # 描画
        self.__pin.oled.show()


if __name__ == '__main__':
    app = Display()
    app.app_drive(12,'NEKO ROMEN',130,0,10)
    # app.app_drive_select_mode([1,2,3],1,1)
