from typing import Tuple
from data.loader import font_small
from pygame import *

class Button:
    def __init__(self, pos: Rect, label: str, background_colour: Tuple[int, int, int], text_colour: Tuple[int, int, int]) -> None:
        super().__init__()
        self.text_colour = text_colour
        self.background_colour = background_colour
        self.label = label
        self.pos = pos

    def render(self):
        out_surface = Surface(self.pos.size)
        out_surface.fill(self.background_colour)
        button_label = font_small.render(self.label, False, self.text_colour)
        out_surface.blit(button_label, (out_surface.get_width()//2 - button_label.get_width()//2, out_surface.get_height()//2 - button_label.get_height()//2))
        shadow_colour = tuple(channel * 0.7 for channel in self.background_colour)
        draw.line(out_surface, shadow_colour, (0, 0), (0, out_surface.get_height()))
        draw.line(out_surface, shadow_colour, (0, out_surface.get_height()-1), (out_surface.get_width(), out_surface.get_height()-1))
        return out_surface

    def click(self, cx, cy):
        return self.pos.collidepoint(cx, cy)

if __name__ == '__main__':
    running = True
    screen = display.set_mode((640, 400))
    screen_surf = Surface((160, 100))
    clockity = time.Clock()
    button = Button(Rect(60, 40, 40, 15), "Register", (0, 255, 0), (0, 0, 0 ))
    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
            elif e.type == MOUSEBUTTONDOWN:
                if button.click(e.pos[0] * screen_surf.get_width() / screen.get_width(), e.pos[1] * screen_surf.get_height() / screen.get_height()):
                    print("click")
        screen_surf.fill((0, 0, 0))
        rendered_field = button.render()
        screen_surf.blit(rendered_field, button.pos)

        screen.blit(transform.scale(screen_surf, (screen.get_width(), screen.get_height())), (0, 0))
        display.flip()
        clockity.tick(30)
    quit()
