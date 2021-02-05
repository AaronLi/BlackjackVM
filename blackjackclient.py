import socket

from pygame import *

from data import OCSimpleImage

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(("blackjack.dumfing.com", 6525))
    running = True
    screen = display.set_mode((640, 400))
    screen_surf = Surface((160, 100))
    clockity = time.Clock()
    receive_buffer = bytearray()
    sock.setblocking(False)
    display.set_icon(image.load('1_chip.png'))
    display.set_caption("Dumfing's Blackjack")
    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN:
                sock.send(f"key {e.key} {e.mod}\n".encode("utf-8"))
            elif e.type == MOUSEBUTTONDOWN:
                sock.send(f"click {e.pos[0] // 4} {e.pos[1] // 4}\n".encode("utf-8"))

        try:
            receive_buffer.extend(sock.recv(8192))
        except BlockingIOError:
            pass
        frames = receive_buffer.split(b"\n")
        if len(frames) > 1:
            screen_surf = OCSimpleImage().deserialize(frames[0].decode('utf-8')).get_surface()
            receive_buffer = bytearray(b'\n'.join(frames[1:]))

            screen.blit(transform.scale(screen_surf, (screen.get_width(), screen.get_height())), (0, 0))
            display.flip()
        clockity.tick(30)
    quit()
