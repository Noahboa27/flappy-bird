#! /usr/bin/python3
#  This is my first pygame project and hopefully it will be a flappy bird clone.


### TODO: Randomize birds, pipes, and backgrounds


import pygame, sys, random


                            #####################
############################# Game Initializers #############################
                            #####################

# Change the defaults used when .mixer is called
pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
# Starts pygame
pygame.init()

# This is setting the x and y pixal length for the game window
# Think of it like a canvace for a painting
# There can only be one display surface
screen = pygame.display.set_mode((576, 1024))
# Object used for the controlling the games speed
clock = pygame.time.Clock()
# font has to be .ttf and 40 is the size
game_font = pygame.font.Font('04B_19.TTF', 40)

# Game variables
gravity = 0.25
bird_movement = 0
game_active = False
score = 0
high_score = 0
point_switch = False
game_start = True

# You can have as many surfaces as you want
# This will be the background for the game
# .convert() helps the game with files the more complex things get
bg_surface = pygame.image.load('assets/background-night.png').convert()
# This method doubles the size of the image
bg_surface = pygame.transform.scale2x(bg_surface)

floor_surface = pygame.transform.scale2x(pygame.image.load(\
	'assets/base.png').convert())
floor_x_pos = 0
floor_y_pos = 900

# Bird surfaces
bird_upflap = pygame.transform.scale2x(pygame.image.load(\
	'assets/redbird-upflap.png').convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load(\
	'assets/redbird-midflap.png').convert_alpha())
bird_downflap = pygame.transform.scale2x(pygame.image.load(\
	'assets/redbird-downflap.png').convert_alpha())
bird_frames = [bird_upflap, bird_midflap, bird_downflap]
bird_frame_index = 0
bird_surface = bird_frames[bird_frame_index]
bird_rect = bird_surface.get_rect(center = (100, 512))

# Start game surface
start_game_surface = pygame.transform.scale2x(\
	pygame.image.load('assets/message.png').convert_alpha())
start_game_rect = start_game_surface.get_rect(center = (288, 512))

# End game surface
game_over_surface = pygame.transform.scale2x(\
	pygame.image.load('assets/gameover.png').convert_alpha())
game_over_rect = game_over_surface.get_rect(center = (288, 512))

# Pipe surfaces
pipe_surface = pygame.transform.scale2x(pygame.image.load(\
	'assets/pipe-green.png').convert())
pipe_list = []

# Event for spawning pipes
SPAWNPIPE = pygame.USEREVENT
# Every 1.2 seconds this event is triggered
pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height = [450, 600, 750]

# Have to increment for a new event, +2, +3...
BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

# Timer to reset the point flag
POINTFLAG = pygame.USEREVENT + 2
pygame.time.set_timer(POINTFLAG, 600)

# Creates a sound object for each sound
flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
flap_sound.set_volume(0.2)
death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
death_sound.set_volume(0.2)
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
score_sound.set_volume(0.2)


                              ##################
############################### Game Functions ###############################
                              ##################
def draw_floor():
	screen.blit(floor_surface,(floor_x_pos, floor_y_pos))
	screen.blit(floor_surface,(floor_x_pos + 576, floor_y_pos))


def create_pipe():
	random_pipe_height = random.choice(pipe_height)
	bottom_pipe = pipe_surface.get_rect(midtop = (700, random_pipe_height))
	top_pipe = pipe_surface.get_rect(midbottom = (700, random_pipe_height - 300))
	pointbox_rect = pygame.Rect(700, random_pipe_height - 300, 50, 300)
	return bottom_pipe, top_pipe, pointbox_rect


def move_pipes(pipes):
	for pipe in pipes:
		pipe.centerx -= 5
	return pipes


def draw_pipes(pipes):
	for pipe in pipes:
		if pipe.height == 300:
			continue
		elif pipe.bottom >= 1024:
			# Because this is list a rectangles we already have the x and y.
			# So we can simply pass pipe like with the bird rectangle
			screen.blit(pipe_surface, pipe)
		else:
			# The other parameters are bool for x and y
			flip_pipe = pygame.transform.flip(pipe_surface, False, True)
			screen.blit(flip_pipe, pipe)


def check_collision(pipes):
	global point_switch
	global score
	for pipe in pipes:
		# returns true if there is a collision of rectangles
		# have as few collisions as possible for performance
		if bird_rect.colliderect(pipe):
			# This is for the point hitbox
			if pipe.height == 300:
				if point_switch == False:
					score_sound.play()
					score += 1
					point_switch = True
				continue

			death_sound.play()
			return False

	if bird_rect.top <= 0 or bird_rect.bottom >= floor_y_pos:
		death_sound.play()
		return False

	return True


def rotate_bird(bird):
	# rotozoom can scale and rotate
	# pass surface, angle, and scale
	new_bird = pygame.transform.rotozoom(bird, -bird_movement * 4, 1)
	return new_bird


def bird_animation():
	new_bird = bird_frames[bird_frame_index]
	new_bird_rect = new_bird.get_rect(center = (100, bird_rect.centery))
	return new_bird, new_bird_rect


def score_display(game_state):
	if game_state == 'game_on':
		# render (what to display, anti-a, color(RGB))
		score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
		score_rect = score_surface.get_rect(center = (288, 100))
		screen.blit(score_surface, score_rect)

	if game_state == 'game_over':
		score_surface = game_font.render(\
			f'Score: {str(int(score))}', True, (255, 255, 255))
		score_rect = score_surface.get_rect(center = (288, 100))
		screen.blit(score_surface, score_rect)

		high_score_surface = game_font.render(\
			f'High score: {str(int(high_score))}', True, (255, 255, 255))
		high_score_rect = score_surface.get_rect(center = (240, 150))
		screen.blit(high_score_surface, high_score_rect)


def update_score(score, high_score):
	if score > high_score:
		high_score = score
	return high_score


                        ##############################
######################### This is the main game loop #########################
                        ##############################
while True:
	# This loop is constantly looking for events or changes
	for event in pygame.event.get():
		# QUIT = red x button
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		# Checks to see if any key is pressed
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE and game_active:
				bird_movement = 0
				bird_movement -= 11
				flap_sound.play()
			if event.key == pygame.K_SPACE and game_active == False:
				game_active = True
				game_start = False
				pipe_list.clear()
				bird_rect.center = (100, 512)
				bird_movement = 0
				score = 0
		if event.type == SPAWNPIPE:
			# extend makes whatever you return fit in the list
			pipe_list.extend(create_pipe())
		if event.type == BIRDFLAP:
			if bird_frame_index < 2:
				bird_frame_index += 1
			else:
				bird_frame_index = 0

			bird_surface, bird_rect = bird_animation()
		if event.type == POINTFLAG:
			point_switch = False

	# blit() adds a surface to the display surface
	# Uses x and y coor to place and the origin is at the top left
	screen.blit(bg_surface,(0, 0))

	if game_active:
		# Bird Movement
		bird_movement += gravity
		rotated_bird = rotate_bird(bird_surface)

		# centerx and centery are used to move the rectangle
		bird_rect.centery += round(bird_movement)
		screen.blit(rotated_bird, bird_rect)
		game_active = check_collision(pipe_list)

		# Pipes
		pipe_list = move_pipes(pipe_list)
		draw_pipes(pipe_list)

		# Score
		score_display('game_on')
	elif game_active == False and game_start:
		screen.blit(start_game_surface, start_game_rect)
	else:
		high_score = update_score(score, high_score)
		screen.blit(game_over_surface, game_over_rect)
		score_display('game_over')
	
	# Floor Movement
	floor_x_pos -= 1
	draw_floor()
	if floor_x_pos <= -576:
		floor_x_pos = 0
	

	pygame.display.update()
	# This is the framerate I am setting the game to run at
	clock.tick(120)
