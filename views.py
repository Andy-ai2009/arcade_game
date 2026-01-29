import random
from pathlib import Path
import arcade
from arcade.camera import Camera2D

from game_data import (
    SCREEN_HEIGHT,
    PLAYER_SPEED,
    JUMP_SPEED,
    GRAVITY,
    IDLE_TRIGGER_TIME,
    BLINK_TIME,
    TELEPORT_TIME,
    FLOOR_TILE,
    PLATFORM_A,
    PLATFORM_B,
    PLAYER_SPRITE,
    ENEMY_SPRITE,
    SHARD_SPRITE,
    EXIT_SPRITE,
    LEVELS,
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
        game_view = GameView(level_index=0)
        game_view.setup()
        self.window.show_view(game_view)


class GameOverView(arcade.View):
    def __init__(self, level_index=0):
        super().__init__()
        self.level_index = level_index

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "GAME OVER",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.RED,
            30,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press R to restart",
            self.window.width / 2,
            self.window.height / 2 - 40,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            game_view = GameView(level_index=self.level_index)
            game_view.setup()
            self.window.show_view(game_view)
        if key == arcade.key.ESCAPE:
            self.window.close()


class WinView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "YOU WIN",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.GREEN_YELLOW,
            32,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press R to restart",
            self.window.width / 2,
            self.window.height / 2 - 40,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            game_view = GameView(level_index=0)
            game_view.setup()
            self.window.show_view(game_view)
        if key == arcade.key.ESCAPE:
            self.window.close()


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
        self.exit_open = False
        self.idle_time = 0.0
        self.freeze_timer = 0.0
        self.background = None
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.world_width = 0
        self.lives = 5
        self.level_data = LEVELS[self.level_index]
        self.level_gravity = GRAVITY
        self.snd_collect = arcade.load_sound(":resources:/sounds/coin1.wav")
        self.snd_hit = arcade.load_sound(":resources:/sounds/hit3.wav")
        self.snd_jump = arcade.load_sound(":resources:/sounds/jump1.wav")
        self.snd_shoot = arcade.load_sound(":resources:/sounds/laser1.wav")

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
        self.exit_open = False
        self.idle_time = 0.0
        self.freeze_timer = 0.0
        self.lives = 5
        self.level_data = LEVELS[self.level_index]
        self.level_gravity = self.level_data.get("gravity", GRAVITY)

        self.background = arcade.load_texture(":resources:images/backgrounds/stars.png")

        base_scale = 0.42
        scale_y = -base_scale if self.level_data.get("flip_player") else base_scale
        self.player = arcade.Sprite(PLAYER_SPRITE, base_scale)
        self.player.scale_y = scale_y
        self.player.center_x = 80
        self.player.center_y = 140 if not self.level_data.get("ceiling") else SCREEN_HEIGHT - 140
        self.player_list.append(self.player)

        self.world_width = self.level_data["world_width"]

        ground_y = SCREEN_HEIGHT - 32 if self.level_data.get("ceiling") else 32
        for x in range(0, self.world_width + 64, 64):
            tile = arcade.Sprite(FLOOR_TILE, 0.5)
            tile.center_x = x
            tile.center_y = ground_y
            self.wall_list.append(tile)

        platform_heights = {}
        for i, (x, y) in enumerate(self.level_data["platform_points"]):
            if self.level_data.get("ceiling"):
                y = SCREEN_HEIGHT - y
            texture = PLATFORM_A if i % 2 == 0 else PLATFORM_B
            platform = arcade.Sprite(texture, 0.5)
            platform.center_x = x
            platform.center_y = y
            self.wall_list.append(platform)
            platform_heights[x] = y

        for x, y, mode in self.level_data["unstable"]:
            if self.level_data.get("ceiling"):
                y = SCREEN_HEIGHT - y
            platform = arcade.Sprite(PLATFORM_A, 0.5)
            platform.center_x = x
            platform.center_y = y
            platform.mode = mode
            platform.timer = 0.0
            platform.visible = True
            self.wall_list.append(platform)
            self.unstable_list.append(platform)
            platform_heights[x] = y

        for x in self.level_data["shards"]:
            shard = arcade.Sprite(SHARD_SPRITE, 0.7)
            shard.center_x = x
            base_y = platform_heights.get(x, 140)
            shard.center_y = base_y + 60
            if self.level_data.get("ceiling"):
                shard.center_y = SCREEN_HEIGHT - shard.center_y
            self.shard_list.append(shard)
        self.shards_required = len(self.level_data["shards"])

        for x, y, left, right in self.level_data["enemies"]:
            if self.level_data.get("ceiling"):
                y = SCREEN_HEIGHT - y
            enemy = arcade.Sprite(ENEMY_SPRITE, 0.6)
            enemy.center_x = x
            enemy.center_y = y
            enemy.patrol_left = left
            enemy.patrol_right = right
            enemy.change_x = 1.2
            enemy.shoot_timer = 0.0
            self.enemy_list.append(enemy)

        exit_sprite = arcade.Sprite(EXIT_SPRITE, 0.7)
        exit_sprite.center_x = self.level_data["exit_x"]
        exit_sprite.center_y = self.level_data.get("exit_y", 100)
        exit_sprite.alpha = 120
        self.exit_list.append(exit_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, gravity_constant=self.level_gravity
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

        self.gui_camera.use()
        arcade.draw_text(
            f"Shards: {self.shards_collected}/{self.shards_required}",
            20,
            self.window.height - 30,
            arcade.color.WHITE,
            16,
        )
        arcade.draw_text(
            f"Lives: {self.lives}",
            20,
            self.window.height - 55,
            arcade.color.WHITE,
            16,
        )

    def on_update(self, delta_time):
        dx = 0
        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            dx -= PLAYER_SPEED
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            dx += PLAYER_SPEED
        if self.level_data.get("invert_controls"):
            dx *= -1
        self.player.change_x = dx

        if dx == 0:
            self.idle_time += delta_time
        else:
            self.idle_time = 0.0
            self.freeze_timer = 2.0
            self.lock_unstable()

        self.physics_engine.update()

        for shard in arcade.check_for_collision_with_list(self.player, self.shard_list):
            shard.remove_from_sprite_lists()
            self.shards_collected += 1
            arcade.play_sound(self.snd_collect, volume=0.4)

        if self.shards_collected >= self.shards_required:
            self.exit_open = True
            for exit_sprite in self.exit_list:
                exit_sprite.alpha = 255

        if self.exit_open and arcade.check_for_collision_with_list(self.player, self.exit_list):
            if self.level_index + 1 < len(LEVELS):
                next_view = GameView(self.level_index + 1)
                next_view.setup()
                self.window.show_view(next_view)
            else:
                self.save_run("win")
                self.window.show_view(WinView())
            return

        self.update_unstable(delta_time)
        self.update_enemies(delta_time)
        self.update_enemy_bullets(delta_time)
        self.check_enemy_stomp()
        self.update_camera()

    def update_unstable(self, delta_time):
        if self.freeze_timer > 0:
            self.freeze_timer -= delta_time
            return
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

    def update_enemies(self, delta_time):
        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            if enemy.center_x < enemy.patrol_left or enemy.center_x > enemy.patrol_right:
                enemy.change_x *= -1
            enemy.shoot_timer += delta_time
            if enemy.shoot_timer > 3.5:
                enemy.shoot_timer = 0.0
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", 0.5)
                bullet.center_x = enemy.center_x
                bullet.center_y = enemy.center_y
                dx = self.player.center_x - enemy.center_x
                dy = self.player.center_y - enemy.center_y
                length = max(1, (dx ** 2 + dy ** 2) ** 0.5)
                bullet.change_x = dx / length * 6
                bullet.change_y = dy / length * 6
                self.enemy_bullets.append(bullet)
                arcade.play_sound(self.snd_shoot, volume=0.25)

    def update_enemy_bullets(self, delta_time):
        for bullet in list(self.enemy_bullets):
            bullet.center_x += bullet.change_x
            bullet.center_y += bullet.change_y
            if (
                bullet.center_x < 0
                or bullet.center_x > self.world_width
                or bullet.center_y < 0
                or bullet.center_y > SCREEN_HEIGHT
            ):
                bullet.remove_from_sprite_lists()
        if arcade.check_for_collision_with_list(self.player, self.enemy_bullets):
            self.lives -= 1
            if self.lives <= 0:
                self.save_run("game_over")
                self.window.show_view(GameOverView(self.level_index))
                return
            self.enemy_bullets.clear()
            self.player.center_x = 80
            self.player.center_y = 140 if not self.level_data.get("ceiling") else SCREEN_HEIGHT - 140
            self.keys_pressed.clear()
            arcade.play_sound(self.snd_hit, volume=0.5)

    def check_enemy_stomp(self):
        hits = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        for enemy in hits:
            falling = (self.level_gravity >= 0 and self.player.change_y < 0) or (
                self.level_gravity < 0 and self.player.change_y > 0
            )
            if falling:
                enemy.remove_from_sprite_lists()
                bounce_dir = 1 if self.level_gravity >= 0 else -1
                self.player.change_y = JUMP_SPEED * 0.5 * bounce_dir
                arcade.play_sound(self.snd_hit, volume=0.4)

    def update_camera(self):
        target_x = max(
            self.window.width / 2,
            min(self.world_width - self.window.width / 2, self.player.center_x),
        )
        target_y = self.window.height / 2
        self.world_camera.position = (target_x, target_y)
        self.gui_camera.position = (self.window.width / 2, self.window.height / 2)

    def lock_unstable(self):
        for plat in self.unstable_list:
            plat.timer = 0.0
            plat.visible = True
            plat.alpha = 255
            if plat not in self.wall_list:
                self.wall_list.append(plat)

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if key == arcade.key.SPACE:
            if self.level_gravity < 0:
                if self.physics_engine.can_jump() or abs(self.player.change_y) < 0.01:
                    self.player.change_y = -JUMP_SPEED * 0.8
                    arcade.play_sound(self.snd_jump, volume=0.4)
            else:
                if self.physics_engine.can_jump():
                    self.player.change_y = JUMP_SPEED
                    arcade.play_sound(self.snd_jump, volume=0.4)

    def on_key_release(self, key , modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def save_run(self, status):
        path = Path(__file__).parent / "stats.csv"
        line = f"{self.level_index},{status},{self.shards_collected},{self.lives}\n"
        with path.open("a") as f:
            f.write(line)
