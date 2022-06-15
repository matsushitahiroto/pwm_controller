from init       import Singleton, Config, SetPin
from display    import Display
from controller import Controller
import time

class Drive(Singleton):

    __pin        = SetPin()
    __display    = Display()
    __controller = Controller()

    # 画面描画モード
    DRIVE_MODE  = 1
    SELECT_MODE = 2
    # 操縦タイプ
    SET_ORDER_VAL_HOLD_TIME = 0.1
    NONE_TYPE                    = 0
    TRAIN_TYPE_NEKO_ROMEN        = 1
    TRAIN_TYPE_YAMANEKO          = 2
    TRAIN_TYPE_GTO               = 3
    TRAIN_TYPE_SIEMENS_SINKANSEN = 4
    TRAIN_LIST = {
        NONE_TYPE : {
            'name'  : 'NONE TYPE',
            'min'   : 30,
            'max'   : 300,
            'speed' : [30,80,150,220,300],
            'freq'  : [None]
        },
        TRAIN_TYPE_NEKO_ROMEN : {
            'name'  : 'NEKO ROMEN',
            'min'   : 20,
            'max'   : 400,
            'speed' : [20,50,80,90,90],
            'freq'  : [None]
        },
        TRAIN_TYPE_YAMANEKO : {
            'name'  : 'YAMANEKO',
            'min'   : 30,
            'max'   : 800,
            'speed' : [20,40,70,100,100],
            'freq'  : [
                [150,200,10],
                [200,1000,140]
            ]
        },
        TRAIN_TYPE_GTO : {
            'name'  : 'GTO',
            'min'   : 30,
            'max'   : 400,
            'speed' : [20,40,60,80,120],
            'freq'  : [
                [800,800,10],
                [380,900,30],
                [500,750,40],
                [500,800,80],
                [800,800,130]
            ]
        },
        TRAIN_TYPE_SIEMENS_SINKANSEN : {
            'name'  : 'SIEMENS SIN',
            'min'   : 30,
            'max'   : 320,
            'speed' : [40,80,140,242,320],
            'freq'  : [
                [300,300,10],
                [350,350,11],
                [390,390,12],
                [440,440,13],
                [466,466,14],
                [523,523,15],
                [587,587,16],
                [622,622,17],
                [698,698,18],
                [783,783,19],
                [900,900,35],
                [900,1000,37],
                [900,1000,41],
                [900,500,101],
                [500,500,350],
            ]
        }
    }

    # 走行関係
    __kasoku     = 0
    __out_speed  = 0
    __freq       = 0
    __sound      = 0
    __order_spd  = 0
    __mascon_pos = 1
    __last_mascon_pos = 1
    __out_speed_disp  = 0
    __order_spd_disp  = 0
    __train_type = NONE_TYPE
    __out_speed_list  = [0,0,0,0,0,0,0,0,0]
    __set_order_val_hold_time = time.time()

    # 画面描画関係
    __display_mode    = DRIVE_MODE
    __cursor_position = NONE_TYPE


    def mascon(self) -> None :

        if self.__pin.mascon == Config.MC_P5 :
            # ボリューム操作時に値が不安定になることがあるので入力値は毎回取得しない
            elapsed_time = time.time() - self.__set_order_val_hold_time
            if (elapsed_time >= self.SET_ORDER_VAL_HOLD_TIME) :
                self.__set_order_val_hold_time = time.time()
                if self.__last_mascon_pos == Config.MC_P5 :
                    self.__mascon_pos = self.__pin.mascon
                else :
                    self.__last_mascon_pos = self.__pin.mascon
        else :
            self.__mascon_pos      = self.__pin.mascon
            self.__last_mascon_pos = self.__mascon_pos

        self.__set_order_speed()
        self.__set_kasoku()
        self.__set_out_speed()
        self.__set_sound_data()

        self.__pin.set_freq_moter1(16000)
        self.__pin.set_freq_moter2(16000 if self.__out_speed == 0 else 30)
        self.__pin.set_freq_moter3(16000)

        self.__pin.set_speed_moter1(round(self.__pin.right_volume))
        self.__pin.set_speed_moter2(round(self.__out_speed))
        self.__pin.set_speed_moter3(round(self.__sound))


    def __set_order_speed(self) -> None :
        if self.__mascon_pos in range(Config.MC_EB, (Config.MC_N + 1)) :
            self.__order_spd = 0
            self.__order_spd_disp = 0
        elif self.__mascon_pos in range(Config.MC_P1, (Config.MC_P5 + 1)) :
            disp_speed = self.TRAIN_LIST[self.__train_type]['speed'][self.__mascon_pos - 8]
            order_spd = Config.ADC_CONVERTE / self.TRAIN_LIST[self.__train_type]['max'] * disp_speed
            self.__order_spd = order_spd if order_spd < Config.ADC_CONVERTE else Config.ADC_CONVERTE
            self.__order_spd_disp = disp_speed


    def __set_kasoku(self) -> None :
        kasoku = 0
        if   self.__mascon_pos in range(Config.MC_P1, (Config.MC_P4 + 1)) : kasoku = Config.ACCEL_RATIO # 力行1~4
        elif self.__mascon_pos == Config.MC_B5 : kasoku = Config.BRAKE_RATIO * 5   # 制動5
        elif self.__mascon_pos == Config.MC_B4 : kasoku = Config.BRAKE_RATIO * 4   # 制動4
        elif self.__mascon_pos == Config.MC_B3 : kasoku = Config.BRAKE_RATIO * 3   # 制動3
        elif self.__mascon_pos == Config.MC_B2 : kasoku = Config.BRAKE_RATIO * 2   # 制動2
        elif self.__mascon_pos == Config.MC_B1 : kasoku = Config.BRAKE_RATIO * 1   # 制動1
        elif self.__mascon_pos == Config.MC_N  : kasoku = Config.BRAKE_RATIO * 1.6 # 惰行
        elif self.__mascon_pos == Config.MC_P5 : kasoku = Config.ACCEL_RATIO * 1.3 # 力行5
        self.__kasoku = kasoku * self.__pin.left_volume / 100


    def __set_out_speed(self) -> None :

        if self.__mascon_pos == Config.MC_EB :
            out_speed = 0
        else :
            out_speed = 0 if self.__out_speed < 0 else self.__out_speed

            if out_speed < self.__order_spd :
                if self.__order_spd - out_speed <= self.__kasoku :
                    out_speed = self.__order_spd
                else :
                    out_speed = out_speed + self.__kasoku

            if out_speed > self.__order_spd :
                if self.__mascon_pos >= Config.MC_N :
                    # 惰行or力行
                    if out_speed - self.__order_spd <= self.__kasoku / Config.BRAKE_RATIO :
                        out_speed = self.__order_spd
                    else :
                        out_speed = out_speed - self.__kasoku / Config.BRAKE_RATIO
                else :
                    # 制動
                    if out_speed - self.__order_spd <= self.__kasoku :
                        out_speed = self.__order_spd
                    else :
                        out_speed = out_speed - self.__kasoku

        if (out_speed < self.TRAIN_LIST[self.__train_type]['min'] and self.__mascon_pos < Config.MC_P1) :
            out_speed  = 0
        else :
            out_speed  = out_speed

        self.__out_speed  = out_speed
        out_speed_disp = round( (out_speed) / ( (Config.ADC_CONVERTE) / self.TRAIN_LIST[self.__train_type]['max'] ) )

        # 値が不安定になることがあるので入力値は平均値で取得
        self.__out_speed_list.append(out_speed_disp)
        mean = sum(self.__out_speed_list)/len(self.__out_speed_list)
        self.__out_speed_list.pop(0)
        self.__out_speed_disp = 0 if round(mean) < 0 else round(mean)


    def __set_sound_data(self) -> None :
        freq = 16000
        freq_data_list = self.TRAIN_LIST[self.__train_type]['freq']
        st = 0
        en = self.TRAIN_LIST[self.__train_type]['speed'][4]
        for index, freq_data in enumerate(freq_data_list) :

            if (index == 0 and freq_data == None) : break

            if index == 0 :
                st  = 0
                en  = freq_data[2]
            else :
                st = freq_data_list[index - 1][2]
                en = freq_data[2]

            stf = freq_data[0]
            enf = freq_data[1]

            if st >= self.__out_speed_disp : continue
            if en <  self.__out_speed_disp : continue
            base = ( (Config.ADC_CONVERTE - self.__pin.right_volume) / self.TRAIN_LIST[self.__train_type]['max'] )
            freq = stf + ( self.__out_speed - st * base ) * (( enf - stf ) / ( en * base - st * base ))
            if   freq < 150   : freq = 150
            elif freq > 16000 : freq = 16000
            if   self.__mascon_pos == Config.MC_N : freq = 150; # 惰行のとき。
            break

        self.__freq  = freq
        self.__sound = 0


    def run(self) -> None :
        if self.__display_mode == self.DRIVE_MODE :
            if (self.__controller.check_right_click() != Config.IS_NOT_CLICK) :
                self.__display_mode = self.SELECT_MODE
        else :
            if (self.__controller.check_left_click() != Config.IS_NOT_CLICK) :
                self.__display_mode = self.DRIVE_MODE

        if self.__display_mode == self.DRIVE_MODE :
            self.__display.app_drive(
                self.__mascon_pos,
                self.TRAIN_LIST[self.__train_type]['name'],
                self.TRAIN_LIST[self.__train_type]['speed'][4],
                self.__order_spd_disp,
                self.__out_speed_disp
            )
        else :
            cursor = self.__cursor_position
            if (self.__controller.check_down_click() != Config.IS_NOT_CLICK) :
                cursor = cursor + 1
            # elif (self.__controller.check_up_click() != Config.IS_NOT_CLICK) :
            #     cursor = cursor - 1

            if len(self.TRAIN_LIST) <= cursor :
                cursor = self.NONE_TYPE
            elif cursor < 0 :
                cursor = len(self.TRAIN_LIST) - 1

            # 存在する設定か判定
            if cursor not in self.TRAIN_LIST.keys() :
                cursor = self.NONE_TYPE

            self.__cursor_position = cursor

            self.__display.app_drive_select_mode(
                self.TRAIN_LIST,
                self.__cursor_position,
                self.__train_type
            )

            # ENTER押下で決定
            if self.__controller.check_enter_click() != Config.IS_NOT_CLICK :
                self.__train_type = cursor


    def deep_sleep(self) -> None :
        self.__out_speed = 0
        self.__pin.set_freq_moter1(16000)
        self.__pin.set_freq_moter2(16000)
        self.__pin.set_freq_moter3(16000)
        self.__pin.set_speed_moter1(0)
        self.__pin.set_speed_moter2(0)
        self.__pin.set_speed_moter3(0)
