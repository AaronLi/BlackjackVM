from typing import Tuple

from virtual_desktop import screensize
from virtual_desktop.text_field import TextField
from data.loader import font_small
from pygame import *


class TotpField(TextField):
    charmap = {
        (48, 0): '0',
        (49, 0): '1',
        (50, 0): '2',
        (51, 0): '3',
        (52, 0): '4',
        (53, 0): '5',
        (54, 0): '6',
        (55, 0): '7',
        (56, 0): '8',
        (57, 0): '9',
        (1073741922, 0): '0',
        (1073741913, 0): '1',
        (1073741914, 0): '2',
        (1073741915, 0): '3',
        (1073741916, 0): '4',
        (1073741917, 0): '5',
        (1073741918, 0): '6',
        (1073741919, 0): '7',
        (1073741920, 0): '8',
        (1073741921, 0): '9',
    }

    def __init__(self, num_digits: int, trim_colour: Tuple[int, int, int], text_colour: Tuple[int, int, int]) -> None:
        self.max_char_width = 0
        self.max_char_height = 0
        for metric in font_small.metrics(''.join(list(TotpField.charmap.values()))):
            self.max_char_width = max(metric[1] - metric[0], self.max_char_width)
            self.max_char_height = max(metric[3] - metric[2], self.max_char_height)

        super().__init__((self.max_char_width + 5) * num_digits, trim_colour, text_colour)
        self.num_digits = num_digits

    def render(self, size: screensize.ScreenSize):
        TOP_PADDING = 2
        BOTTOM_PADDING = 2
        LEFT_PADDING = 2
        RIGHT_PADDING = 2
        out_surf = Surface((self.width, 13))

        for i in range(self.num_digits):
            char_x_start = i * (self.max_char_width + LEFT_PADDING + RIGHT_PADDING + 1)
            draw.rect(out_surf, self.trim_colour, (
            char_x_start, TOP_PADDING, LEFT_PADDING + self.max_char_width + RIGHT_PADDING,
            TOP_PADDING + self.max_char_height + BOTTOM_PADDING), 1)
            if i < len(self.chars):
                render_digit = font_small.render(self.chars[i], False, self.text_colour)
                out_surf.blit(render_digit, (char_x_start + LEFT_PADDING, TOP_PADDING + 1))
        return out_surf

    def add_char(self, char, mod):
        if len(self.chars) < self.num_digits:
            super().add_char(char, mod)

if __name__ == '__main__':
    running = True
    screen = display.set_mode((640, 400))
    screen_surf = Surface((160, 100))
    clockity = time.Clock()
    text = TotpField(6, (150, 150, 150), (230, 230, 230))
    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                if e.key == K_LEFT:
                    text.cursor_left()
                elif e.key == K_RIGHT:
                    text.cursor_right()
                elif e.key == K_BACKSPACE:
                    text.backspace_char()
                elif e.key == K_DELETE:
                    text.delete_char()
                else:
                    text.add_char(e.key, e.mod)

        screen_surf.fill((0, 0, 0))
        rendered_field = text.render(screensize.ScreenSize.SMALL)
        screen_surf.blit(rendered_field, (screen_surf.get_width() // 2 - rendered_field.get_width() // 2,
                                          screen_surf.get_height() // 2 - rendered_field.get_height() // 2))

        screen.blit(transform.scale(screen_surf, (screen.get_width(), screen.get_height())), (0, 0))
        display.flip()
        clockity.tick(30)
    quit()
