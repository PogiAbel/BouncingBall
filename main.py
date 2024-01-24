import pygame
from pygame import Vector2
import math

class Circle():
    def __init__(self, radius: int, point: Vector2,color, width = 0) -> None:
        self.radius = radius
        self.point = point.copy()
        self.color = color
        self.width = width

    def draw(self):
        pygame.draw.circle(screen, self.color, self.point, self.radius, self.width)
        
    def getPointOnCircle(self, angle: float) -> Vector2:
        return Vector2(self.radius * math.cos(angle), self.radius * math.sin(angle)) + self.point
    
    def pointToCircle(self, point: Vector2) -> Vector2:
        return (point - self.point).normalize() * (self.radius * 0.95) + self.point
    
class Ball (Circle):
    def __init__(self, radius: int, point: Vector2, color,speed,mass, velocity: Vector2 = Vector2(0,0),outline_width=0, outline_color="white") -> None:
        super().__init__(radius, point, color, 0)
        self.radius = radius
        self.point = point.copy()
        self.color = color
        self.sepeed = speed
        self.mass = mass
        self.velocity = velocity
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.original = (radius, point.copy(), color, mass, self.velocity.copy())

    def draw(self):
        if self.outline_width != 0:
            pygame.draw.circle(screen, self.outline_color, self.point, self.radius + self.outline_width, self.outline_width)
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

def Line(point1: Vector2, point2: Vector2, color, width = 1):
    pygame.draw.line(screen, color, point1, point2, width)

def SimpleCollision(ball: Ball, circle: Circle):
    ball.velocity = ball.velocity.reflect(circle.point - ball.point)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((540, 960))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
running = True
dt = 0

# Physics
start_velocity = Vector2(50,-10)
gravitation = Vector2(0, 2)
dump = 0.8
speed = 10

screen_middle = Vector2(screen.get_width() / 2, screen.get_height() / 2)

current_fps = 0

screen.fill("black")

hit_sound = pygame.mixer.Sound("sounds/hit.wav")

offset = Vector2(0,0)

center_circle = Circle(200, screen_middle,"blue", 8)

player_circle = Ball(10, screen_middle - offset, "red", 10, 5,start_velocity.copy(),outline_width=0)

def refresh():
    screen.fill("black")
    
    for x in buttons: 
        x.draw()
    for x in lines:
        Line(x[0], x[1], "white", 2)
        
    center_circle.draw()
    player_circle.draw()

# Buttons
buttons: list[Button] = []
reset_button = Button(10, 10, 100, 50, "green", "Reset", "white", font)
#buttons.append(reset_button)

# Lines
lines : list[Vector2] = []

start = False

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
                        lines.clear()
            case pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start = not start
                if event.key == pygame.K_r:
                    player_circle.reset()
                    lines.clear()
            case pygame.WINDOWMOVED:
                screen_middle = Vector2(screen.get_width() / 2, screen.get_height() / 2)
                continue

    if start:
        
        player_circle.velocity += gravitation * player_circle.mass

        if OutsideCircle(center_circle, player_circle) == True:
            # move inside to the circle
            new_point = (center_circle.point - player_circle.point).normalize() * 2
            player_circle.point += new_point

            # calculate new velocity
            SimpleCollision(player_circle, center_circle)
            
            lines.append((center_circle.pointToCircle(player_circle.point), player_circle.point))
            
            if player_circle.velocity.length() > 16:
                pygame.mixer.Sound.play(hit_sound)
            else:
                player_circle.velocity = Vector2(0,0)
                player_circle.mass = 0
                
        # Velocity calculation
        player_circle.point += player_circle.velocity * dt

        
        # check if player is out of bounds
        if player_circle.radius > center_circle.radius:
            running = False

    refresh()
    pygame.display.flip()

    dt = clock.tick(60) / 1000


pygame.quit()