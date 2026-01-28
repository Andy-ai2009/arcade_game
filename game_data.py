SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Lab Platformer"

PLAYER_SPEED = 5
JUMP_SPEED = 16
GRAVITY = 0.6

IDLE_TRIGGER_TIME = 2.0
BLINK_TIME = 0.4
TELEPORT_TIME = 0.9

FLOOR_TILE = ":resources:images/tiles/brickGrey.png"
PLATFORM_A = ":resources:images/tiles/brickGrey.png"
PLATFORM_B = ":resources:images/tiles/brickTextureWhite.png"
PLAYER_SPRITE = ":resources:images/alien/alienBlue_front.png"
ENEMY_SPRITE = ":resources:images/enemies/fly.png"
SHARD_SPRITE = ":resources:images/items/star.png"
EXIT_SPRITE = ":resources:images/tiles/signExit.png"

LEVEL1 = {
    "world_width": 2200,
    "platform_points": [
        (180, 180), (320, 220), (460, 260), (600, 220), (740, 180),
        (880, 220), (1020, 260), (1160, 220), (1300, 180),
        (1440, 200), (1580, 240), (1720, 180), (1860, 220), (2000, 260), (2140, 220),
    ],
    "unstable": [
        (260, 220, "blink"),
        (520, 220, "blink"),
        (900, 260, "teleport"),
        (1720, 220, "blink"),
    ],
    "shards": [180, 320, 460, 600, 740, 880, 1020, 1160, 1300, 1440, 1580, 1720, 1860, 2000, 2140],
    "enemies": [
        (460, 260, 380, 540),
        (1020, 260, 940, 1100),
        (1700, 240, 1600, 1780),
        (2000, 260, 1900, 2100),
    ],
    "exit_x": 2160,
    "gravity": GRAVITY,
    "ceiling": False,
    "invert_controls": False,
    "flip_player": False,
    "exit_y": 100,
}

LEVEL2 = {
    "world_width": 2200,
    "platform_points": [
        (200, 240), (360, 280), (520, 320), (680, 280), (840, 240),
        (1000, 280), (1160, 320), (1320, 280), (1480, 240),
        (1640, 280), (1800, 320), (1960, 280), (2120, 240),
    ],
    "unstable": [
        (520, 280, "teleport"),
        (1000, 320, "blink"),
        (1640, 280, "teleport"),
    ],
    "shards": [200, 360, 520, 680, 840, 1000, 1160, 1320, 1480, 1640, 1800, 1960, 2120],
    "enemies": [
        (520, 320, 440, 600),
        (1160, 320, 1080, 1240),
        (1800, 320, 1720, 1880),
    ],
    "exit_x": 2100,
    "gravity": -0.3,
    "ceiling": True,
    "invert_controls": True,
    "flip_player": True,
    "exit_y": 480,
}

LEVELS = [LEVEL1, LEVEL2]
