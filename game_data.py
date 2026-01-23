import arcade

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Lab Platformer"

PLAYER_SPEED = 5
JUMP_SPEED = 16
GRAVITY = 0.6

IDLE_TRIGGER_TIME = 2.0
BLINK_TIME = 0.4
TELEPORT_TIME = 0.9

WORLD_WIDTH = 2200

PLATFORM_POINTS = [
    (180, 180), (320, 220), (460, 260), (600, 220), (740, 180),
    (880, 220), (1020, 260), (1160, 220), (1300, 180),
    (1440, 200), (1580, 240), (1720, 180), (1860, 220), (2000, 260), (2140, 220),
]

UNSTABLE_PLATFORMS = [
    (260, 220, "blink"),
    (520, 220, "blink"),
    (900, 260, "teleport"),
    (1720, 220, "blink"),
]

SHARD_X = [180, 320, 460, 600, 740, 880, 1020, 1160, 1300, 1440, 1580, 1720, 1860, 2000, 2140]

ENEMIES = [
    (460, 260, 380, 540),
    (1020, 260, 940, 1100),
    (1700, 240, 1600, 1780),
    (2000, 260, 1900, 2100),
]

FLOOR_TILE = ":resources:images/tiles/brickGrey.png"
PLATFORM_A = ":resources:images/tiles/brickGrey.png"
PLATFORM_B = ":resources:images/tiles/brickTextureWhite.png"
PLAYER_SPRITE = ":resources:images/alien/alienBlue_front.png"
ENEMY_SPRITE = ":resources:images/enemies/fly.png"
SHARD_SPRITE = ":resources:images/items/star.png"
EXIT_SPRITE = ":resources:images/tiles/signExit.png"
EXIT_X = 2160
