# lib
from machine import Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
from rs_2688_0112 import RS_2688_0112
import time

class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        else:
            def init_pass(self, *args, **kwargs):
                pass
            cls.__init__ = init_pass
        return cls._instance


class Config(Singleton):

    # ADCのデジタル値を変換する値
    ADC_CONVERTE = 65535

    # I2C 関連
    I2C_SDA_PIN = 16
    I2C_SCL_PIN = 17
    I2C_CH      = 0
    FREQ        = 400000

    # PWM出力関連
    MOTER1_PIN  = 19 # 常点灯
    MOTER2_PIN  = 21 # 加速
    MOTER3_PIN  = 22 # 音

    # スイッチ関連
    ENTER_BTN_PIN = 1 # 決定ボタン
    DOWN_BTN_PIN  = 2 # 下ボタン
    LEFT_BTN_PIN  = 3 # 左ボタン
    RIGHT_BTN_PIN = 4 # 右ボタン
    UP_BTN_PIN    = 5 # 上ボタン

    # ボリューム関連(ADC)
    RIGHT_VOLUME_PIN = 0 # 右ボリューム
    LEFT_VOLUME_PIN  = 1 # 左ボリューム
    MAIN_VOLUME_PIN  = 2 # マスコン

    # ボタンの状態
    OFF = 1
    ON  = 0

    # ENTERボタンの状態
    IS_NOT_CLICK   = 0
    IS_SHORT_CLICK = 1
    IS_LONG_CLICK  = 2

    # モニター関連
    HEIGHT = 64
    WIDTH  = 128

    # APPモード
    DRIVE_APP  = 0
    BLOCK_APP  = 1
    TETRIS_APP = 2
    APP = {
        DRIVE_APP  : 'DRIVE',
        BLOCK_APP  : 'BLOCK',
        TETRIS_APP : 'TETRIS'
    }

    # 画像
    MAIN_THUMBNAIL   = 'img/thumbnail.pbm' # 64x64
    TRAIN_THUMBNAIL  = 'img/train.pbm'     # 88X40
    BLOCK_THUMBNAIL  = 'img/block.pbm'     # 40X40
    TETRIS_THUMBNAIL = 'img/tetris.pbm'    # 40X40

    # 画面の状態定数
    SLEEP_TIME      = 300
    RUN             = 1
    SELECT_MODE     = 2
    SLEEP_MODE      = 3
    DEEP_SLEEP_MODE = 4

    # マスコン関連
    ACCEL_RATIO    = 50
    BRAKE_RATIO    = 30
    MC_EB =  1 # マスコン位置 非常
    MC_B5 =  2 # マスコン位置 制動5
    MC_B4 =  3 # マスコン位置 制動4
    MC_B3 =  4 # マスコン位置 制動3
    MC_B2 =  5 # マスコン位置 制動2
    MC_B1 =  6 # マスコン位置 制動1
    MC_N  =  7 # マスコン位置 惰行
    MC_P1 =  8 # マスコン位置 力行1
    MC_P2 =  9 # マスコン位置 力行2
    MC_P3 = 10 # マスコン位置 力行3
    MC_P4 = 11 # マスコン位置 力行4
    MC_P5 = 12 # マスコン位置 力行5
    MASCON_POS = {
        MC_EB : 'EB',
        MC_B5 : 'B5',
        MC_B4 : 'B4',
        MC_B3 : 'B3',
        MC_B2 : 'B2',
        MC_B1 : 'B1',
        MC_N  : 'N',
        MC_P1 : 'P1',
        MC_P2 : 'P2',
        MC_P3 : 'P3',
        MC_P4 : 'P4',
        MC_P5 : 'P5'
    }


class AppStatus(Singleton):
    # 現在の状態
    __status = Config.SELECT_MODE
    # 現在選択中のアプリid
    __app_id = Config.DRIVE_APP

    @property
    def status(self) -> int :
        return self.__status
    @status.setter
    def status(self, value : int) -> None :
        self.__status = value

    @property
    def app_id(self) -> int :
        return self.__app_id
    @app_id.setter
    def app_id(self, value : int) -> None :
        self.__app_id = value


class SetPin(Singleton):

    __status = AppStatus()

    # 最後にボタン操作があったタイミング
    time_operated_last = time.time()
    # 最後のボタンの状態
    __last_enter_btn_val     = 0
    __last_left_btn_val      = 0
    __last_right_btn_val     = 0
    __last_up_btn_val        = 0
    __last_down_btn_val      = 0
    __last_mascon_val        = 0

    def __init__(self):
        # 入力端子設定
        mascon                = ADC( Config.MAIN_VOLUME_PIN )
        self.__left_volume    = ADC( Config.LEFT_VOLUME_PIN )
        self.__right_volume   = ADC( Config.RIGHT_VOLUME_PIN )
        self.__moter1         = PWM( Pin( Config.MOTER1_PIN ) )
        self.__moter2         = PWM( Pin( Config.MOTER2_PIN ) )
        self.__moter3         = PWM( Pin( Config.MOTER3_PIN ) )
        self.__enter_btn      = Pin( Config.ENTER_BTN_PIN, Pin.IN, Pin.PULL_DOWN )
        self.__left_btn       = Pin( Config.LEFT_BTN_PIN,  Pin.IN, Pin.PULL_DOWN )
        self.__right_btn      = Pin( Config.RIGHT_BTN_PIN, Pin.IN, Pin.PULL_DOWN )
        self.__up_btn         = Pin( Config.UP_BTN_PIN,    Pin.IN, Pin.PULL_DOWN )
        self.__down_btn       = Pin( Config.DOWN_BTN_PIN,  Pin.IN, Pin.PULL_DOWN )
        i2c = I2C( Config.I2C_CH, scl=Pin( Config.I2C_SCL_PIN ), sda=Pin( Config.I2C_SDA_PIN ), freq=Config.FREQ )
        data = i2c.scan()

        # ライブラリ関連設定
        self.oled      = SSD1306_I2C( Config.WIDTH, Config.HEIGHT, i2c )
        self.__mascon  = RS_2688_0112( mascon )

        self.set_val()

    @property
    def left_volume(self)   -> int : return round(self.__left_volume.read_u16() / Config.ADC_CONVERTE * 100 - 0.2)
    @property
    def right_volume(self)  -> int : return Config.ADC_CONVERTE - self.__right_volume.read_u16()
    @property
    def mascon(self)        -> int : return self.__mascon.value()
    @property
    def enter_btn(self)     -> int : return self.__enter_btn.value()
    @property
    def left_btn(self)      -> int : return self.__left_btn.value()
    @property
    def right_btn(self)     -> int : return self.__right_btn.value()
    @property
    def up_btn(self)        -> int : return self.__up_btn.value()
    @property
    def down_btn(self)      -> int : return self.__down_btn.value()

    # モーターの制御
    def set_freq_moter1( self, value : int) -> None : self.__moter1.freq(value)
    def set_speed_moter1(self, value : int) -> None : self.__moter1.duty_u16(value)
    def set_freq_moter2( self, value : int) -> None : self.__moter2.freq(value)
    def set_speed_moter2(self, value : int) -> None : self.__moter2.duty_u16(value)
    def set_freq_moter3( self, value : int) -> None : self.__moter3.freq(value)
    def set_speed_moter3(self, value : int) -> None : self.__moter3.duty_u16(value)


    def set_val (self) -> None :
        self.__last_enter_btn_val     = self.enter_btn
        self.__last_left_btn_val      = self.left_btn
        self.__last_right_btn_val     = self.right_btn
        self.__last_up_btn_val        = self.up_btn
        self.__last_down_btn_val      = self.down_btn
        self.__last_mascon_val        = self.mascon


    def check_sleep (self) -> None :
        is_operated = True
        if (self.__last_enter_btn_val     == self.enter_btn
        and self.__last_left_btn_val      == self.left_btn
        and self.__last_right_btn_val     == self.right_btn
        and self.__last_up_btn_val        == self.up_btn
        and self.__last_down_btn_val      == self.down_btn
        and self.__last_mascon_val        == self.mascon) :
            is_operated = False


        # 最後のボタン操作からの経過時間計算
        elapsed_time = time.time() - self.time_operated_last

        if is_operated :
            self.time_operated_last = time.time()
            if self.__status.status == Config.SLEEP_MODE or self.__status.status == Config.DEEP_SLEEP_MODE :
                self.__status.status = Config.RUN
                time.sleep(0.2)
        elif elapsed_time > Config.SLEEP_TIME * 2 :
            if self.__status.status != Config.DEEP_SLEEP_MODE : self.__status.status = Config.DEEP_SLEEP_MODE
        elif elapsed_time > Config.SLEEP_TIME :
            if self.__status.status != Config.SLEEP_MODE : self.__status.status = Config.SLEEP_MODE

        self.set_val()
