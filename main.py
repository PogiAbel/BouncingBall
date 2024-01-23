from cgitb import reset
from hmac import new
from pdb import run
from types import coroutine
import pygame
import math

class Circle():
    def __init__(self, radius: int, point: pygame.Vector2,color, width = 0) -> None:
        self.radius = radius
        self.point = point.copy()
        self.color = color
        self.width = width

    def draw(self):
        pygame.draw.circle(screen, self.color, self.point, self.radius, self.width)

class Ball (Circle):
    def __init__(self, radius: int, point: pygame.Vector2, color,mass) -> None:
        super().__init__(radius, point, color, 0)
        self.radius = radius
        self.point = point.copy()
        self.color = color
        self.mass = mass
        self.velocity = pygame.Vector2(0,0)
        self.original = (radius, point.copy(), color, mass, self.velocity.copy())

    def draw(self):
        self.point += self.velocity * dt
        pygame.draw.circle(screen, self.color, self.point, self.radius, self.width)

    def reset(self):
        self.radius = self.original[0]
        self.point = self.original[1].copy()
        self.color = self.original[2]
        self.mass = self.original[3]
        self.velocity = self.original[4].copy()

    

class Button:
    def __init__(self, x, y, width, height, color, text, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.font = font
        self.text_surface = font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center = self.rect.center)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def is_clicked(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False

    def set_text(self, text):
        self.text = text
        self.text_surface = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center = self.rect.center)

    def set_color(self, color):
        self.color = color

    def set_text_color(self, color):
        self.text_color = color
        self.text_surface = self.font.render(self.text, True, self.text_color)

    def set_font(self, font):
        self.font = font
        self.text_surface = self.font.render(self.text, True, self.text_color)

def OutsideCircle(outer_circle: Circle, inner_circle: Circle):
    if outer_circle.point.distance_squared_to(inner_circle.point) < (outer_circle.radius - inner_circle.radius) ** 2:
        return False
    return True

def HitVelocityChange(velocity1: pygame.Vector2, mass1: int, mass2: int = 100, velocit2: pygame.Vector2 = pygame.Vector2(0,0)):
    new_velocity = (velocity1 * (mass1 - mass2) + (2 * mass2 * velocit2)) / (mass1 + mass2)
    print(new_velocity)
    return new_velocity


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
running = True
dt = 0

# Physics
start_velocity = pygame.Vector2(50,-10)
gravitation = pygame.Vector2(0, 1)
speed = 10

screen_middle = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

current_fps = 0

screen.fill("black")

hit_sound = pygame.mixer.Sound("hit.wav")

offset = pygame.Vector2(0,0)

center_circle = Circle(200, screen_middle,"blue", 3)

player_circle = Ball(10, screen_middle - offset, "red", 1)
player_circle_2 = Ball(30, screen_middle - offset, "green", 30)

def refresh():
    screen.fill("black")
    center_circle.draw()
    player_circle.draw()
    player_circle_2.draw()
    for x in buttons: 
        x.draw()

# Buttons
buttons: list[Button] = []
reset_button = Button(10, 10, 100, 50, "green", "Reset", "white", font)
buttons.append(reset_button)


velocity = start_velocity.copy()

while running:

    # set variables
    current_fps+=1

    # poll for events
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if reset_button.is_clicked(event.pos):
                        player_circle.reset()
                        player_circle_2.reset()
                        velocity = start_velocity.copy()


    if OutsideCircle(center_circle, player_circle) == True:
        new_point = (center_circle.point - player_circle.point).normalize() * 2
        player_circle.point += new_point
        #player_circle.velocity = pygame.Vector2(center_circle.point - player_circle.point).normalize() * velocity.length()
        player_circle.velocity += HitVelocityChange(player_circle.velocity, player_circle.mass)
        if velocity.length() > 1:
            pygame.mixer.Sound.play(hit_sound)
            #player_circle.radius += 5
            #player_circle.mass = player_circle.radius / 10
        else:
            player_circle.velocity = pygame.Vector2(0,0)

    if OutsideCircle(center_circle, player_circle_2) == True:
        new_point = (center_circle.point - player_circle_2.point).normalize() * 2
        player_circle_2.point += new_point
        player_circle_2.velocity = pygame.Vector2(center_circle.point - player_circle_2.point).normalize() * velocity.length()
        if velocity.length() > 1:
            pygame.mixer.Sound.play(hit_sound)
            #player_circle_2.radius += 5
            #player_circle_2.mass = player_circle_2.radius / 10
        else:
            player_circle_2.velocity = pygame.Vector2(0,0)
            
    # Velocity calculation
    player_circle.velocity += gravitation * player_circle.mass * dt
    player_circle_2.velocity += gravitation * player_circle_2.mass * dt

    
    # check if player is out of bounds
    if player_circle.radius > center_circle.radius:
        running = False

    refresh()
    pygame.display.flip()

    dt = clock.tick(60) / 1000


pygame.quit()