import socketserver
import requests
import pygame
from blackjackremote.blackjackprogram import BlackJackProgram
from data.image_half_colour import OCSimpleImage

BACKEND_IP = ("127.0.0.1", 6525)

class BlackJackVM(socketserver.StreamRequestHandler):
    timeout = 60

    def setup(self) -> None:
        super().setup()

    def handle(self) -> None:
        render_surf = pygame.Surface((160, 100))
        game = BlackJackProgram(render_surf)
        game.render()
        self.wfile.write((OCSimpleImage(render_surf).serialize()+"\n").encode('utf-8'))
        running = True
        while running:
            user_input = self.rfile.readline().decode("utf-8").split(" ")
            if user_input[0] == 'click':
                game.mouse_click(int(user_input[1]), int(user_input[2]))
            elif user_input[0] == 'key':
                game.key_input(int(user_input[1]), int(user_input[2]))
            elif user_input[0] == 'drag':
                game.mouse_relative_move(int(user_input[1]), int(user_input[2]))
            game.render()
            self.wfile.write((OCSimpleImage(render_surf).serialize()+"\n").encode('utf-8'))


    def finish(self) -> None:
        super().finish()


if __name__ == '__main__':
    if hasattr(socketserver, 'ForkingTCPServer'):
        server_backend = socketserver.ForkingTCPServer
    else:
        server_backend = socketserver.ThreadingTCPServer

    with server_backend(("localhost", 9999), BlackJackVM) as server:
        server.serve_forever()
