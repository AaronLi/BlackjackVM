from pygame import *

class Window:
    """
    Window on a desktop
    """

    def __init__(self, window_surface: Surface) -> None:
        super().__init__()
        self.screen = window_surface

    def mouse_click(self, mx, my) -> None:
        """
        Where the user clicked the screen
        :param mx: x click position on window
        :param my: y click position on window
        :return:
        """
        pass

    def mouse_relative_move(self, rx, ry) -> None:
        """
        The relative motion of the user's mouse
        :param rx: The distance moved in x
        :param ry: The disgtance moved in y
        :return:
        """
        pass

    def key_input(self, keycode, mod) -> None:
        pass

    def render(self) -> None:
        """
        Draws to the surface that was given to this window
        :return:
        """
        pass