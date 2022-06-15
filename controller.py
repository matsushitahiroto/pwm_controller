from init import Singleton, Config, SetPin
import time

class Controller(Singleton):

    __pin = SetPin()

    # ENTERボタン制御
    enter_hold_time = None
    is_enter_over_hold = False
    # クリックして離したタイミングで押下判定
    def check_enter_click(self) -> int :
        value = self.__pin.enter_btn
        # ボタン検出異常
        if value != Config.OFF and value != Config.ON :
            print('ボタンが不正な状態です')
            self.enter_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作なし
        if value == Config.OFF and self.enter_hold_time == None :
            self.enter_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作開始
        if (value == Config.ON and self.enter_hold_time == None) :
            self.enter_hold_time = time.time()
            return Config.IS_NOT_CLICK

        # 押下時間計算
        elapsed_time = time.time() - self.enter_hold_time

        # ボタン長押し
        if (elapsed_time >= 2) :
            if (value == Config.OFF) :
                self.enter_hold_time = None
                self.is_enter_over_hold = False
                return Config.IS_NOT_CLICK
            elif self.is_enter_over_hold :
                return Config.IS_NOT_CLICK
            else :
                self.is_enter_over_hold = True
                return Config.IS_LONG_CLICK

        # ボタン押下中
        if (value == Config.ON) :
            return Config.IS_NOT_CLICK

        # ボタン操作終了
        self.enter_hold_time = None
        return Config.IS_SHORT_CLICK

    # LEFTボタン制御
    left_hold_time = None
    # クリックして押したタイミングで押下判定
    # 0.5秒ごとに押下判定
    def check_left_click(self, long = None) -> int :
        value = self.__pin.left_btn
        # ボタン検出異常
        if value != Config.OFF and value != Config.ON :
            print('ボタンが不正な状態です')
            self.left_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作なし
        if value == Config.OFF and self.left_hold_time == None :
            self.left_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作開始
        if (value == Config.ON and self.left_hold_time == None) :
            self.left_hold_time = time.time()
            return Config.IS_SHORT_CLICK

        # 押下時間計算
        elapsed_time = time.time() - self.left_hold_time

        if (value == Config.OFF) :
            self.left_hold_time = None
            return Config.IS_NOT_CLICK


        if long is not None :
            # ボタン長押し
            if (elapsed_time >= long) :
                return Config.IS_LONG_CLICK

        # ボタン長押し
        if (elapsed_time >= 0.5) :
            self.left_hold_time = time.time()
            return Config.IS_SHORT_CLICK

        return Config.IS_NOT_CLICK

    # RIGHTボタン制御
    right_hold_time = None
    # クリックして押したタイミングで押下判定
    # 0.5秒ごとに押下判定
    def check_right_click(self, long = None) -> int :
        value = self.__pin.right_btn
        # ボタン検出異常
        if value != Config.OFF and value != Config.ON :
            print('ボタンが不正な状態です')
            self.right_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作なし
        if value == Config.OFF and self.right_hold_time == None :
            self.right_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作開始
        if (value == Config.ON and self.right_hold_time == None) :
            self.right_hold_time = time.time()
            return Config.IS_SHORT_CLICK

        # 押下時間計算
        elapsed_time = time.time() - self.right_hold_time

        if (value == Config.OFF) :
            self.right_hold_time = None
            return Config.IS_NOT_CLICK


        if long is not None :
            # ボタン長押し
            if (elapsed_time >= long) :
                return Config.IS_LONG_CLICK

        # ボタン長押し
        if (elapsed_time >= 0.5) :
            self.right_hold_time = time.time()
            return Config.IS_SHORT_CLICK

        return Config.IS_NOT_CLICK

    # UPボタン制御
    up_hold_time = None
    # クリックして押したタイミングで押下判定
    # 0.5秒ごとに押下判定
    def check_up_click(self, long = None) -> int :
        value = self.__pin.up_btn
        # ボタン検出異常
        if value != Config.OFF and value != Config.ON :
            print('ボタンが不正な状態です')
            self.up_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作なし
        if value == Config.OFF and self.up_hold_time == None :
            self.up_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作開始
        if (value == Config.ON and self.up_hold_time == None) :
            self.up_hold_time = time.time()
            return Config.IS_SHORT_CLICK

        # 押下時間計算
        elapsed_time = time.time() - self.up_hold_time

        if (value == Config.OFF) :
            self.up_hold_time = None
            return Config.IS_NOT_CLICK


        if long is not None :
            # ボタン長押し
            if (elapsed_time >= long) :
                return Config.IS_LONG_CLICK

        # ボタン長押し
        if (elapsed_time >= 0.5) :
            self.up_hold_time = time.time()
            return Config.IS_SHORT_CLICK

        return Config.IS_NOT_CLICK

    # DOWNボタン制御
    down_hold_time = None
    # クリックして押したタイミングで押下判定
    # 0.5秒ごとに押下判定
    def check_down_click(self, long = None) -> int :
        value = self.__pin.down_btn
        # ボタン検出異常
        if value != Config.OFF and value != Config.ON :
            print('ボタンが不正な状態です')
            self.down_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作なし
        if value == Config.OFF and self.down_hold_time == None :
            self.down_hold_time = None
            return Config.IS_NOT_CLICK

        # ボタン操作開始
        if (value == Config.ON and self.down_hold_time == None) :
            self.down_hold_time = time.time()
            return Config.IS_SHORT_CLICK

        # 押下時間計算
        elapsed_time = time.time() - self.down_hold_time

        if (value == Config.OFF) :
            self.down_hold_time = None
            return Config.IS_NOT_CLICK


        if long is not None :
            # ボタン長押し
            if (elapsed_time >= long) :
                return Config.IS_LONG_CLICK

        # ボタン長押し
        if (elapsed_time >= 0.5) :
            self.down_hold_time = time.time()
            return Config.IS_SHORT_CLICK

        return Config.IS_NOT_CLICK