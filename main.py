from init       import Singleton, Config, SetPin, AppStatus
from display    import Display
from controller import Controller
from app.drive  import Drive
from app.paddle import Paddle
from app.tetris import Tetris

class App(Singleton):

    __status     = AppStatus()
    __pin        = SetPin()
    __display    = Display()
    __controller = Controller()
    __drive      = Drive()
    __paddle     = Paddle()
    __tetris     = Tetris()

    def main(self) -> None :

        while True :
            self.__pin.check_sleep()
            status = self.__status.status
            if status == Config.DEEP_SLEEP_MODE :
                # ディープスリープ
                self.__deep_sleep()
                self.__drive.__deep_sleep()
            else :
                self.__drive.mascon()
                # アプリ実行中
                if status == Config.RUN :
                    self.__run()
                # モードセレクト
                elif status == Config.SELECT_MODE :
                    self.__app_select()
                # スリープ
                elif status == Config.SLEEP_MODE :
                    self.__sleep()
                # モードセレクトに移行
                else :
                    self.__status.status = Config.SELECT_MODE



    def __run(self) -> None :
        app_id = self.__status.app_id
        app_id = 0

        app = self.__drive
        if app_id == Config.BLOCK_APP :
            app = self.__paddle
        elif app_id == Config.TETRIS_APP :
            app = self.__tetris

        # アプリが選択されていたら実行
        if app != None : app.run()

        # エンター長押しでモード切り替え
        if self.__controller.check_enter_click() == Config.IS_LONG_CLICK :
            self.__status.status = Config.SELECT_MODE


    def __app_select(self) -> None :
        app_id = self.__status.app_id
        if (self.__controller.check_right_click() != Config.IS_NOT_CLICK) :
            app_id = app_id + 1
        elif (self.__controller.check_left_click() != Config.IS_NOT_CLICK) :
            app_id = app_id - 1

        if len(Config.APP) <= app_id :
            app_id = Config.DRIVE_APP
        elif app_id < 0 :
            app_id = len(Config.APP) - 1

        # 存在する設定か判定
        if app_id not in Config.APP.keys() :
            app_id = Config.DRIVE_APP

        self.__status.app_id = app_id

        self.__display.app_select()

        # ENTER押下で決定
        if self.__controller.check_enter_click() != Config.IS_NOT_CLICK :
            self.__status.status = Config.RUN


    def __sleep(self) -> None :
        self.__display.sleep()


    def __deep_sleep(self) -> None :
        self.__display.deep_sleep()


if __name__ == '__main__':
    app = App()
    app.main()
