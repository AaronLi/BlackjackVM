import pygame

pygame.font.init()

font_small = pygame.font.Font("font/Minecraftia-Regular.ttf", 6)
font_medium = pygame.font.Font("font/Minecraftia-Regular.ttf", 12)
font_large = pygame.font.Font("font/Minecraftia-Regular.ttf", 24)

card_small = pygame.image.load("card_small.png")
card_small_back = pygame.image.load("card_small_back.png")

shekel = pygame.image.load('shekel.png')

class ChipsSmall:
    chips = [
        pygame.image.load("0_chip.png"),
        pygame.image.load("1_chip.png"),
        pygame.image.load("2_chip.png"),
        pygame.image.load("3_chip.png")
    ]

class SuitsSmall:
    spades = pygame.image.load("spades.png")
    clubs = pygame.image.load("clubs.png")
    hearts = pygame.image.load("hearts.png")
    diamonds = pygame.image.load("diamonds.png")
