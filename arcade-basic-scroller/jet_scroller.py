# Basic arcade shooter
# As seen in https://realpython.com/arcade-python-game-framework/#fundamentals-of-python-game-design

import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Arcade Space Shooter"
SCALING = 2.0

class FlyingSprite(arcade.Sprite):
    """Base class for all flying sprites
    Flying sprites include enemies and clouds
    """

    def update(self):
        """Update the position of the sprite
        When it moves off screen to the left, remove it
        """

        # Move the sprite
        super().update()

        if (
            self.velocity[0] < 0 and self.right < 0
            or self.velocity[0] > 0 and self.left > SCREEN_WIDTH
        ):
            self.remove_from_sprite_lists()

class SpaceShooter(arcade.Window):
    """Space Shooter side scroller game
    Player starts on the left, enemies appear on the right
    Player can move anywhere, but not off screen
    Enemies fly to the left at variable speed
    Collisions end the game
    """

    def __init__(self, width, height, title):
        """Initialize the game
        """

        super().__init__(width, height, title)

        # Set up the empty sprite lists
        self.enemies_list = arcade.SpriteList()
        self.clouds_list = arcade.SpriteList()
        self.missile_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()

    def setup(self):
        """Get the game ready to play
        """

        # Set the background colour
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Set up the player
        self.player = arcade.Sprite("images/jet.png", SCALING)
        self.player.center_y = self.height/2
        self.player.left = 10
        self.all_sprites.append(self.player)

        # Spawn a new enemy every 0.25 seconds
        arcade.schedule(self.add_enemy, 0.25)

        # Spawn a new cloud every second
        arcade.schedule(self.add_cloud, 1.0)

        # Load background music
        # Sound source: http://ccmixter.org/files/Apoxode/59262
        # License: https://creativecommons.org/licenses/by/3.0/
        self.background_music = arcade.load_sound(
            "sounds/Apoxode_-_Electric_1.wav"
        )

        # Load all the sounds
        # Sound sources: Jon Fincher
        self.collision_sound = arcade.load_sound("sounds/Collision.wav")
        self.move_up_sound = arcade.load_sound("sounds/Rising_putter.wav")
        self.move_down_sound = arcade.load_sound("sounds/Falling_putter.wav")

        self.paused = False

        # Play the background music and schedule the loop
        self.play_background_music()
        arcade.schedule(self.play_background_music, 15)
        
    def play_background_music(self, delta_time: int = 0):
        """Starts playing the background music
        """
        self.background_music.play()

    def fire_missile(self):
        """Fires a missile against the incoming enemies
        """
        if self.paused:
            return

        missile = FlyingSprite("images/missile_right.png", SCALING)

        missile.center_x = self.player.center_x
        missile.center_y = self.player.center_y - 5
        missile.velocity = (500, 0)

        self.missile_list.append(missile)
        self.all_sprites.append(missile)

    def add_enemy(self, delta_time: float):
        """Adds a new enemy to the screen

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """

        if self.paused:
            return

        # First, create the the new enemy sprite
        enemy = FlyingSprite("images/ovni.png", SCALING)

        # Set its position to a random height and off screen right
        enemy.left = random.randint(self.width, self.width + 80)
        enemy.top = random.randint(10, self.height - 10)
        # Set its speed to a random speed heading left
        enemy.velocity = (random.randint(-800, -200), 0)

        # Add it to the enemies list
        self.enemies_list.append(enemy)
        self.all_sprites.append(enemy)

    def add_cloud(self, delta_time: float):
        """Adds a new cloud to the screen

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """

        if self.paused:
            return

        # First, create the cloud sprite
        cloud = FlyingSprite("images/cloud.png", SCALING)

        # Set its position to a random height and off screen right
        cloud.left = random.randint(self.width, self.width + 80)
        cloud.top = random.randint(10, self.height - 10)

        # Set its speed to a random speed heading left
        cloud.velocity = (random.randint(-200, -80), 0)

        # Add it to the enemies list
        self.clouds_list.append(cloud)
        self.all_sprites.append(cloud)

    def on_key_press(self, symbol, modifiers):
        """Handle user keyboard input
        Q: Quit the game
        P: Pause/unpause the game
        W/A/S/D: Move Up, Left, Down, Right
        Arrows: Move Up, Left, Down, Right

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if symbol == arcade.key.Q:
            # Quit immediately
            arcade.close_window()

        if symbol == arcade.key.P:
            self.paused = not self.paused

        if symbol == arcade.key.SPACE:
            self.fire_missile()

        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.move_up_sound.play()
            self.player.change_y = 200
        elif symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.player.change_x = -200
        elif symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.move_down_sound.play()
            self.player.change_y = -200
        elif symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.player.change_x = 200

    def on_key_release(self, symbol: int, modifiers: int):
        """Undo movement vectors when movement keys are released

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if (
            symbol == arcade.key.W
            or symbol == arcade.key.S
            or symbol == arcade.key.UP
            or symbol == arcade.key.DOWN
        ):
            self.player.change_y = 0

        if (
            symbol == arcade.key.A
            or symbol == arcade.key.D
            or symbol == arcade.key.LEFT
            or symbol == arcade.key.RIGHT
        ):
            self.player.change_x = 0

    def on_update(self, delta_time: float):
        """Update all game objects
        """
        if self.paused:
            return

        if self.player.collides_with_list(self.enemies_list):
            self.collision_sound.play()
            # Stop the game and schedule the game close
            self.paused = True
            arcade.schedule(lambda delta_time: arcade.close_window(), 0.5)

        for enemy in self.enemies_list:
            collisions = enemy.collides_with_list(self.missile_list)
            if collisions:
                enemy.remove_from_sprite_lists()
                for missile in collisions:
                    missile.remove_from_sprite_lists()

        # Update everything
        for sprite in self.all_sprites:
            sprite.center_x = int(
                sprite.center_x + sprite.change_x * delta_time
            )
            sprite.center_y = int(
                sprite.center_y + sprite.change_y * delta_time
            )

        if self.player.top > self.height:
            self.player.top = self.height
        elif self.player.bottom < 0:
            self.player.bottom = 0
        
        if self.player.left < 0:
            self.player.left = 0
        elif self.player.right > self.width:
            self.player.right = self.width


    def on_draw(self):
        """Draw all game objects
        """

        arcade.start_render()
        self.all_sprites.draw()


if __name__ == "__main__":
    app = SpaceShooter(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    app.setup()
    arcade.run()