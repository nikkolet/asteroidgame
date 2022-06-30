
"""
File: asteroids.py
Original Author: Br. Burton
Designed to be completed by Dhener Trinidad

This program implements the asteroids game.

My changes:
Added Background
Added sound for fire and hit
asteroid bounce to each other
limit the speed of the ship and make the direction where it is traveling the same with the angle or orientation.
If ship died. it will show a new Game Over view for game over and the time-lapse to finish the game + score penalty.
If all asteroids were destroyed, a new Game over view for congratulations and the time-lapse will appear
Added ship life and display mini ship on the top right corner that represents the ship
Score: the lower the better, penalty points will be added when you hit an asteroid
The Game() was also change from arcade.Window to arcade.View to make the change screen possible
main functions was added
############################################################################
week10 update: 
bullet was corrected to have a life of 60 frames by counting the travel time via self.travel
For the ship to move easier, removed the bounce for ship and now only implement it with the asteroid
As part of the assesment guidline when asteroid and ship collide, it should break the asteroid
The ship now moving correctly and at a fix slower rate when the key is released
draw method in base class for flyingobjects and ship are no longer abstract, (changed this in week 11)
draw method were removed in subclasses because of the changes and added attributes/member variables instead
Week11:
To satisfy the assesment requirement for draw method, 
    I have added the draw method back to each flying object 
    and make a it an abstract method in flyingbase class again.
Added life for ship and it will blink when it by the asteroid
Removed the try/except for loading images, I finally found a fix in my issue with vs code
Penalty was added when an asteroid hit the ship, it varies base on asteroid size, 


############################################################################
About the bounce:
    The bounce will make the game more realistic in a way that the asteroid have a chance to collide and bounce, 
    Bounce might go to a totally opposite direction or just slide, or just move a little depending on the impact and angle

About Scoring and endgame:
    The ship will live until all the asteroids are gone.
    The score will depend on how long the player clears all the asteroids.
    The lower the score, the better.
    The game will end once all the asteroids were gone and the congratulatory message with the score will show at the center 
############################################################################

"""
import arcade
import math
import random
from abc import ABC, abstractmethod
import time


# These are Global constants to use throughout the game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BULLET_RADIUS = 30
BULLET_SPEED = 10
BULLET_LIFE = 60

SHIP_TURN_AMOUNT = 3
SHIP_THRUST_AMOUNT = 0.25
SHIP_RADIUS = 30

INITIAL_ROCK_COUNT = 5

BIG_ROCK_SPIN = 1
BIG_ROCK_SPEED = 1.5
BIG_ROCK_RADIUS = 15

MEDIUM_ROCK_SPIN = -2
MEDIUM_ROCK_RADIUS = 5

SMALL_ROCK_SPIN = 5
SMALL_ROCK_RADIUS = 2

class Point:
    """
    This will provide the location of the object
    """
    def __init__(self):
        self.x = 0.00 
        self.y = 0.00

class Velocity:
    """
    This helps in the movement of the object
    """
    def __init__(self):
        self.dx = 0
        self.dy = 0

class FlyingObject(ABC):
    """
    This will be the base class for flying objects
    """
    def __init__(self):
        self.center = Point()
        self.velocity = Velocity()
        self.alive = True #check if the object is still alive
        self.radius = 0.0
        self.angle = 0 #facing 

        self.img = "images/bgu.jpg"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.alpha = 0
    
    @abstractmethod
    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.width, 
                self.height, self.texture, self.angle, self.alpha) 
  
    def advance(self):

        """
        This will help in the movement of the object
        """
        self.center.x += self.velocity.dx #initial position += new possition
        self.center.y += self.velocity.dy #initial position += new possition
    
    def is_off_screen(self,width,height):
        """
        This will check if the object is off screen, sample, if an object goes off the right edge of the screen, 
        it should appear on the left edge.
        """        
        if self.center.x > width:
            self.center.x = 0
        elif self.center.x < 0:
            self.center.x = width
        elif self.center.y > height:
            self.center.y = 0
        elif self.center.y < 0:
            self.center.y = height

class Ship(FlyingObject):
    """
    This will have the ship functions and basic attributes
    """
    def __init__(self):
        super().__init__()
        self.angle = 0.00
        self.radius = SHIP_RADIUS
        self.center.x = SCREEN_WIDTH // 2
        self.center.y = SCREEN_HEIGHT //2
        self.life = 5


    def draw(self):
        self.img = "images/playerShip1_orange.png"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height  
        super().draw() 
    
    def advance(self):
        super().advance()
        #this will make the help looks blinking when hit by the asteroid, collission will set the alpha to 1
        if self.alpha <= 5:
            self.alpha += 1
            if self.alpha >= 5:
                self.alpha = 255

class Bullet(FlyingObject):
    def __init__(self):
        super().__init__()
        self.radius = BULLET_RADIUS
        self.travel = 0
        self.angle = self.angle + 90

    def draw(self):
        self.img = "images/laserBlue01.png"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.alpha = 255
        super().draw()
    
    def advance(self):
        super().advance()
        #travel represents the frame, it will die in 60 frames
        self.travel += 1
        if self.travel == BULLET_LIFE:
            self.alive = False

    def fire(self, ship):
        """
        This will give the movement for our bullet and angel for its direction
        """
        #get the position of the ship and angle
        self.center.x = ship.center.x
        self.center.y = ship.center.y
        self.angle += ship.angle
        #speed and angle of bullet when fired
        self.velocity.dx = math.cos(math.radians(ship.angle - 270)) * BULLET_SPEED
        self.velocity.dy = math.sin(math.radians(ship.angle - 270)) * BULLET_SPEED
        self.velocity.dx += ship.velocity.dx
        self.velocity.dy += ship.velocity.dy  
       

class Asteroids(FlyingObject, ABC):
    def __init__(self):
        """
        Base class for asteroids
        """
        super().__init__()
        self.rotation = 0.00 #spin
        self.penalty = 0 #this will be added to the score when the asteroid hit the ship

    def advance(self):
        """
        This will help in the movement of the object
        """
        self.angle += self.rotation #spin
        self.center.x += self.velocity.dx #initial position += new possition
        self.center.y += self.velocity.dy #initial position += new possition    
    
    @abstractmethod
    def hit(self):
        """
        
        """
        return

    def bounce_horizontal(self):
        """
        The asteroid will bounce when they hit each other
        """
        self.velocity.dx *= -1 #inverse the movement of the ball
        

    def bounce_vertical(self):
        """
        The asteroid will bounce when they hit each other
        """
        self.velocity.dy *= -1 #inverse the movement of the ball
        

class Largeasteroids(Asteroids):
    def __init__(self):
        super().__init__()
        #position
        self.center.x = random.uniform(0,SCREEN_HEIGHT)
        self.center.y = random.uniform(SCREEN_HEIGHT,SCREEN_WIDTH)
        #speed
        self.velocity.dx = random.uniform(-BIG_ROCK_SPEED,BIG_ROCK_SPEED)
        self.velocity.dy = random.uniform(-BIG_ROCK_SPEED,BIG_ROCK_SPEED)
        self.rotation = BIG_ROCK_SPIN
        self.radius = BIG_ROCK_RADIUS
        self.penalty = 10
        
    def draw(self):
        self.img = "images/meteorGrey_big1.png"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.alpha = 255
        super().draw()


    def hit(self):
        """
        split the asteroid
        """
        #create new asteroid from the current posstion of this asteroid
        particles = [Mediumasteroids(self.center), Mediumasteroids(self.center), Smallasteroids(self.center)]
        
        #get the speed of this asteroid and pass it to the new asteriods and give them direction + speed
        particles[0].velocity.dx = self.velocity.dx
        particles[0].velocity.dy = self.velocity.dy + 2 #go up

        particles[1].velocity.dx = self.velocity.dx
        particles[1].velocity.dy = self.velocity.dy + 2 * -1 #go down

        particles[2].velocity.dx = self.velocity.dx + 5 #to the right
        particles[2].velocity.dy = self.velocity.dy

        return particles

class Mediumasteroids(Asteroids):
    def __init__(self,asteroid_center):
        super().__init__()
        self.rotation = MEDIUM_ROCK_SPIN
        self.radius = MEDIUM_ROCK_RADIUS
        self.center.x = asteroid_center.x
        self.center.y = asteroid_center.y
        self.penalty = 6  
        
    def draw(self):    
        self.img = "images/meteorGrey_med1.png"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.alpha = 255
        super().draw()

    def hit(self):
        """
        split the asteroid
        """
        #create new asteroid from the current posstion of this asteroid
        particles = [Smallasteroids(self.center), Smallasteroids(self.center)]
        
        #get the speed of this asteroid and pass it to the new asteriods and give then direction + speed
        particles[0].velocity.dx = self.velocity.dx + 1.5
        particles[0].velocity.dy = self.velocity.dy + 1.5

        particles[1].velocity.dx = self.velocity.dx + 1.5 * -1
        particles[1].velocity.dy = self.velocity.dy + 1.5 * -1

        return particles

class Smallasteroids(Asteroids):
    def __init__(self,asteroid_center):
        super().__init__()
        self.rotation = SMALL_ROCK_SPIN
        self.radius = SMALL_ROCK_RADIUS
        self.center.x = asteroid_center.x
        self.center.y = asteroid_center.y
        self.penalty = 3
  
    def draw(self):
        self.img = "images/meteorGrey_small1.png"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.alpha = 255
        super().draw()

    def hit(self):
        """
        split the asteroid
        """
        #no new asteroid will be created
        particles = []
        return particles

class Game(arcade.View):
    """
    This class handles all the game callbacks and interaction

    This class will then call the appropriate functions of
    each of the above classes.

    You are welcome to modify anything in this class.
    """

    def __init__(self):
        """
        Sets up the initial conditions of the game
        :param width: Screen width
        :param height: Screen height
        """
        super().__init__()
        arcade.set_background_color(arcade.color.SMOKY_BLACK)

        self.held_keys = set()

        # TODO: declare anything here you need the game class to track
        self.ship = Ship()
        self.score = 0
        self.bullets = []
        self.asteroids = []
        self.background = arcade.load_texture("images/bgu.jpg")
        #create asteroids
        for i in range(5):
            asteroid = Largeasteroids()
            self.asteroids.append(asteroid)        

        # my add on: Load sounds. Sounds from kenney.nl
        self.fire_sound = arcade.sound.load_sound(":resources:sounds/laser1.wav") 
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion1.wav")
        
    def on_draw(self):
        """
        Called automatically by the arcade framework.
        Handles the responsibility of drawing all elements.
        """

        # clear the screen to begin drawing
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        # TODO: draw each object
        #draw bullets
        for bullet in self.bullets:
            bullet.draw()        

        #draw asteroids
        for asteroid in self.asteroids:
            asteroid.draw()
       
        #do this when ship is alive
        if self.ship.alive:
            #draw the ship
            self.ship.draw()
            #draw the score
            self.draw_score()
            #draw the mini ships representing the ship life
            self.draw_ship_life()

        #if the ship has no more lives it will die
        if self.ship.life <= 0:
            self.ship.alive = False

        #if all the asteroids were cleared show congratulations if the ship died show game over
        if len(self.asteroids) == 0 or self.ship.alive == False:
            view = GameOver() #create and instance of gameover class
            view.score = self.score #copy the score to the gameoverclass
            view.asteroids = self.asteroids #copy the asteroids to the gameoverclass
            self.window.show_view(view) #show the gameoverview
            self.ship.alive = False #hide the ship
  
    def update(self, delta_time):
        """
        Update each object in the game.
        :param delta_time: tells us how much time has actually elapsed
        """
        self.check_keys()
        self.check_collisions()

        # TODO: Tell everything to advance or move forward one step in time
        self.ship.advance()
        self.ship.is_off_screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        #move the bullets
        for bullet in self.bullets:
            bullet.advance()
            bullet.is_off_screen(SCREEN_WIDTH,SCREEN_HEIGHT)   

        #move the asterois
        for asteroid in self.asteroids:
            asteroid.advance()
            asteroid.is_off_screen(SCREEN_WIDTH,SCREEN_HEIGHT)

        #add score while the ship alive
        if self.ship.alive:   
            self.score += delta_time

        # TODO: Check for collisions
    def check_collisions(self):
        """
        Checks to see if bullets have hit asteroids.
        Updates scores and removes dead items.
        :return:
        """

        # NOTE: This assumes you named your asteroids list "asteroids"
        #on progress this should bounce the asteroid when it hit ship and other asteroid
        #ship and asteroid
        for asteroid in self.asteroids:

            # Make sure they are both alive before checking for a collision
            if self.ship.alive and asteroid.alive:
                    too_close = self.ship.radius + asteroid.radius

                    if (abs(self.ship.center.x - asteroid.center.x) < too_close and
                                abs(self.ship.center.y - asteroid.center.y) < too_close):
                        
                            asteroid.alive = False
                            self.ship.life -= 1
                            self.ship.alpha = 1
                            self.score += asteroid.penalty #add the penalty score
                            self.asteroids += asteroid.hit() #add the new asteroids to current list
                            arcade.play_sound(self.hit_sound) #play the sound
                            
        #asteroid to asteroid
        for asteroid1 in self.asteroids:
            for asteroid in self.asteroids:
            # Make sure they are both alive before checking for a collision
            #This will make the asteroid bounce when they hit eachother
                if asteroid1.alive and asteroid.alive:
                        too_close = asteroid1.radius + asteroid.radius

                        if (abs(asteroid1.center.x - asteroid.center.x) < too_close and
                                    abs(asteroid1.center.y - asteroid.center.y) < too_close):        
                    
                            if asteroid.center.x > asteroid1.center.x and asteroid.velocity.dx > asteroid1.velocity.dx:
                                asteroid.bounce_horizontal()
                            
                            if asteroid.center.x < asteroid1.center.x and asteroid.velocity.dx < asteroid1.velocity.dx:
                                asteroid.bounce_horizontal()
                            
                            if asteroid.center.y > asteroid1.center.y and asteroid.velocity.dy > asteroid1.velocity.dy:
                                asteroid.bounce_horizontal()
                            
                            if asteroid.center.y < asteroid1.center.y and asteroid.velocity.dy < asteroid1.velocity.dy:
                                asteroid.bounce_horizontal()
    
                            
        #bullets and asteroid
        for bullet in self.bullets:
            for asteroid in self.asteroids:

                # Make sure they are both alive before checking for a collision
                if bullet.alive and asteroid.alive:
                    too_close = bullet.radius + asteroid.radius

                    if (abs(bullet.center.x - asteroid.center.x) < too_close and
                                abs(bullet.center.y - asteroid.center.y) < too_close):
                        # its a hit!
                        bullet.alive = False #kill the bullet
                        asteroid.alive = False #kill the asteroid
                        self.asteroids += asteroid.hit() #add the new asteroids to current list
                        arcade.play_sound(self.hit_sound) #play sound

                        # We will wait to remove the dead objects until after we
                        # finish going through the list

        # Now, check for anything that is dead, and remove it
        self.cleanup_zombies()

    def cleanup_zombies(self):
        """
        Removes any dead bullets or asteroids from the list.
        :return:
        """
        #clean up bullets
        for bullet in self.bullets:
            if not bullet.alive:
                self.bullets.remove(bullet)

        #clean up asteroids
        for asteroid in self.asteroids:
            if not asteroid.alive:
                self.asteroids.remove(asteroid)

    def check_keys(self):
        """
        This function checks for keys that are being held down.
        You will need to put your own method calls in here.
        """
        if arcade.key.LEFT in self.held_keys:
            self.ship.angle += SHIP_TURN_AMOUNT

        if arcade.key.RIGHT in self.held_keys:
            self.ship.angle -= SHIP_TURN_AMOUNT


        if arcade.key.UP in self.held_keys:
            #move the ship
            self.ship.velocity.dx += math.cos(math.radians(self.ship.angle + 90)) * SHIP_THRUST_AMOUNT
            self.ship.velocity.dy += math.sin(math.radians(self.ship.angle + 90)) * SHIP_THRUST_AMOUNT

            #limit the speed of the ship
            if self.ship.velocity.dx > 10:
                self.ship.velocity.dx = 10
            
            if self.ship.velocity.dx < -10:
                self.ship.velocity.dx = -10
            
            if self.ship.velocity.dy > 10:
                self.ship.velocity.dy = 10
            
            if self.ship.velocity.dy < -10:
                self.ship.velocity.dy = -10

        
        if arcade.key.DOWN in self.held_keys:
            #move the ship
            self.ship.velocity.dx -= math.cos(math.radians(self.ship.angle + 90)) * SHIP_THRUST_AMOUNT
            self.ship.velocity.dy -= math.sin(math.radians(self.ship.angle + 90)) * SHIP_THRUST_AMOUNT

            #limit the speed of the ship
            if self.ship.velocity.dx > 10:
                self.ship.velocity.dx = 10
            
            if self.ship.velocity.dx < -10:
                self.ship.velocity.dx = -10
            
            if self.ship.velocity.dy > 10:
                self.ship.velocity.dy = 10
            
            if self.ship.velocity.dy < -10:
                self.ship.velocity.dy = -10

        # Machine gun mode...
        #if arcade.key.SPACE in self.held_keys:
        #    pass

    def on_key_press(self, key: int, modifiers: int):
        """
        Puts the current key in the set of keys that are being held.
        You will need to add things here to handle firing the bullet.
        """
        if self.ship.alive:
            self.held_keys.add(key)

            if key == arcade.key.SPACE:
                # TODO: Fire the bullet here!
                # Fire!
                ship = self.ship

                #get the instance of bullet then align it with the ship's location and angle
                bullet = Bullet()
                bullet.fire(ship)
                #my addtional sound
                arcade.play_sound(self.fire_sound) #playsound
                self.bullets.append(bullet) #add the new bullet to the list

    def on_key_release(self, key: int, modifiers: int):
        """
        Removes the current key from the set of held keys.
        """
        if key in self.held_keys:
            self.held_keys.remove(key)
            #slow down the ship but will still  looks like floating
            self.ship.velocity.dx = math.cos(math.radians(self.ship.angle + 90)) * SHIP_THRUST_AMOUNT
            self.ship.velocity.dy = math.sin(math.radians(self.ship.angle + 90)) * SHIP_THRUST_AMOUNT

    def draw_score(self):
        """
        Puts the current score on the screen
        """
        score_text = f"Time Lapse: {self.score}"
        start_x = 10
        start_y = SCREEN_HEIGHT - 20
        arcade.draw_text(score_text, start_x=start_x, start_y=start_y, font_size=12, color=arcade.color.WHITE_SMOKE)

    def draw_ship_life(self):
        """
        Draw the mini ships that represent the lives of the ship
        """
        x = 10 #position it to the left
        y = SCREEN_HEIGHT - 30 #position this to the top - 30
        for i in range(self.ship.life):
            img = "images/playerShip1_orange.png"
            texture = arcade.load_texture(img)
            width = texture.width // 4 #reduce the size
            height = texture.height // 4 #reduce the size
            angle = 0 
            alpha = 255
            arcade.draw_texture_rectangle(x, y, width, 
                    height, texture, angle, alpha)
            x += width #add the new mini ship beside the last ship created 

class GameOver(arcade.View):
    """ View to show when game is over """
    def __init__(self):

        super().__init__()

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
        
        arcade.set_background_color(arcade.color.SMOKY_BLACK)
        self.asteroids = []

        self.score = 0.00
        
    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        if len(self.asteroids) > 0:
            self.draw_game_over()
        else:
            self.draw_congratulations()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, re-start the game. """
        game_view = Game()
        self.window.show_view(game_view)

    def draw_congratulations(self):
        """
        Print the message "Congratulations" and show the score(time lapse) 
        """
        self.background = arcade.load_texture("images/congrats.png")
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        lapse = f"Time Lapse: {self.score:.2f}"
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        arcade.draw_text(lapse, start_x=start_x, start_y=start_y, font_size= 20, color=arcade.color.WHITE, anchor_x="center")  
        
    def draw_game_over(self):
        """
        Print the message "Game over" and show the score(time lapse) 
        """
        self.background = arcade.load_texture("images/game_over.png")
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        lapse = f"Time Lapse: {self.score:.2f}"
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        arcade.draw_text(lapse, start_x=start_x, start_y=start_y, font_size= 20, color=arcade.color.WHITE, anchor_x="center")   
        
def main():
    """
    This will initiate the game
    """

    # Creates the game and starts it going
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT)
    start_view = Game()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()