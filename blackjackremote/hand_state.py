import enum


class HandState(enum.IntFlag):
    INACTIVE = 0
    STANDING = 1
    ACTIVE = 2
    DOUBLING = 4