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

PLATFORM_POINTS = [
    (180, 180), (320, 220), (460, 260), (600, 220), (740, 180),
    (880, 220), (1020, 260), (1160, 220), (1300, 180),
]

UNSTABLE_PLATFORMS = [
    (260, 220, "blink"),
    (520, 220, "blink"),
    (900, 260, "teleport"),
]

SHARD_X = [180, 320, 460, 600, 740, 880, 1020, 1160, 1300]

ENEMIES = [
    (460, 260, 380, 540),
    (1020, 260, 940, 1100),
]

FLOOR_TILE = ":resources:images/tiles/brickGrey.png"
PLATFORM_A = ":resources:images/tiles/brickGrey.png"
PLATFORM_B = ":resources:images/tiles/brickTextureWhite.png"
PLAYER_SPRITE = ":resources:images/alien/alienBlue_front.png"
ENEMY_SPRITE = ":resources:images/enemies/fly.png"
SHARD_SPRITE = ":resources:images/items/star.png"
EXIT_SPRITE = ":resources:images/tiles/signExit.png"
