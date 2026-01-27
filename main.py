import arcade

from game_data import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from views import StartView, GameOverView


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
