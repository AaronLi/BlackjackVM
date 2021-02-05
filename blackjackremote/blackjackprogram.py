import itertools
from collections import deque, namedtuple
from io import BytesIO
from typing import Tuple, List

import requests
from PIL import Image
from pygame import *
from pygame import gfxdraw

from blackjackremote import blackjackcard
from blackjackremote.hand_state import HandState
from data.image_half_colour import OCSimpleImage
from data.loader import font_small, font_large, ChipsSmall, shekel
from virtual_desktop.button import Button
from virtual_desktop.coin_button import CoinButton
from virtual_desktop.screensize import ScreenSize
from virtual_desktop.text_field import TextField
from virtual_desktop.totp_field import TotpField
from virtual_desktop.window import Window

BLACKJACK_BACKEND = ("127.0.0.1", 6595)
SimpleHandState = namedtuple("SimpleHandState", ("hand_state", "bet", "cards"))


class BlackJackProgram(Window):
    def __init__(self, window_surface: Surface) -> None:
        super().__init__(window_surface)
        self.login_button = Button(Rect(self.screen.get_width() // 2 - 42, self.screen.get_height() // 2 + 5, 40, 13),
                                   "Login", (255, 255, 255), (0, 0, 0))
        self.register_button = Button(Rect(self.screen.get_width() // 2 + 2, self.screen.get_height() // 2 + 5, 40, 13),
                                      "Register", (255, 255, 255), (0, 0, 0))
        self.scanned_button = Button(Rect(self.screen.get_width() // 2 - 30, self.screen.get_height() - 11, 60, 10),
                                     "Scanned it!", (0, 255, 0), (255, 255, 255))
        self.login_submit_button = Button(
            Rect(self.screen.get_width() // 2 - 20, self.screen.get_height() - 40, 40, 13), "Login", (255, 255, 255),
            (0, 0, 0))
        self.cancel_totp_button = Button(Rect(2, 2, 9, 12), "←", (0, 0, 0), (255, 255, 255))
        self.submit_bet_button = Button(Rect(self.screen.get_width() // 2 - 25, self.screen.get_height() - 12, 50, 11),
                                        "Submit  Bet", (0, 255, 0), (0, 0, 0))

        self.add_coins = [
            CoinButton((self.screen.get_width() // 2 + 2, self.screen.get_height() - 36), "TBD", ChipsSmall.chips[0],
                       (220, 190, 80)),
            CoinButton((self.screen.get_width() // 2 + 20, self.screen.get_height() - 36), "TBD", ChipsSmall.chips[1],
                       (220, 190, 80)),
            CoinButton((self.screen.get_width() // 2 + 38, self.screen.get_height() - 36), "TBD", ChipsSmall.chips[2],
                       (220, 190, 80)),
            CoinButton((self.screen.get_width() // 2 + 56, self.screen.get_height() - 36), "TBD", ChipsSmall.chips[3],
                       (220, 190, 80))
        ]
        self.remove_coins = [
            CoinButton((self.screen.get_width() // 2 - 18, self.screen.get_height() - 36), "TBD", ChipsSmall.chips[0],
                       (220, 190, 80)),
            CoinButton((self.screen.get_width() // 2 - 36, self.screen.get_height() - 36), "TBD", ChipsSmall.chips[1],
                       (220, 190, 80)),
            CoinButton((self.screen.get_width() // 2 - 54, self.screen.get_height() - 36), "TBD", ChipsSmall.chips[2],
                       (220, 190, 80)),
            CoinButton((self.screen.get_width() // 2 - 72, self.screen.get_height() - 36), "TBD", ChipsSmall.chips[3],
                       (220, 190, 80))
        ]

        self.acknowledge_button = Button(Rect(self.screen.get_width()//2 - 20, self.screen.get_height()-13, 40, 12), "Ok", (100, 255, 100), (255, 255, 255))
        self.play_again_yes_button = Button(Rect(self.screen.get_width()//2 - 42, self.screen.get_height()//2 - 6, 40, 12), "Yes", (90, 255, 90), (255, 255, 255))
        self.play_again_no_button = Button(Rect(self.screen.get_width()//2 + 2, self.screen.get_height()//2 - 6, 40, 12), "No", (255, 90, 90), (255, 255, 255))
        self.exit_button = Button(Rect(self.screen.get_width() - 17, 1, 16, 12), "X", (255,0, 0), (255, 255, 255))
        self.username_field = TextField(84, (255, 255, 255), (255, 255, 255))
        self.totp_field = TotpField(6, (255, 255, 255), (255, 255, 255))
        self.username = None
        self.auth = None
        self.login_error_text = None
        self.registration_qr = None
        self.game_state = None

    def mouse_click(self, mx, my) -> None:
        super().mouse_click(mx, my)
        if self.auth is None:
            if self.username is None:
                if self.registration_qr is None:
                    if self.login_button.click(mx, my):
                        self.username = self.username_field.get_string()
                    elif self.register_button.click(mx, my):
                        response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/auth/register",
                                                 {"username": self.username_field.get_string()}).text.split("\n")
                        if response[0] == "failed":
                            self.login_error_text = response[1]
                        elif response[0] == "success":
                            self.registration_qr = response[1]
                            self.login_error_text = None
                else:
                    if self.scanned_button.click(mx, my):
                        self.registration_qr = None
            else:
                if self.login_submit_button.click(mx, my) and len(self.totp_field.chars) == self.totp_field.num_digits:
                    response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/auth/login",
                                             {"username": self.username,
                                              "totp": self.totp_field.get_string()}).text.split('\n')
                    self.totp_field.clear()
                    if response[0] == 'failed':
                        self.login_error_text = response[1]
                        self.username = None
                    elif response[0] == 'success':
                        self.auth = response[1]
                        response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                                 {"username": self.username, "auth": self.auth, "action": "poll"})
                        self.game_state = response.text
                elif self.cancel_totp_button.click(mx, my):
                    self.username = None
                    self.totp_field.clear()
                    self.username_field.clear()

        else:
            game_phase = self.get_game_phase()
            if self.exit_button.click(mx, my):
                self.reset()
                return
            if game_phase == "betting":
                for amount, button in itertools.chain(zip(self.get_positive_bets(), self.add_coins),
                                                      zip(self.get_negative_bets(), self.remove_coins)):
                    if button.click(mx, my):
                        response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                                 {'username': self.username, 'auth': self.auth, "action": "input",
                                                  "move": amount[1]}).text
                        if response.split("\n")[0] == "success":
                            self.game_state = response

                if self.submit_bet_button.click(mx, my):
                    response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                             {'username': self.username, 'auth': self.auth, "action": "input",
                                              "move": "submitbet"}).text
                    if response.split("\n")[0] == "success":
                        self.game_state = response
            elif game_phase == 'playermove':
                for button, command, enabled in self.get_move_buttons()[1]:
                    if enabled:
                        if button.click(mx, my):
                            response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                                     {'username': self.username, 'auth': self.auth, "action": "input",
                                                      "move": command}).text
                            if response.split("\n")[0] == "success":
                                self.game_state = response
            elif game_phase == 'dealermove':
                if self.acknowledge_button.click(mx, my):
                    response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                             {'username': self.username, 'auth': self.auth, "action": "input",
                                              "move": 'ack'}).text
                    if response.split('\n')[0] == 'success':
                        self.game_state = response

            elif game_phase == 'payout':
                if self.acknowledge_button.click(mx, my):
                    response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                             {'username': self.username, 'auth': self.auth, "action": "input",
                                              "move": 'ack'}).text
                    if response.split('\n')[0] == 'success':
                        self.game_state = response
            elif game_phase == 'continueplaying':
                if self.play_again_yes_button.click(mx, my):
                    response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                             {'username': self.username, 'auth': self.auth, "action": "input",
                                              "move": 'yes'}).text
                    if response.split('\n')[0] == 'success':
                        self.game_state = response
                elif self.play_again_no_button.click(mx, my):
                    response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                             {'username': self.username, 'auth': self.auth, "action": "input",
                                              "move": 'no'}).text
                    if response.split('\n')[0] == 'success':
                        if response.split('\n')[1] == 'GAME OVER':
                            self.reset()

    def reset(self):
        self.auth = None
        self.username = None
        self.registration_qr = None
        self.game_state = None
        self.login_error_text = None
        self.totp_field.clear()
        self.username_field.clear()

    def get_current_game_state(self):
        response = requests.post(f"http://{BLACKJACK_BACKEND[0]}:{BLACKJACK_BACKEND[1]}/game/blackjack",
                                 {"username": self.username, "auth": self.auth, "action": "poll"}).text
        split_response = response.split("\n")
        response_success = split_response[0]
        if response_success == "success":
            self.game_state = response
        else:
            self.auth = None
        self.game_state = response

    def key_input(self, keycode, mod) -> None:
        super().key_input(keycode, mod)
        print(self.username_field.get_string())
        if self.auth is None:
            if self.username is None:
                if self.registration_qr is None:
                    if keycode == K_LEFT:
                        self.username_field.cursor_left()
                    elif keycode == K_RIGHT:
                        self.username_field.cursor_right()
                    elif keycode == K_BACKSPACE:
                        self.username_field.backspace_char()
                    elif keycode == K_DELETE:
                        self.username_field.delete_char()
                    else:
                        self.username_field.add_char(keycode, mod)
            else:
                if keycode == K_LEFT:
                    self.totp_field.cursor_left()
                elif keycode == K_RIGHT:
                    self.totp_field.cursor_right()
                elif keycode == K_BACKSPACE:
                    self.totp_field.backspace_char()
                elif keycode == K_DELETE:
                    self.totp_field.delete_char()
                else:
                    self.totp_field.add_char(keycode, mod)

    def render(self) -> None:
        super().render()
        if self.auth is None:
            if self.username is None:
                # still have to select login or register
                self.screen.fill((0, 0, 0))
                if self.registration_qr is None:
                    self.screen.blit(self.login_button.render(), self.login_button.pos)
                    self.screen.blit(self.register_button.render(), self.register_button.pos)

                    rendered_username_prompt = self.username_field.render(ScreenSize.SMALL)

                    render_prompt = font_small.render("Login/Register", False, (255, 255, 255))
                    self.screen.blit(render_prompt, (self.screen.get_width() // 2 - render_prompt.get_width() // 2,
                                                     self.screen.get_height() // 2 - render_prompt.get_height() - rendered_username_prompt.get_height()))
                    self.screen.blit(rendered_username_prompt, (
                        self.screen.get_width() // 2 - rendered_username_prompt.get_width() // 2,
                        self.screen.get_height() // 2 - rendered_username_prompt.get_height()))
                    if self.login_error_text:
                        rendered_reason = font_small.render(self.login_error_text, False, (255, 0, 0))
                        self.screen.blit(rendered_reason, (
                            self.screen.get_width() // 2 - rendered_reason.get_width() // 2,
                            self.screen.get_height() - rendered_reason.get_height() - 1))
                else:
                    registration_qr = OCSimpleImage().deserialize(self.registration_qr, 2).get_surface()
                    draw.rect(self.screen, (255, 255, 255), (
                        self.screen.get_width() // 2 - registration_qr.get_width() // 2, 0, registration_qr.get_width(),
                        self.screen.get_height()))
                    self.screen.blit(registration_qr,
                                     (self.screen.get_width() // 2 - registration_qr.get_width() // 2, 0))

                    self.screen.blit(self.scanned_button.render(), self.scanned_button.pos)
                    # rendered_qr_label = font_mono_light.render(f"Use a 2FA app", False, (0, 0, 0))
                    # self.screen.blit(rendered_qr_label, (self.screen.get_width()//2 - rendered_qr_label.get_width()//2, self.screen.get_height() - rendered_qr_label.get_height() - 1))
            else:
                self.screen.fill((0, 0, 0))
                rendered_totp_field = self.totp_field.render(ScreenSize.SMALL)
                self.screen.blit(rendered_totp_field, (
                    self.screen.get_width() // 2 - rendered_totp_field.get_width() // 2,
                    self.screen.get_height() // 2 - rendered_totp_field.get_height() // 2))
                prompt_text = font_small.render(f"Enter the TOTP for {self.username}", False, (255, 255, 255))
                self.screen.blit(prompt_text, (self.screen.get_width() // 2 - prompt_text.get_width() // 2,
                                               self.screen.get_height() // 2 - rendered_totp_field.get_height() // 2 - prompt_text.get_height() - 1))
                self.screen.blit(self.login_submit_button.render(), self.login_submit_button.pos)
                self.screen.blit(self.cancel_totp_button.render(), self.cancel_totp_button.pos)
        else:
            self.screen.fill((0, 120, 0))
            game_data = self.game_state.split("\n")
            game_phase = self.get_game_phase()
            if game_phase != "GAME":
                bets = self.get_bets()
                if bets:
                    rendered_bet = font_small.render(f"Bets:", False, (255, 255, 255))
                    self.screen.blit(rendered_bet, (1, 1))
                    y_height = 1 + rendered_bet.get_height()
                    for i, bet in enumerate(bets):
                        rendered_bet = font_small.render(f"Hand {i+1}: {bet}", False, (255, 255, 255))
                        self.screen.blit(rendered_bet, (1, y_height))
                        y_height += rendered_bet.get_height()
            if game_phase == "betting":
                bet_amount = int(game_data[1].split(" ")[1])
                moves = game_data[2].strip().split(" ")
                num_bet_options = moves[1]
                bet_options = moves[2:]
                bet_text = font_small.render("Place a bet!", False, (255, 255, 255))
                self.screen.blit(bet_text, (self.screen.get_width() // 2 - bet_text.get_width() // 2, 5))

                bet_amount_text = font_large.render(str(bet_amount), False, (255, 255, 255))
                self.screen.blit(bet_amount_text, (
                    self.screen.get_width() // 2 - bet_amount_text.get_width() // 2, 6 + bet_text.get_height()))
                if bet_options != ['0']:
                    if 'submitbet' in bet_options:
                        self.submit_bet_button.background_colour = (255, 255, 255)
                        self.submit_bet_button.text_colour = (0, 0, 0)
                    else:
                        self.submit_bet_button.background_colour = (150, 150, 150)
                        self.submit_bet_button.text_colour = (180, 180, 180)
                    self.screen.blit(self.submit_bet_button.render(), self.submit_bet_button.pos)
                    for amount, button in zip(self.get_positive_bets(), self.add_coins):
                        button.label = f"+{amount[0]}"
                        self.screen.blit(button.render(), button.pos)

                    for amount, button in zip(self.get_negative_bets(), self.remove_coins):
                        button.label = amount[0]
                        self.screen.blit(button.render(), button.pos)
                else:
                    print("Not enough funds")
            elif game_phase == 'playermove':
                num_active_hands, hands = self.get_player_hands()
                hand_offset_x = self.screen.get_width() // (num_active_hands + 1)
                active_hand, move_buttons = self.get_move_buttons()
                for i, hand in enumerate(hands):
                    hand_center = hand_offset_x * (i + 1)
                    if hand.hand_state & HandState.ACTIVE:
                        min_hand_x = 0
                        max_hand_x = 0
                        card_height = 0
                        for j, card in enumerate(hand.cards):
                            rendered_card = blackjackcard.render(card, ScreenSize.SMALL)
                            card_offset_x = int(-len(hand.cards) / 2 * rendered_card.get_width() + (
                                    rendered_card.get_width() + 1) * j)
                            self.screen.blit(rendered_card, (hand_center + card_offset_x,
                                                             self.screen.get_height() // 2 - rendered_card.get_height() // 2 + 23))
                            min_hand_x = min(min_hand_x, card_offset_x)
                            max_hand_x = max(max_hand_x, card_offset_x + rendered_card.get_width())
                            card_height = rendered_card.get_height()
                        if not (hand.hand_state & HandState.STANDING) and i == active_hand:
                            draw.rect(self.screen, (100, 100, 255), (hand_center + min_hand_x - 2, self.screen.get_height()//2 - card_height//2 + 21, max_hand_x - min_hand_x + 4, 20), 1)
                self.draw_dealer_hand()

                for button, command, button_enabled in move_buttons:
                    self.screen.blit(button.render(), button.pos)

                current_game_phase_render = font_small.render("Your Move", False, (255, 255, 255))
                self.screen.blit(current_game_phase_render, (self.screen.get_width()//2 - current_game_phase_render.get_width()//2, 1))
            elif game_phase == 'dealermove':
                self.basic_draw_game()

                self.screen.blit(self.acknowledge_button.render(), self.acknowledge_button.pos)

                current_game_phase_render = font_small.render("Dealer's Move", False, (255, 255, 255))
                self.screen.blit(current_game_phase_render, (self.screen.get_width()//2 - current_game_phase_render.get_width()//2, 1))
            elif game_phase == 'payout':

                game_result = self.game_state.split("\n")[2].split(" ")
                if game_result[0] == 'won':
                    self.screen.fill((50, 210, 235))
                    self.screen.blit(self.acknowledge_button.render(), self.acknowledge_button.pos)

                    current_game_phase_render = font_small.render("Payout", False, (255, 255, 255))
                    self.screen.blit(current_game_phase_render, (self.screen.get_width()//2 - current_game_phase_render.get_width()//2, 1))

                    victory_text = font_large.render("You Won!", False, (255, 255, 255))
                    self.screen.blit(victory_text, (self.screen.get_width()//2 - victory_text.get_width()//2, 5 + current_game_phase_render.get_height()))

                    winnings_amount = font_large.render(game_result[1], False, (255, 255, 255))
                    self.screen.blit(winnings_amount, (self.screen.get_width()//2 - winnings_amount.get_width()//2, victory_text.get_height() + current_game_phase_render.get_height()))
                    self.screen.blit(shekel, (self.screen.get_width()//2 + winnings_amount.get_width()//2 + 2, 8 + victory_text.get_height() + current_game_phase_render.get_height()))
                elif game_result[0] == 'tie':
                    self.screen.fill((150, 150, 150))
                    self.screen.blit(self.acknowledge_button.render(), self.acknowledge_button.pos)

                    current_game_phase_render = font_small.render("Payout", False, (255, 255, 255))
                    self.screen.blit(current_game_phase_render, (self.screen.get_width()//2 - current_game_phase_render.get_width()//2, 1))

                    victory_text = font_large.render("Tie", False, (255, 255, 255))
                    self.screen.blit(victory_text, (self.screen.get_width()//2 - victory_text.get_width()//2, 5 + current_game_phase_render.get_height()))
                elif game_result[0] == 'loss':
                    self.screen.fill((150, 100, 100))
                    self.screen.blit(self.acknowledge_button.render(), self.acknowledge_button.pos)

                    current_game_phase_render = font_small.render("Payout", False, (255, 255, 255))
                    self.screen.blit(current_game_phase_render, (self.screen.get_width()//2 - current_game_phase_render.get_width()//2, 1))

                    victory_text = font_large.render("You Lose", False, (255, 255, 255))
                    self.screen.blit(victory_text, (self.screen.get_width()//2 - victory_text.get_width()//2, 5 + current_game_phase_render.get_height()))
            elif game_phase == 'continueplaying':
                self.basic_draw_game()
                gfxdraw.box(self.screen, (10, 10, self.screen.get_width() - 20 , self.screen.get_height() - 20), (0, 0, 0, 220))

                play_again_prompt = font_small.render("Play Again?", False, (255, 255, 255))
                self.screen.blit(play_again_prompt, (self.screen.get_width()//2 - play_again_prompt.get_width()//2, 22))
                self.screen.blit(self.play_again_yes_button.render(), self.play_again_yes_button.pos)
                self.screen.blit(self.play_again_no_button.render(), self.play_again_no_button.pos)
            self.screen.blit(self.exit_button.render(), self.exit_button.pos)

    def draw_dealer_hand(self):
        dealer_hand = self.get_dealer_hand().cards
        for i, card in enumerate(dealer_hand):
            rendered_card = blackjackcard.render(card, ScreenSize.SMALL)
            card_offset_x = int(-len(dealer_hand) / 2 * rendered_card.get_width() + (
                    rendered_card.get_width() + 1) * i)
            self.screen.blit(rendered_card, (self.screen.get_width() // 2 + card_offset_x,
                                             self.screen.get_height() // 2 - rendered_card.get_height() // 2 - 23))

    def basic_draw_game(self):
        num_active_hands, hands = self.get_player_hands()
        hand_offset_x = self.screen.get_width() // (num_active_hands + 1)
        for i, hand in enumerate(hands):
            hand_center = hand_offset_x * (i + 1)
            if hand.hand_state & HandState.ACTIVE:
                for j, card in enumerate(hand.cards):
                    rendered_card = blackjackcard.render(card, ScreenSize.SMALL)
                    card_offset_x = int(-len(hand.cards) / 2 * rendered_card.get_width() + (
                            rendered_card.get_width() + 1) * j)
                    self.screen.blit(rendered_card, (hand_center + card_offset_x,
                                                     self.screen.get_height() // 2 - rendered_card.get_height() // 2 + 23))

        self.draw_dealer_hand()

    def get_positive_bets(self):
        moves_line = self.game_state.split("\n")[2].split(" ")
        num_moves = moves_line[1]
        moves = moves_line[2:]
        return [(move[3:], move) for move in moves if move[0:3] == "bet" and move[3] != '-']

    def get_negative_bets(self):
        moves_line = self.game_state.split("\n")[2].split(" ")
        num_moves = moves_line[1]
        moves = moves_line[2:]
        return [(move[3:], move) for move in moves if move[0:3] == "bet" and move[3] == '-']

    def get_player_hands(self) -> Tuple[int, List[SimpleHandState]]:
        hand_data = self.game_state.split("\n")[2].split(" ")
        num_hands = int(hand_data[1])
        hand_stack = deque(hand_data[2:])  # TODO: replace deque with pointer and move pointer instead of pop from deque
        hands_out = []
        num_active = 0
        for i in range(num_hands):
            hand_state = HandState(int(hand_stack.popleft()))
            if hand_state & HandState.ACTIVE:
                num_active += 1
            hand_bet = int(hand_stack.popleft())
            num_cards = int(hand_stack.popleft())
            cards = [int(hand_stack.popleft()) for _ in range(num_cards)]
            hands_out.append(SimpleHandState(hand_state, hand_bet, cards))
        return num_active, hands_out

    def get_dealer_hand(self) -> SimpleHandState:
        hand_data = self.game_state.split("\n")[3].split(" ")
        num_cards = int(hand_data[1])
        cards = [int(i) for i in hand_data[2:]]
        return SimpleHandState(HandState.ACTIVE, 0, cards)

    def get_game_phase(self):
        game_data = self.game_state.split("\n")
        return game_data[1].split(" ")[0]

    def get_move_buttons(self):
        num_active_hands = self.get_player_hands()[0]
        buttons = {
            "hit": Button(Rect(self.screen.get_width()//2 - 63, self.screen.get_height() - 11, 30, 10), "Hit", (0, 255, 0), (0, 0, 0)),
            "double": Button(Rect(self.screen.get_width()//2 - 31, self.screen.get_height() - 11, 30, 10), "Double", (0, 0, 255), (0, 0, 0)),
            "stand": Button(Rect(self.screen.get_width()//2 + 1, self.screen.get_height() - 11, 30, 10), "Stand", (255, 0, 0), (0, 0, 0)),
            "split": Button(Rect(self.screen.get_width()//2 + 33, self.screen.get_height() - 11, 30, 10), "Split", (255, 180, 80), (0, 0, 0))
        }

        active_hand = None
        possible_moves = self.game_state.split("\n")[4].strip().split(" ")[2:]
        for move in possible_moves:
            move_hand = int(move[-1])
            if active_hand is not None:
                assert active_hand == move_hand
            else:
                active_hand = move_hand
        enabled = set()
        for move in possible_moves:
            buttons[move[:-2]].text_colour = (255, 255, 255)
            enabled.add(move[:-2])
        return active_hand, ((buttons['hit'], f"hit_{active_hand}", 'hit' in enabled), (buttons['double'], f"double_{active_hand}", 'double' in enabled), (buttons['stand'], f"stand_{active_hand}", 'stand' in enabled), (buttons['split'], f"split_{active_hand}", 'split' in enabled))

    def get_bets(self):
        game_phase = self.get_game_phase()
        if game_phase == 'continueplaying' or game_phase == 'betting' or game_phase == 'payout':
            return None
        else:
            player_hand_info = self.get_player_hands()
            return [hand.bet * (2 if hand.hand_state & HandState.DOUBLING else 1) for hand in player_hand_info[1] if hand.bet > 0]

    def log_out(self):
        self.username = None
        self.auth = None


if __name__ == '__main__':
    running = True
    screen = display.set_mode((640, 400))
    screen_surf = Surface((160, 100))
    clockity = time.Clock()
    game = BlackJackProgram(screen_surf.subsurface((0, 0, 160, 100)))
    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                game.key_input(e.key, e.mod)
            elif e.type == MOUSEBUTTONDOWN:
                game.mouse_click(e.pos[0] // 4, e.pos[1] // 4)

        game.render()

        screen.blit(transform.scale(screen_surf, (screen.get_width(), screen.get_height())), (0, 0))
        display.flip()
        clockity.tick(30)
    quit()



