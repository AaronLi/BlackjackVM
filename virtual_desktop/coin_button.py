from typing import Tuple

from pygame import Rect, Surface
from data.loader import font_small

from virtual_desktop.button import Button


class CoinButton(Button):
    def __init__(self, pos: Tuple[int, int], label: str, background_coin: Surface, text_colour=(0, 0, 0)) -> None:
        super().__init__(Rect(pos, background_coin.get_size()), label, (0, 0, 0), text_colour)
        self.coin_icon = background_coin

    def render(self):
        out_coin = self.coin_icon.copy()
        rendered_coin_label = font_small.render(self.label, False, self.text_colour)
        out_coin.blit(rendered_coin_label, (out_coin.get_width()//2 - rendered_coin_label.get_width()//2, out_coin.get_height()//2 - rendered_coin_label.get_height()//2))
        return out_coin
