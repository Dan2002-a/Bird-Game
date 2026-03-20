import time
import pygame
import random
import os
from pygame import mixer

# --- FIX WORKING DIRECTORY ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- INITIALIZATION ---
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

# --- WINDOW SETUP ---
surfaceWidth = 1200
surfaceHeight = 700
surface = pygame.display.set_mode((surfaceWidth, surfaceHeight))
pygame.display.set_caption('BIRD GAME')
clock = pygame.time.Clock()

# --- COLORS ---
white = (255, 255, 255)
gold = (255, 215, 0) # For high score celebration

# --- BIRD CLASS ---
class Bird():
    def __init__(self, x, y, fly_imgs, hit_imgs):
        self.x = x
        self.y = y
        self.fly_images = [pygame.transform.scale(img, (75, 60)) for img in fly_imgs]
        self.hit_images = [pygame.transform.scale(img, (75, 60)) for img in hit_imgs]
        self.index = 0
        self.counter = 0
        self.is_hit = False 
        self.texture = self.fly_images[self.index]
        self.width = self.texture.get_size()[0]
        self.height = self.texture.get_size()[1]
        self.velocity = 0
        self.gravity = 0.4

    def animate(self):
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            current_set = self.hit_images if self.is_hit else self.fly_images
            self.index = (self.index + 1) % len(current_set)
            self.texture = current_set[self.index]

    def move(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.animate()

    def flap(self):
        if not self.is_hit:
            self.velocity = -9

    def draw(self):
        surface.blit(self.texture, (self.x, self.y))

# --- ASSETS LOADING ---
bg_img = pygame.transform.scale(pygame.image.load('assets/bckgrnd4.2.gif'), (surfaceWidth, surfaceHeight)).convert()
start_bg = pygame.transform.scale(pygame.image.load('assets/StartText2.png'), (surfaceWidth, surfaceHeight)).convert()
pipe_top_img = pygame.image.load('assets/p_top.png').convert_alpha()
pipe_bottom_img = pygame.image.load('assets/p_bottom.png').convert_alpha()

fly_frames = [pygame.image.load(f'assets/fly{i}.png').convert_alpha() for i in range(1, 4)]
hit_frames = [pygame.image.load(f'assets/hit{i}.png').convert_alpha() for i in range(1, 3)]

# --- AUDIO ---
def play_bg_music():
    if os.path.exists('BG_Music.wav'):
        mixer.music.load('BG_Music.wav')
        mixer.music.set_volume(0.3)
        mixer.music.play(-1)

def play_gameover_music():
    path = 'assets/gameover.mp3'
    if os.path.exists(path):
        mixer.music.load(path)
        mixer.music.set_volume(0.6)
        mixer.music.play(0)

try:
    point_sound = mixer.Sound('assets/point.mp3')
    celebration_sound = mixer.Sound('assets/celebration.mp3') # Celebration SFX
    celebration_sound.set_volume(0.9)
except:
    point_sound = None
    celebration_sound = None

# --- HELPERS ---
def get_high_score():
    if not os.path.exists("highscore.txt"): return 0
    with open("highscore.txt", "r") as f:
        try: return int(f.read())
        except: return 0

def save_high_score(new_score):
    if new_score > get_high_score():
        with open("highscore.txt", "w") as f: f.write(str(new_score))

def draw_pipes(x, h, w, g):
    surface.blit(pygame.transform.scale(pipe_top_img, (w, h)), (x, 0))
    b_height = surfaceHeight - (h + g)
    surface.blit(pygame.transform.scale(pipe_bottom_img, (w, b_height)), (x, h + g))

# --- MAIN LOOP ---
def main():
    play_bg_music()
    while True:
        player = Bird(200, 300, fly_frames, hit_frames)
        bg_x, bg_speed = 0, 3
        pipe_x, pipe_width = surfaceWidth + 400, 120 
        pipe_height = random.randint(100, 400)
        pipe_gap = 220 
        pipe_speed = 6
        
        score = 0
        passed = False
        game_active = False
        show_over_ui = False
        music_switched = False
        high_score_achieved = False # Flag for celebration
        
        current_high = get_high_score()
        
        # Start Screen
        while not game_active:
            surface.blit(start_bg, (0, 0))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True

        # Game Loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not player.is_hit: player.flap()
                    elif show_over_ui: main()

            if not show_over_ui:
                player.move()
                if not player.is_hit:
                    pipe_x -= pipe_speed
                    bg_x -= bg_speed
                    if bg_x <= -surfaceWidth: bg_x = 0

                # Collision
                if player.y + player.height > surfaceHeight or player.y < 0:
                    player.is_hit = True
                if not player.is_hit and player.x + player.width > pipe_x and player.x < pipe_x + pipe_width:
                    if player.y < pipe_height or player.y + player.height > pipe_height + pipe_gap:
                        player.is_hit = True

                # Game Over Music Trigger
                if player.is_hit and not music_switched:
                    mixer.music.stop()
                    play_gameover_music()
                    music_switched = True

                # Scoring Logic
                if not passed and not player.is_hit and player.x > pipe_x + pipe_width:
                    score += 1
                    passed = True
                    
                    # CELEBRATION CHECK
                    if score > current_high and not high_score_achieved:
                        if celebration_sound: celebration_sound.play()
                        high_score_achieved = True
                    elif point_sound:
                        point_sound.play()
                        
                if pipe_x < -pipe_width:
                    pipe_x, pipe_height, passed = surfaceWidth, random.randint(100, 400), False

            # Draw Everything
            surface.blit(bg_img, (bg_x, 0))
            surface.blit(bg_img, (bg_x + surfaceWidth, 0))
            draw_pipes(pipe_x, pipe_height, pipe_width, pipe_gap)
            player.draw()
            
            # Scores UI
            fontS = pygame.font.Font('freesansbold.ttf', 30)
            score_color = gold if high_score_achieved else white
            surface.blit(fontS.render(f"Score: {score}", True, score_color), (30, 30))
            surface.blit(fontS.render(f"High Score: {current_high}", True, (200, 200, 200)), (30, 70))

            if player.is_hit and player.y + player.height >= surfaceHeight:
                show_over_ui = True
                save_high_score(score)
                fontL = pygame.font.Font('freesansbold.ttf', 80)
                
                msg_text = "GAME OVER"
                if high_score_achieved: msg_text = "NEW RECORD!"
                
                msg = fontL.render(msg_text, True, score_color)
                surface.blit(msg, msg.get_rect(center=(surfaceWidth/2, surfaceHeight/2 - 40)))
                retry = fontS.render("Press SPACE to Restart", True, white)
                surface.blit(retry, retry.get_rect(center=(surfaceWidth/2, surfaceHeight/2 + 60)))

            pygame.display.update()
            clock.tick(60)

if __name__ == "__main__":
    main()