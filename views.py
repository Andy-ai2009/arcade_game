import random
import arcade

from game_data import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_SPEED,
    JUMP_SPEED,
    GRAVITY,
    IDLE_TRIGGER_TIME,
    BLINK_TIME,
    TELEPORT_TIME,
    PLATFORM_POINTS,
    UNSTABLE_PLATFORMS,
    SHARD_X,
    ENEMIES,
    FLOOR_TILE,
    PLATFORM_A,
    PLATFORM_B,
    PLAYER_SPRITE,
    ENEMY_SPRITE,
    SHARD_SPRITE,
    EXIT_SPRITE,
)


class StartView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "BROKEN LAB",
            self.window.width / 2,
            self.window.height / 2 + 30,
            arcade.color.WHITE,
            28,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press any key",
            self.window.width / 2,
            self.window.height / 2 - 10,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.shard_list = arcade.SpriteList()
        self.exit_list = arcade.SpriteList()
        self.unstable_list = arcade.SpriteList()

        self.physics_engine = None
        self.keys_pressed = set()
        self.shards_collected = 0
        self.shards_required = 0
        self.exit_open = False
        self.idle_time = 0.0

    def setup(self):
        arcade.set_background_color(arcade.color.BLACK)

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.shard_list = arcade.SpriteList()
        self.exit_list = arcade.SpriteList()
        self.unstable_list = arcade.SpriteList()

        self.shards_collected = 0
        self.exit_open = False
        self.idle_time = 0.0

        self.player = arcade.Sprite(PLAYER_SPRITE, 0.42)
        self.player.center_x = 80
        self.player.center_y = 140
        self.player_list.append(self.player)

        for x in range(0, 1400, 64):
            tile = arcade.Sprite(FLOOR_TILE, 0.5)
            tile.center_x = x
            tile.center_y = 32
            self.wall_list.append(tile)

        for i, (x, y) in enumerate(PLATFORM_POINTS):
            texture = PLATFORM_A if i % 2 == 0 else PLATFORM_B
            platform = arcade.Sprite(texture, 0.5)
            platform.center_x = x
            platform.center_y = y
            self.wall_list.append(platform)

        for x, y, mode in UNSTABLE_PLATFORMS:
            platform = arcade.Sprite(PLATFORM_A, 0.5)
            platform.center_x = x
            platform.center_y = y
            platform.mode = mode
            platform.timer = 0.0
            platform.visible = True
            self.wall_list.append(platform)
            self.unstable_list.append(platform)

        for x in SHARD_X:
            shard = arcade.Sprite(SHARD_SPRITE, 0.7)
            shard.center_x = x
            shard.center_y = 280
            self.shard_list.append(shard)
        self.shards_required = len(SHARD_X)

        for x, y, left, right in ENEMIES:
            enemy = arcade.Sprite(ENEMY_SPRITE, 0.6)
            enemy.center_x = x
            enemy.center_y = y
            enemy.patrol_left = left
            enemy.patrol_right = right
            enemy.change_x = 1.2
            self.enemy_list.append(enemy)

        exit_sprite = arcade.Sprite(EXIT_SPRITE, 0.7)
        exit_sprite.center_x = 1360
        exit_sprite.center_y = 100
        exit_sprite.alpha = 120
        self.exit_list.append(exit_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, gravity_constant=GRAVITY
        )

    def on_draw(self):
        self.clear()
        self.wall_list.draw()
        self.shard_list.draw()
        self.enemy_list.draw()
        self.exit_list.draw()
        self.player_list.draw()

        arcade.draw_text(
            f"Shards: {self.shards_collected}/{self.shards_required}",
            20,
            self.window.height - 30,
            arcade.color.WHITE,
            16,
        )

    def on_update(self, delta_time):
        dx = 0
        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            dx -= PLAYER_SPEED
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            dx += PLAYER_SPEED
        self.player.change_x = dx

        if dx == 0:
            self.idle_time += delta_time
        else:
            self.idle_time = 0.0

        self.physics_engine.update()

        for shard in arcade.check_for_collision_with_list(self.player, self.shard_list):
            shard.remove_from_sprite_lists()
            self.shards_collected += 1

        if self.shards_collected >= self.shards_required:
            self.exit_open = True
            for exit_sprite in self.exit_list:
                exit_sprite.alpha = 255

        if self.exit_open and arcade.check_for_collision_with_list(self.player, self.exit_list):
            self.setup()
            return

        self.update_unstable(delta_time)
        self.update_enemies()

    def update_unstable(self, delta_time):
        if self.idle_time < IDLE_TRIGGER_TIME:
            return

        for plat in self.unstable_list:
            plat.timer += delta_time
            if plat.mode == "blink" and plat.timer > BLINK_TIME:
                plat.timer = 0.0
                plat.visible = not plat.visible
                plat.alpha = 0 if not plat.visible else 255
                if plat.visible and plat not in self.wall_list:
                    self.wall_list.append(plat)
                if not plat.visible and plat in self.wall_list:
                    self.wall_list.remove(plat)
            elif plat.mode == "teleport" and plat.timer > TELEPORT_TIME:
                plat.timer = 0.0
                plat.center_x = random.randint(200, 1200)
                plat.center_y = random.choice([180, 220, 260])

    def update_enemies(self):
        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            if enemy.center_x < enemy.patrol_left or enemy.center_x > enemy.patrol_right:
                enemy.change_x *= -1

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = JUMP_SPEED

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
