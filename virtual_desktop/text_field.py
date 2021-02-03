from typing import Tuple

from pygame import *
from virtual_desktop import screensize
from data.loader import font_small


class TextField:
    charmap = {
        (45, 1): "_",
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
        (97, 0): 'a',
        (97, 1): 'A',
        (98, 0): 'b',
        (98, 1): 'B',
        (99, 0): 'c',
        (99, 1): 'C',
        (100, 0): 'd',
        (100, 1): 'D',
        (101, 0): 'e',
        (101, 1): 'E',
        (102, 0): 'f',
        (102, 1): 'F',
        (103, 0): 'g',
        (103, 1): 'G',
        (104, 0): 'h',
        (104, 1): 'H',
        (105, 0): 'i',
        (105, 1): 'I',
        (106, 0): 'j',
        (106, 1): 'J',
        (107, 0): 'k',
        (107, 1): 'K',
        (108, 0): 'l',
        (108, 1): 'L',
        (109, 0): 'm',
        (109, 1): 'M',
        (110, 0): 'n',
        (110, 1): 'N',
        (111, 0): 'o',
        (111, 1): 'O',
        (112, 0): 'p',
        (112, 1): 'P',
        (113, 0): 'q',
        (113, 1): 'Q',
        (114, 0): 'r',
        (114, 1): 'R',
        (115, 0): 's',
        (115, 1): 'S',
        (116, 0): 't',
        (116, 1): 'T',
        (117, 0): 'u',
        (117, 1): 'U',
        (118, 0): 'v',
        (118, 1): 'V',
        (119, 0): 'w',
        (119, 1): 'W',
        (120, 0): 'x',
        (120, 1): 'X',
        (121, 0): 'y',
        (121, 1): 'Y',
        (122, 0): 'z',
        (122, 1): 'Z',
    }

    def __init__(self, field_width: int, trim_colour: Tuple[int, int, int], text_colour: Tuple[int, int, int]) -> None:
        super().__init__()
        self.chars = []
        self.cursor_pos = 0
        self.width = field_width
        self.trim_colour = trim_colour
        self.text_colour = text_colour

    def render(self, size: screensize.ScreenSize):
        TOP_PADDING = 2
        BOTTOM_PADDING = 2
        LEFT_PADDING = 2
        RIGHT_PADDING = 2
        draw_surf = Surface((self.width, 13))
        draw.rect(draw_surf, self.trim_colour, (0, 0, draw_surf.get_width(), draw_surf.get_height()), width=1)
        text_to_render = self.get_string()
        render_text = font_small.render(text_to_render, False, self.text_colour)
        draw_surf.blit(render_text, (TOP_PADDING, LEFT_PADDING))
        text_metrics = font_small.metrics(text_to_render)
        char_x = 0
        char_w = text_metrics[0][1] if len(text_metrics) > 0 else 4
        for c_ind in range(self.cursor_pos):
            char_w = text_metrics[c_ind][4]
            char_x += char_w

        # print(char_x, char_w, text_metrics)
        # draw.rect(draw_surf, self.text_colour, (char_x + LEFT_PADDING, TOP_PADDING + render_text.get_height(), char_w, 2))
        draw.rect(draw_surf, self.text_colour, (char_x + LEFT_PADDING, TOP_PADDING, 1, render_text.get_height()))
        return draw_surf

    def add_char(self, keycode, mod):
        try:
            self.chars.insert(self.cursor_pos, self.charmap[(keycode, mod & 0x1)])
            self.cursor_pos += 1
        except KeyError:
            print("unknown", keycode, mod)
            return

    def backspace_char(self):
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
            del self.chars[self.cursor_pos]

    def delete_char(self):
        if self.cursor_pos < len(self.chars):
            del self.chars[self.cursor_pos]

    def cursor_left(self):
        self.cursor_pos = max(0, self.cursor_pos - 1)

    def cursor_right(self):
        self.cursor_pos = min(len(self.chars), self.cursor_pos + 1)

    def get_string(self):
        return ''.join(self.chars)

    def clear(self):
        self.chars = []
        self.cursor_pos = 0

if __name__ == '__main__':
    running = True
    screen = display.set_mode((640, 400))
    screen_surf = Surface((160, 100))
    clockity = time.Clock()
    text = TextField(100, (200, 200, 200), (230, 230, 230))
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
