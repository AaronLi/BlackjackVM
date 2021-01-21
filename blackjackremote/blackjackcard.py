import enum
from pygame import *
from virtual_desktop.screensize import ScreenSize
from typing import Tuple, List
from data.loader import font_small, card_small, SuitsSmall, card_small_back


class CardSizes:
    SMALL = (12, 16)


def render(card_value: int, screen_size: ScreenSize):
    if card_value == -1:
        return card_small_back.copy()
    card_suit = Suit.from_card(card_value)
    card_power = Power.from_card(card_value)
    draw_card = card_small.copy()
    card_text_render = font_small.render(card_power.get_char(), False, card_suit.get_colour())
    card_icon = card_suit.get_icon()

    draw_card.blit(card_icon, (1, 1))
    draw_card.blit(card_text_render, (
    draw_card.get_width() - card_text_render.get_width(), draw_card.get_height() - card_text_render.get_height() + 1))
    return draw_card


class Suit(enum.IntEnum):
    HEARTS = 0
    DIAMONDS = 1
    SPADES = 2
    CLUBS = 3

    @staticmethod
    def from_card(card: int) -> "Suit":
        return Suit(card // 13)

    def get_colour(self) -> Tuple[int, int, int]:
        return {
            Suit.HEARTS: (255, 0, 0),
            Suit.DIAMONDS: (255, 0, 0),
            Suit.SPADES: (0, 0, 0),
            Suit.CLUBS: (0, 0, 0)
        }[self]

    def get_icon(self) -> Surface:
        return {
            Suit.HEARTS: SuitsSmall.hearts,
            Suit.DIAMONDS: SuitsSmall.diamonds,
            Suit.SPADES: SuitsSmall.spades,
            Suit.CLUBS: SuitsSmall.clubs
        }[self]


class Power(enum.IntEnum):
    ACE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4
    SIX = 5
    SEVEN = 6
    EIGHT = 7
    NINE = 8
    TEN = 9
    JACK = 10
    QUEEN = 11
    KING = 12

    @staticmethod
    def from_card(card: int) -> "Power":
        return Power(card % 13)

    def get_score(self) -> List[int]:
        if self == Power.ACE:
            return [1, 11]
        elif Power.TWO <= self <= Power.TEN:
            return [self + 1]
        elif self >= Power.TEN:
            return [10]

    def get_char(self):
        return {
            Power.ACE: 'A',
            Power.TWO: '2',
            Power.THREE: '3',
            Power.FOUR: '4',
            Power.FIVE: '5',
            Power.SIX: '6',
            Power.SEVEN: '7',
            Power.EIGHT: '8',
            Power.NINE: '9',
            Power.TEN: '10',
            Power.JACK: 'J',
            Power.QUEEN: 'Q',
            Power.KING: 'K'
        }[self]


if __name__ == '__main__':
    running = True
    screen = display.set_mode((640, 400))
    screen_surf = Surface((160, 100))
    clockity = time.Clock()
    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
        screen_surf.fill((0, 0, 0))
        draw_x = 0
        draw_y = 0
        for card_val in range(52):
            rendered_card = render(card_val, ScreenSize.SMALL)
            if draw_x + rendered_card.get_width() + 1 > screen_surf.get_width():
                draw_x = 0
                draw_y += rendered_card.get_height() + 1
            screen_surf.blit(rendered_card, (draw_x, draw_y))
            draw_x += rendered_card.get_width() + 1
        screen.blit(transform.scale(screen_surf, (screen.get_width(), screen.get_height())), (0, 0))
        display.flip()
        clockity.tick(30)
    quit()
