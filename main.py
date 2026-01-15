import math
import random
import arcade
from arcade.camera import Camera2D

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Broken Lab Platformer"

PLAYER_SPEED = 5
JUMP_SPEED = 18
BASE_GRAVITY = 0.6

ENEMY_BULLET_SPEED = 6
PLAYER_MAX_HEALTH = 100

IDLE_TRIGGER_TIME = 2.0
UNSTABLE_BLINK_TIME = 0.35
UNSTABLE_TELEPORT_TIME = 0.9

GLITCH_POINT_MAX = 160

ENEMY_TIERS = {
    1: {"speed": 0.9, "fire_rate": 4.5},
    2: {"speed": 1.2, "fire_rate": 3.8},
    3: {"speed": 1.6, "fire_rate": 3.2},
}

LEVELS = [
    {
        "world_width": 2400,
        "spawn": (80, 140),
        "platforms": [
            (140, 180), (260, 220), (380, 260), (520, 200), (660, 240),
            (800, 180), (940, 220), (1080, 260), (1220, 200), (1360, 240),
            (1500, 180), (1640, 220), (1780, 260), (1920, 200), (2060, 240),
            (2200, 180),
        ],
        "unstable": [
            {"pos": (260, 220), "mode": "blink"},
            {"pos": (520, 220), "mode": "blink"},
            {"pos": (900, 220), "mode": "blink"},
            {"pos": (1540, 300), "mode": "teleport"},
        ],
        "shards": [
            140, 260, 380, 520, 660, 800, 940, 1080, 1220,
            1360, 1500, 1640, 1780, 1920, 2060, 2200,
            260, 620, 980, 1400, 1700, 1980, 2280,
        ],
        "enemies": [
            {"pos": (520, 240), "patrol": (440, 600), "tier": 1},
            {"pos": (1080, 260), "patrol": (1000, 1180), "tier": 2},
            {"pos": (1640, 220), "patrol": (1560, 1720), "tier": 2},
            {"pos": (2060, 240), "patrol": (1980, 2140), "tier": 3},
        ],
        "glitch_zones": [
            (420, 32, 180, 140, "invert"),
            (740, 32, 200, 140, "heavy"),
            (1520, 32, 220, 140, "low"),
        ],
        "exit": (2320, 100),
    },
]


class StartView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "BROKEN LAB",
            self.window.width / 2,
            self.window.height / 2 + 40,
            arcade.color.WHITE,
            32,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press any key to start",
            self.window.width / 2,
            self.window.height / 2 - 20,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        game_view = GameView(level_index=0)
        game_view.setup()
        self.window.show_view(game_view)


class GameOverView(arcade.View):
    def __init__(self, level_index):
        super().__init__()
        self.level_index = level_index

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "GAME OVER",
            self.window.width / 2,
            self.window.height / 2 + 20,
            arcade.color.RED,
            30,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press R to retry",
            self.window.width / 2,
            self.window.height / 2 - 20,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            game_view = GameView(level_index=self.level_index)
            game_view.setup()
            self.window.show_view(game_view)


class WinView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "YOU RESTORED THE LAB",
            self.window.width / 2,
            self.window.height / 2 + 20,
            arcade.color.WHITE,
            26,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press R to play again",
            self.window.width / 2,
            self.window.height / 2 - 20,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            game_view = GameView(level_index=0)
            game_view.setup()
            self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self, level_index=0):
        super().__init__()
        self.level_index = level_index

        self.player = None
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.enemy_bullets = arcade.SpriteList()
        self.shard_list = arcade.SpriteList()
        self.exit_list = arcade.SpriteList()
        self.unstable_list = arcade.SpriteList()

        self.physics_engine = None

        self.keys_pressed = set()
        self.shards_collected = 0
        self.shards_required = 0
        self.player_health = PLAYER_MAX_HEALTH
        self.exit_open = False

        self.idle_time = 0.0
        self.glitch_zones = []
        self.gravity = BASE_GRAVITY
        self.background = None

        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.world_width = SCREEN_WIDTH
        self.world_height = SCREEN_HEIGHT

        self.text_shards = None
        self.text_health = None
        self.text_level = None

    def setup(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.enemy_bullets = arcade.SpriteList()
        self.shard_list = arcade.SpriteList()
        self.exit_list = arcade.SpriteList()
        self.unstable_list = arcade.SpriteList()

        self.shards_collected = 0
        self.player_health = PLAYER_MAX_HEALTH
        self.exit_open = False
        self.idle_time = 0.0
        level = LEVELS[self.level_index]
        self.world_width = level["world_width"]
        self.world_height = SCREEN_HEIGHT

        self.background = arcade.load_texture(
            ":resources:images/cybercity_background/back-buildings.png"
        )

        self.player = arcade.Sprite(
            ":resources:images/alien/alienBlue_front.png",
            scale=0.42,
        )
        self.player.center_x, self.player.center_y = level["spawn"]
        self.player_list.append(self.player)

        for x in range(0, self.world_width + 64, 64):
            tile = arcade.Sprite(":resources:images/tiles/brickGrey.png", 0.5)
            tile.center_x = x
            tile.center_y = 32
            self.wall_list.append(tile)

        platform_y_by_x = {}
        for i, (x, y) in enumerate(level["platforms"]):
            platform_texture = (
                ":resources:images/tiles/brickGrey.png"
                if i % 2 == 0
                else ":resources:images/tiles/brickTextureWhite.png"
            )
            platform = arcade.Sprite(platform_texture, 0.5)
            platform.center_x = x
            platform.center_y = y
            self.wall_list.append(platform)
            platform_y_by_x[x] = y

        for item in level["unstable"]:
            platform = arcade.Sprite(":resources:images/tiles/brickGrey.png", 0.5)
            platform.center_x, platform.center_y = item["pos"]
            platform.mode = item["mode"]
            platform.timer = 0.0
            platform.visible = True
            self.wall_list.append(platform)
            self.unstable_list.append(platform)

        for x in level["shards"]:
            shard = arcade.Sprite(":resources:images/items/star.png", 0.7)
            shard.center_x = x
            shard.center_y = platform_y_by_x.get(x, 120) + 40
            self.shard_list.append(shard)
        self.shards_required = len(level["shards"])

        for info in level["enemies"]:
            enemy = arcade.Sprite(":resources:images/enemies/fly.png", 0.6)
            enemy.center_x, enemy.center_y = info["pos"]
            enemy.patrol_left, enemy.patrol_right = info["patrol"]
            enemy.tier = info["tier"]
            enemy.change_x = ENEMY_TIERS[enemy.tier]["speed"]
            enemy.shoot_timer = 0.0
            self.enemy_list.append(enemy)

        exit_sprite = arcade.Sprite(":resources:images/tiles/signExit.png", 0.7)
        exit_sprite.center_x, exit_sprite.center_y = level["exit"]
        exit_sprite.alpha = 120
        self.exit_list.append(exit_sprite)

        self.glitch_zones = level["glitch_zones"]

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, gravity_constant=self.gravity
        )

        self.text_shards = arcade.Text(
            "", 20, self.window.height - 30, arcade.color.WHITE, 16
        )
        self.text_health = arcade.Text(
            "", 20, self.window.height - 55, arcade.color.WHITE, 16
        )
        self.text_level = arcade.Text(
            "", 20, self.window.height - 80, arcade.color.LIGHT_GRAY, 14
        )

    def on_draw(self):
        self.clear()

        self.world_camera.use()
        if self.background:
            arcade.draw_texture_rect(
                self.background,
                arcade.rect.XYWH(
                    self.world_width / 2,
                    self.window.height / 2,
                    self.world_width,
                    self.window.height,
                ),
            )

        self.wall_list.draw()
        self.shard_list.draw()
        self.enemy_list.draw()
        self.enemy_bullets.draw()
        self.exit_list.draw()
        self.player_list.draw()

        glitch_strength = 1.0 - min(1.0, self.shards_collected / max(1, self.shards_required))
        glitch_points = int(GLITCH_POINT_MAX * glitch_strength)
        for _ in range(glitch_points):
            arcade.draw_point(
                random.randint(0, self.window.width) + int(self.world_camera.position[0] - self.window.width / 2),
                random.randint(0, self.window.height),
                arcade.color.WHITE,
                1,
            )

        self.gui_camera.use()
        self.text_shards.text = f"Shards: {self.shards_collected}/{self.shards_required}"
        self.text_health.text = f"Health: {self.player_health}"
        self.text_level.text = f"Level: {self.level_index + 1}"
        self.text_shards.draw()
        self.text_health.draw()
        self.text_level.draw()

    def on_update(self, delta_time):
        dx = 0
        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            dx -= PLAYER_SPEED
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            dx += PLAYER_SPEED

        glitch_type = self.get_glitch_type()
        if glitch_type == "invert":
            dx *= -1
        elif glitch_type == "low":
            dx *= 1.3

        self.player.change_x = dx

        if dx == 0:
            self.idle_time += delta_time
        else:
            self.idle_time = 0.0

        if glitch_type == "heavy":
            self.physics_engine.gravity_constant = BASE_GRAVITY * 2.2
        elif glitch_type == "low":
            self.physics_engine.gravity_constant = BASE_GRAVITY * 0.5
        else:
            self.physics_engine.gravity_constant = BASE_GRAVITY

        self.physics_engine.update()

        for shard in arcade.check_for_collision_with_list(self.player, self.shard_list):
            shard.remove_from_sprite_lists()
            self.shards_collected += 1

        if self.shards_collected >= self.shards_required:
            self.exit_open = True
            for exit_sprite in self.exit_list:
                exit_sprite.alpha = 255

        if self.exit_open and arcade.check_for_collision_with_list(self.player, self.exit_list):
            self.go_next_level()
            return

        self.update_unstable_platforms(delta_time)
        self.update_enemies(delta_time)
        self.update_enemy_bullets()
        self.check_enemy_collisions()
        self.update_camera()

    def update_unstable_platforms(self, delta_time):
        if self.idle_time < IDLE_TRIGGER_TIME:
            return

        for plat in self.unstable_list:
            plat.timer += delta_time
            if plat.mode == "blink" and plat.timer > UNSTABLE_BLINK_TIME:
                plat.timer = 0.0
                plat.visible = not plat.visible
                plat.alpha = 0 if not plat.visible else 255
                if plat.visible and plat not in self.wall_list:
                    self.wall_list.append(plat)
                if not plat.visible and plat in self.wall_list:
                    self.wall_list.remove(plat)
            elif plat.mode == "teleport" and plat.timer > UNSTABLE_TELEPORT_TIME:
                plat.timer = 0.0
                plat.center_x = random.randint(200, self.world_width - 200)
                plat.center_y = random.randint(160, 320)

    def update_enemies(self, delta_time):
        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            if enemy.center_x < enemy.patrol_left or enemy.center_x > enemy.patrol_right:
                enemy.change_x *= -1

            enemy.shoot_timer += delta_time
            if enemy.shoot_timer > ENEMY_TIERS[enemy.tier]["fire_rate"]:
                enemy.shoot_timer = 0.0
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", 0.5)
                bullet.center_x = enemy.center_x
                bullet.center_y = enemy.center_y
                dx = self.player.center_x - enemy.center_x
                dy = self.player.center_y - enemy.center_y
                angle = math.atan2(dy, dx)
                bullet.change_x = math.cos(angle) * ENEMY_BULLET_SPEED
                bullet.change_y = math.sin(angle) * ENEMY_BULLET_SPEED
                self.enemy_bullets.append(bullet)

    def update_enemy_bullets(self):
        for bullet in self.enemy_bullets:
            bullet.center_x += bullet.change_x
            bullet.center_y += bullet.change_y
            if (
                bullet.center_x < 0
                or bullet.center_x > self.world_width
                or bullet.center_y < 0
                or bullet.center_y > self.world_height
            ):
                bullet.remove_from_sprite_lists()

        if arcade.check_for_collision_with_list(self.player, self.enemy_bullets):
            self.damage_player(8)
            for bullet in arcade.check_for_collision_with_list(self.player, self.enemy_bullets):
                bullet.remove_from_sprite_lists()

    def check_enemy_collisions(self):
        enemies_hit = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        for _enemy in enemies_hit:
            pass

    def damage_player(self, amount):
        self.player_health -= amount
        if self.player_health <= 0:
            game_over = GameOverView(self.level_index)
            self.window.show_view(game_over)

    def get_glitch_type(self):
        for zone in self.glitch_zones:
            x, y, w, h, ztype = zone
            if x <= self.player.center_x <= x + w and y <= self.player.center_y <= y + h:
                return ztype
        return None

    def update_camera(self):
        target_x = max(self.window.width / 2, min(self.world_width - self.window.width / 2, self.player.center_x))
        target_y = self.window.height / 2
        self.world_camera.position = (target_x, target_y)
        self.gui_camera.position = (self.window.width / 2, self.window.height / 2)

    def go_next_level(self):
        self.window.show_view(WinView())

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = JUMP_SPEED

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
