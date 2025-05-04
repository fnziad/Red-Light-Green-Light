from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import sys
import time

# --- Configuration ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
NEAR_CLIP = 1.0
FAR_CLIP = 150000

# Game settings
GAME_VERSION = "2.0"
GAME_TITLE = "Squid Game: Red Light Green Light"
GAME_STATE = "start"  # Start with start screen
STATE_TIMER = 0
STATE_CHANGE_INTERVAL_MIN = 3.0  # Initial timing values, will be adjusted based on game progression
STATE_CHANGE_INTERVAL_MAX = 7.0  # Initial timing values, will be adjusted based on game progression
NEXT_STATE_CHANGE = random.uniform(STATE_CHANGE_INTERVAL_MIN, STATE_CHANGE_INTERVAL_MAX)
DOLL_ROTATION_SPEED = 180.0  # Degrees per second
DOLL_TARGET_ROTATION = 0  # 0 = facing player (red light), 180 = facing away (green light)
DOLL_CURRENT_ROTATION = 180  # Start facing away

# Game phases for dynamic difficulty
GAME_PHASE = 1
GAME_START_TIME = 0
CURRENT_GAME_TIME = 0
PHASE_DURATION = 30.0  # Time in seconds before increasing difficulty

# Performance settings
ENABLE_VSYNC = True
USE_FRAME_LIMITING = True
TARGET_FPS = 60
MAX_VISIBLE_TREES = 1500
PLAYER_SMOOTHING = 12.0
CAMERA_SMOOTHING = 15.0
PERFORMANCE_MODE = False

# --- Playable Area Definition ---
PLAY_AREA_WIDTH = 4000
PLAY_AREA_LENGTH = 15000
FINISH_ZONE_LENGTH = 1000

# Forest Generation
FOREST_BUFFER = 10000
TOTAL_AREA_WIDTH = PLAY_AREA_WIDTH + FOREST_BUFFER * 2
TOTAL_AREA_LENGTH = PLAY_AREA_LENGTH + FINISH_ZONE_LENGTH + FOREST_BUFFER * 2
FOREST_DENSITY = 6000
MIN_TREE_DISTANCE = 55

# Visual Settings
sky_color_top = (0.65, 0.85, 1.0)
sky_color_horizon = (0.95, 0.95, 1.0)
FOG_COLOR = (0.90, 0.88, 0.82)
FOG_DENSITY = 0.000065

fovY = 70

# Player attributes
player_start_pos = [0, -PLAY_AREA_LENGTH/2 + 50, 15]  # Start slightly inside arena
player_position = list(player_start_pos)
target_player_position = list(player_start_pos)
player_velocity = [0.0, 0.0, 0.0]  # Added for friction movement
player_friction = 0.88  # Movement friction factor (was 0.85 - slightly increased)
player_direction = 90.0
target_player_direction = 90.0
player_move_speed = 900.0
player_base_speed = 900.0  # Base speed for reference
player_height = 30
player_width = 15
player_is_moving = False
player_was_caught = False
player_reached_finish = False
player_speed_boost_active = False
player_speed_boost_timer = 0.0
player_speed_boost_duration = 5.0  # 5 seconds of speed boost

# Enemy attributes
enemies = []
NUM_RED_ENEMIES = 6  # Reduced from 8
NUM_BLUE_ENEMIES = 4  # Reduced from 5
NUM_BLACK_ENEMIES = 2  # Unchanged
ENEMY_MOVE_SPEED_RED = 350.0       # Drastically reduced from 600.0
ENEMY_MOVE_SPEED_BLUE = 250.0      # Drastically reduced from 450.0 
ENEMY_MOVE_SPEED_BLACK = 150.0     # Drastically reduced from 250.0
ENEMY_HEIGHT = 60                  # Increased from 45
ENEMY_WIDTH = 40                   # Increased from 28
ENEMY_DETECTION_RADIUS = 30.0  # For movement detection during red light

# Weapon attributes
BULLET_SPEED = 1200.0  # Reduced from 2500.0 for better collision detection
bullets = []
bullet_cooldown = 0
BULLET_COOLDOWN_TIME = 0.4  # Slightly faster firing rate
BULLET_SIZE = 8.0  # Added defined bullet size for clarity

# Power-ups
powerups = []
NUM_POWERUPS = 3
POWERUP_SPAWN_INTERVAL = 20.0  # Time in seconds between powerup spawns
powerup_spawn_timer = 0.0

# --- Camera Attributes ---
camera_height = 45
camera_distance_min = 40.0
camera_distance_max = 1200.0
camera_distance = 250.0
camera_pitch_min = -85.0
camera_pitch_max = 70.0
camera_pitch = -10.0
target_camera_pitch = camera_pitch
camera_yaw = 0.0
target_camera_yaw = camera_yaw
camera_rotation_speed = 120.0

# Sun attributes
sun_size = 450
sun_color = (1.0, 0.97, 0.85)
sun_position = [TOTAL_AREA_WIDTH * 0.3, (PLAY_AREA_LENGTH/2 + FINISH_ZONE_LENGTH) * 1.2, 80000]

# --- Doll Configuration ---
DOLL_SCALE_FACTOR = 0.55
DOLL_BASE_HEIGHT = 8000 * DOLL_SCALE_FACTOR
DOLL_WIDTH = DOLL_BASE_HEIGHT * 0.20
DOLL_DEPTH = DOLL_BASE_HEIGHT * 0.18
DOLL_POSITION = [0, PLAY_AREA_LENGTH / 2, 0]  # Base exactly at finish line start

# Static environment elements
fixed_plants = []
plant_positions = set()

# Input state tracking
keys_pressed = set()
last_positions = {}  # To track movement for red light detection

# Scoring
player_score = 0
time_survived = 0.0
enemies_killed = 0

# Korean dialogue for Squid Game authenticity (using English text with Korean terms)
DIALOGUE_RED_LIGHT = "RED LIGHT! (Mugunghwa Kkochi Pieosseumnida!)"
DIALOGUE_GREEN_LIGHT = "GREEN LIGHT! (Chorok Bul-iya!)"
DIALOGUE_YELLOW_WARNING = "WARNING! RED LIGHT COMING! (Juuiha-seyo!)"

# Timing / Debug
print_debug = False
last_update_time = 0
fps_last_time = 0
frame_count = 0
fps = 0

# --- Utility & Setup Functions ---
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(0.0, 0.0, 0.0)):
    """Renders text on screen at specified position with improved visibility."""
    glColor3fv(color)
    glWindowPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))

def draw_centered_text(text, y_pos, font=GLUT_BITMAP_TIMES_ROMAN_24, color=(0.0, 0.0, 0.0)):
    """Renders text centered on screen at specified y position with improved visibility."""
    text_width = 0
    for char in text:
        text_width += glutBitmapWidth(font, ord(char))
    x_pos = (WINDOW_WIDTH - text_width) // 2
    draw_text(x_pos, y_pos, text, font, color)

def setup_fixed_environment():
    """Generate the forest and environmental objects."""
    global fixed_plants, plant_positions
    
    random.seed(12345)  # Use fixed seed for consistent layout
    plant_positions.clear()
    fixed_plants.clear()
    
    print(f"Generating environment (Target Density: {FOREST_DENSITY})...")
    attempts, plant_count = 0, 0
    
    half_play_w = PLAY_AREA_WIDTH / 2
    play_area_start_y = -PLAY_AREA_LENGTH / 2
    play_area_end_y = PLAY_AREA_LENGTH / 2
    finish_zone_end_y = play_area_end_y + FINISH_ZONE_LENGTH
    
    half_total_w = TOTAL_AREA_WIDTH / 2
    half_total_l = TOTAL_AREA_LENGTH / 2
    
    grid_size = MIN_TREE_DISTANCE * 2
    grid = {}
    max_attempts = FOREST_DENSITY * 5
    
    print(f"Arena Bounds: X[-{half_play_w}, {half_play_w}], Y[{play_area_start_y}, {play_area_end_y}]")
    print(f"Finish Zone: Y[{play_area_end_y}, {finish_zone_end_y}]")
    
    while plant_count < FOREST_DENSITY and attempts < max_attempts:
        attempts += 1
        
        # Generate random position
        x = random.uniform(-half_total_w, half_total_w)
        y = random.uniform(-half_total_l, half_total_l)
        
        # Check if inside playable area (we don't want plants there)
        is_inside_x = -half_play_w < x < half_play_w
        is_inside_y = play_area_start_y < y < finish_zone_end_y
        if is_inside_x and is_inside_y:
            continue
        
        # Check for minimum distance using grid system
        grid_x, grid_y = int((x + half_total_w) / grid_size), int((y + half_total_l) / grid_size)
        too_close = False
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell_key = (grid_x + dx, grid_y + dy)
                if cell_key in grid:
                    for px, py in grid[cell_key]:
                        if (x - px)**2 + (y - py)**2 < MIN_TREE_DISTANCE**2:
                            too_close = True
                            break
                    if too_close:
                        break
            if too_close:
                break
                
        if too_close:
            continue
            
        # Add to grid and plant list
        cell_key = (grid_x, grid_y)
        if cell_key not in grid:
            grid[cell_key] = []
        grid[cell_key].append((x, y))
        
        plant_positions.add((x, y))
        plant_count += 1
        
        plant_data = {'x': x, 'y': y}
        is_tree = random.random() < 0.90
        
        if is_tree:
            tree_type = random.choice([0, 1])
            height = random.uniform(180, 700)
            z_rot = random.uniform(0, 360)
            g = random.uniform(0.3, 0.55)
            r = random.uniform(0.0, 0.1 * g)
            b = random.uniform(0.0, 0.15 * g)
            
            plant_data.update({
                'plant': 'tree',
                'type': tree_type,
                'height': height,
                'color': (r, g, b),
                'z_rot': z_rot
            })
            
            if tree_type == 1:
                foliage_radius = height / 4.0
                num_clumps = 4
                clump_details = []
                
                for i in range(num_clumps):
                    ox = random.uniform(-foliage_radius * 0.5, foliage_radius * 0.5) * (1.0 - i / num_clumps)
                    oy = random.uniform(-foliage_radius * 0.5, foliage_radius * 0.5) * (1.0 - i / num_clumps)
                    oz = random.uniform(foliage_radius * 0.1, foliage_radius * 0.6) + i * (foliage_radius * 0.1)
                    csize = foliage_radius * random.uniform(0.5, 0.8) * (1.0 - i / (num_clumps * 1.5))
                    clump_details.append({'ox': ox, 'oy': oy, 'oz': oz, 'size': csize})
                
                plant_data['clump_details'] = clump_details
        else:
            size = random.uniform(60, 120)
            g = random.uniform(0.35, 0.65)
            r = random.uniform(0.05, 0.15 * g)
            b = random.uniform(0.1, 0.2 * g)
            
            plant_data.update({
                'plant': 'bush',
                'size': size,
                'color': (r, g, b)
            })
            
            num_spheres = 3
            sphere_details = []
            
            for _ in range(num_spheres):
                ox = random.uniform(-size * 0.3, size * 0.3)
                oy = random.uniform(-size * 0.3, size * 0.3)
                oz = random.uniform(-size * 0.1, size * 0.1)
                ssize = size * random.uniform(0.45, 0.75)
                sphere_details.append({'ox': ox, 'oy': oy, 'oz': oz, 'size': ssize})
            
            plant_data['sphere_details'] = sphere_details
            
        fixed_plants.append(plant_data)
    
    print(f"Generated {plant_count} background plants.")
    
    # Sort by distance from center for rendering optimization
    fixed_plants.sort(key=lambda p: p['x']**2 + p['y']**2)
    
    # Reset random seed
    random.seed()

def setup_enemies():
    """Create enemy characters at positions ahead of the player."""
    global enemies
    enemies.clear()
    
    half_play_w = PLAY_AREA_WIDTH / 2 - 50
    
    # Red enemies - fastest, 1 hit
    for _ in range(NUM_RED_ENEMIES):
        x = random.uniform(-half_play_w, half_play_w)
        # Place enemies ahead of player, toward the finish line
        y = random.uniform(0, PLAY_AREA_LENGTH / 2 - 500)
        direction = random.uniform(0, 360)
        
        enemy = {
            'position': [x, y, 0],
            'direction': direction,
            'speed': ENEMY_MOVE_SPEED_RED * random.uniform(0.9, 1.1),
            'color': (0.95, 0.2, 0.2),  # Red
            'type': 'red',
            'health': 1,
            'alive': True,
            'last_position': [x, y, 0]
        }
        enemies.append(enemy)
    
    # Blue enemies - medium speed, 2 hits
    for _ in range(NUM_BLUE_ENEMIES):
        x = random.uniform(-half_play_w, half_play_w)
        y = random.uniform(0, PLAY_AREA_LENGTH / 2 - 500)
        direction = random.uniform(0, 360)
        
        enemy = {
            'position': [x, y, 0],
            'direction': direction,
            'speed': ENEMY_MOVE_SPEED_BLUE * random.uniform(0.9, 1.1),
            'color': (0.2, 0.3, 0.9),  # Blue
            'type': 'blue',
            'health': 2,
            'alive': True,
            'last_position': [x, y, 0]
        }
        enemies.append(enemy)
    
    # Black enemies - slow but tough, 5 hits
    for _ in range(NUM_BLACK_ENEMIES):
        x = random.uniform(-half_play_w, half_play_w)
        y = random.uniform(0, PLAY_AREA_LENGTH / 2 - 500)
        direction = random.uniform(0, 360)
        
        enemy = {
            'position': [x, y, 0],
            'direction': direction,
            'speed': ENEMY_MOVE_SPEED_BLACK * random.uniform(0.9, 1.1),
            'color': (0.1, 0.1, 0.1),  # Black
            'type': 'black',
            'health': 5,
            'scale': 2.0,  # Bigger enemy (increased from 1.5)
            'alive': True,
            'last_position': [x, y, 0]
        }
        enemies.append(enemy)

def setup_powerups():
    """Initialize power-ups across the playing field."""
    global powerups
    powerups.clear()
    
    half_play_w = PLAY_AREA_WIDTH / 2 - 100
    
    for _ in range(NUM_POWERUPS):
        x = random.uniform(-half_play_w, half_play_w)
        # Place powerups ahead of player, toward the finish line
        y = random.uniform(-PLAY_AREA_LENGTH / 4, PLAY_AREA_LENGTH / 2 - 500)
        
        powerup = {
            'position': [x, y, 15],
            'type': 'speed',  # Currently only speed boost
            'active': True,
            'rotation': 0.0  # For spinning effect
        }
        powerups.append(powerup)

# --- Drawing Functions ---
def draw_sky():
    """Draw sky gradient."""
    viewport = glGetIntegerv(GL_VIEWPORT)
    
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, viewport[2], 0, viewport[3])
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)
    
    glBegin(GL_QUADS)
    glColor3fv(sky_color_top)
    glVertex2f(0, viewport[3])
    glVertex2f(viewport[2], viewport[3])
    glColor3fv(sky_color_horizon)
    glVertex2f(viewport[2], 0)
    glVertex2f(0, 0)
    glEnd()
    
    glDepthMask(GL_TRUE)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

def draw_fixed_sun():
    """Draw the sun in the sky."""
    glPushMatrix()
    glTranslatef(sun_position[0], sun_position[1], sun_position[2])
    
    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)
    glDisable(GL_LIGHTING)
    
    glColor3fv(sun_color)
    glutSolidSphere(sun_size, 20, 16)
    
    # Glow effect
    glColor4f(sun_color[0], sun_color[1], sun_color[2], 0.15)
    glutSolidSphere(sun_size * 1.4, 16, 12)
    
    glEnable(GL_LIGHTING)
    glDepthMask(GL_TRUE)
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()

def draw_fixed_tree(plant_data):
    """Draw a tree at the specified position."""
    x = plant_data['x']
    y = plant_data['y']
    type = plant_data['type']
    height = plant_data['height']
    color = plant_data['color']
    z_rot = plant_data['z_rot']
    
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(z_rot, 0, 0, 1)
    
    # Draw trunk
    trunk_scale = 1.0
    trunk_radius = max(2.5 * trunk_scale, height / 22.0)
    trunk_height = height / 2.6
    
    glColor3f(0.40, 0.28, 0.18)
    quadric = gluNewQuadric()
    slices = 6
    gluCylinder(quadric, trunk_radius, trunk_radius * 0.3, trunk_height, slices, 2)
    gluDeleteQuadric(quadric)
    
    # Draw foliage
    glTranslatef(0, 0, trunk_height * 0.7)
    glColor3fv(color)
    
    if type == 0:
        # Pine tree
        glutSolidCone(height / 5.0, height * 0.85, 8, 4)
    else:
        # Deciduous tree
        if 'clump_details' in plant_data:
            clump_scale = 1.0
            for clump in plant_data['clump_details']:
                glPushMatrix()
                glTranslatef(clump['ox'] * clump_scale, clump['oy'] * clump_scale, clump['oz'] * clump_scale)
                slices, stacks = (6, 5)
                glutSolidSphere(clump['size'] * clump_scale, slices, stacks)
                glPopMatrix()
        else:
            glutSolidSphere(height / 4.0, 6, 5)
    
    glPopMatrix()

def draw_fixed_bush(plant_data):
    """Draw a bush at the specified position."""
    x = plant_data['x']
    y = plant_data['y']
    size = plant_data['size']
    color = plant_data['color']
    
    glPushMatrix()
    glTranslatef(x, y, size * 0.3)
    glColor3fv(color)
    
    if 'sphere_details' in plant_data:
        for sphere in plant_data['sphere_details']:
            glPushMatrix()
            glTranslatef(sphere['ox'], sphere['oy'], sphere['oz'])
            glutSolidSphere(sphere['size'], 5, 4)
            glPopMatrix()
    else:
        glutSolidSphere(size * 0.6, 5, 4)
    
    glPopMatrix()

def draw_fixed_plants():
    """Draw all plants in the environment."""
    visible_count = 0
    
    for i, plant_data in enumerate(fixed_plants):
        if i >= MAX_VISIBLE_TREES:
            break
            
        visible_count += 1
        
        if plant_data['plant'] == 'tree':
            draw_fixed_tree(plant_data)
        elif plant_data['plant'] == 'bush':
            draw_fixed_bush(plant_data)
    
    return visible_count

def draw_field():
    """Draw the checkered playing field."""
    # --- Temporarily disable lighting for pure colors ---
    lighting_enabled = glIsEnabled(GL_LIGHTING)
    if lighting_enabled:
        glDisable(GL_LIGHTING)

    # Draw checkerboard ground pattern
    checker_z = 0.0
    half_play_w = PLAY_AREA_WIDTH / 2
    play_area_start_y = -PLAY_AREA_LENGTH / 2
    play_area_end_y = PLAY_AREA_LENGTH / 2
    
    # Define grid parameters for checker pattern
    CHECKER_COLS = 20   # Increase for more squares
    CHECKER_ROWS = 60   # Increase for more squares
    tile_width = PLAY_AREA_WIDTH / CHECKER_COLS
    tile_length = PLAY_AREA_LENGTH / CHECKER_ROWS
    
    # Colors changed to be less confusing with red enemies
    checker_color1 = (0.9, 0.9, 0.9)  # Light gray/white
    checker_color2 = (0.6, 0.8, 0.4)  # Light green instead of red/purple
    
    glBegin(GL_QUADS)
    for r in range(CHECKER_ROWS):
        for c in range(CHECKER_COLS):
            x_start = -half_play_w + c * tile_width
            y_start = play_area_start_y + r * tile_length
            x_end = x_start + tile_width
            y_end = y_start + tile_length
            
            if (r + c) % 2 == 0:
                glColor3fv(checker_color1)
            else:
                glColor3fv(checker_color2)
                
            glVertex3f(x_start, y_start, checker_z)
            glVertex3f(x_end, y_start, checker_z)
            glVertex3f(x_end, y_end, checker_z)
            glVertex3f(x_start, y_end, checker_z)
    glEnd()

    # Progress markers every 20% of the track
    marker_count = 5
    marker_width = 10.0
    for i in range(1, marker_count):
        progress_y = play_area_start_y + (play_area_end_y - play_area_start_y) * (i / marker_count)
        
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 0.0)  # Yellow marker
        glVertex3f(-half_play_w, progress_y - marker_width/2, checker_z + 0.5)
        glVertex3f(half_play_w, progress_y - marker_width/2, checker_z + 0.5)
        glVertex3f(half_play_w, progress_y + marker_width/2, checker_z + 0.5)
        glVertex3f(-half_play_w, progress_y + marker_width/2, checker_z + 0.5)
        glEnd()
        
        # Draw percentage text
        text_z = checker_z + 0.6
        percentage = i * 20
        glPushMatrix()
        glTranslatef(0, progress_y, text_z)
        glRotatef(90, 1, 0, 0)
        glScalef(0.15, 0.15, 0.15)
        glColor3f(0.0, 0.0, 0.0)
        # Note: In a real implementation, you would render text here
        # This is simplified since glutStrokeCharacter doesn't render well at angle
        glPopMatrix()

    # Make the finish line more visible - add flashing effect
    finish_zone_z = 0.05
    finish_zone_start_y = play_area_end_y - 100  # Move finish zone slightly before end for more lenient win
    finish_zone_end_y = finish_zone_start_y + FINISH_ZONE_LENGTH + 200  # Make it wider
    finish_zone_start_x = -half_play_w
    finish_zone_end_x = half_play_w
    
    # Draw finish zone slightly above main ground with a flashing effect
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(-1.0, -1.0)
    
    # Flashing effect based on time
    flash_intensity = 0.7 + 0.3 * math.sin(time.time() * 5.0)  # Oscillate between 0.7 and 1.0
    
    # Draw main white finish zone
    glBegin(GL_QUADS)
    glColor3f(flash_intensity, flash_intensity, flash_intensity)  # Flashing white
    glVertex3f(finish_zone_start_x, finish_zone_start_y, finish_zone_z)
    glVertex3f(finish_zone_end_x, finish_zone_start_y, finish_zone_z)
    glVertex3f(finish_zone_end_x, finish_zone_end_y, finish_zone_z)
    glVertex3f(finish_zone_start_x, finish_zone_end_y, finish_zone_z)
    glEnd()
    
    # Draw a FINISH line text on the ground
    # Draw several checkered strips across the finish line for better visibility
    strip_count = 10
    strip_width = PLAY_AREA_WIDTH / strip_count
    
    for i in range(strip_count):
        if i % 2 == 0:
            glColor3f(0.0, 0.0, 0.0)  # Black
        else:
            glColor3f(1.0, 1.0, 1.0)  # White
            
        start_x = -half_play_w + i * strip_width
        end_x = start_x + strip_width
        
        # Draw checkered strip at finish line
        glBegin(GL_QUADS)
        glVertex3f(start_x, finish_zone_start_y - 20, finish_zone_z + 0.1)
        glVertex3f(end_x, finish_zone_start_y - 20, finish_zone_z + 0.1)
        glVertex3f(end_x, finish_zone_start_y + 20, finish_zone_z + 0.1)
        glVertex3f(start_x, finish_zone_start_y + 20, finish_zone_z + 0.1)
        glEnd()
    
    # Add "FINISH" text in 3D
    # Since glutStrokeCharacter doesn't work well in 3D orientation,
    # we'll create a visible sign with alternating colors
    sign_width = 500
    sign_height = 80
    
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.0, 0.0)  # Red finish sign
    glVertex3f(-sign_width/2, finish_zone_start_y, finish_zone_z + 10)
    glVertex3f(sign_width/2, finish_zone_start_y, finish_zone_z + 10)
    glVertex3f(sign_width/2, finish_zone_start_y, finish_zone_z + 10 + sign_height)
    glVertex3f(-sign_width/2, finish_zone_start_y, finish_zone_z + 10 + sign_height)
    glEnd()
    
    # Draw white text on the sign
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(5.0)
    glBegin(GL_POINTS)
    
    # Draw "FINISH" with points (simple but visible)
    points = [
        # F
        (-170, 20), (-170, 30), (-170, 40), (-170, 50),
        (-160, 50), (-150, 50), (-140, 50),
        (-160, 35), (-150, 35),
        
        # I
        (-120, 20), (-120, 30), (-120, 40), (-120, 50),
        
        # N
        (-90, 20), (-90, 30), (-90, 40), (-90, 50),
        (-80, 40), (-70, 30),
        (-60, 20), (-60, 30), (-60, 40), (-60, 50),
        
        # I
        (-30, 20), (-30, 30), (-30, 40), (-30, 50),
        
        # S
        (0, 50), (10, 50), (20, 50),
        (0, 35), (10, 35), (20, 35),
        (0, 20), (10, 20), (20, 20),
        (0, 35), (0, 50),
        (20, 20), (20, 35),
        
        # H
        (40, 20), (40, 30), (40, 40), (40, 50),
        (50, 35), (60, 35),
        (70, 20), (70, 30), (70, 40), (70, 50),
    ]
    
    for px, py in points:
        glVertex3f(px, finish_zone_start_y + 0.1, finish_zone_z + 10 + py)
    
    glEnd()
    
    glDisable(GL_POLYGON_OFFSET_FILL)

    # Re-enable lighting if it was on before
    if lighting_enabled:
        glEnable(GL_LIGHTING)

def draw_giant_doll():
    """Draw the giant doll character."""
    global DOLL_CURRENT_ROTATION
    
    glPushMatrix()
    glTranslatef(DOLL_POSITION[0], DOLL_POSITION[1], DOLL_POSITION[2])
    glRotatef(DOLL_CURRENT_ROTATION, 0, 0, 1)  # Rotate based on game state
    
    # Define doll proportions
    head_size = DOLL_BASE_HEIGHT * 0.25
    torso_h = DOLL_BASE_HEIGHT * 0.30
    frock_h = DOLL_BASE_HEIGHT * 0.20
    leg_h = DOLL_BASE_HEIGHT * 0.30
    arm_l = DOLL_BASE_HEIGHT * 0.25
    
    torso_w = DOLL_WIDTH * 1.0
    frock_w = DOLL_WIDTH * 1.5
    limb_w = DOLL_WIDTH * 0.2
    
    current_z = 0  # Start at ground level
    
    # Draw legs (white cubes)
    leg_center_z = current_z + leg_h / 2
    leg_offset_x = torso_w * 0.25
    
    glColor3f(0.95, 0.95, 0.95)
    glPushMatrix()
    glTranslatef(-leg_offset_x, -DOLL_DEPTH * 0.1, leg_center_z)
    glScalef(limb_w, limb_w, leg_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glColor3f(0.95, 0.95, 0.95)
    glPushMatrix()
    glTranslatef(leg_offset_x, -DOLL_DEPTH * 0.1, leg_center_z)
    glScalef(limb_w, limb_w, leg_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    current_z += leg_h
    
    # Draw frock/dress (orange-red cube, wider) - Squid Game doll colors
    frock_center_z = current_z + frock_h / 2
    
    glColor3f(0.95, 0.35, 0.15)  # Orange-red
    glPushMatrix()
    glTranslatef(0, -DOLL_DEPTH * 0.1, frock_center_z)
    glScalef(frock_w, DOLL_DEPTH * 0.8, frock_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    current_z += frock_h
    
    # Draw torso (orange-red cube)
    torso_center_z = current_z + torso_h / 2
    
    glColor3f(0.95, 0.35, 0.15)  # Orange-red
    glPushMatrix()
    glTranslatef(0, -DOLL_DEPTH * 0.1, torso_center_z)
    glScalef(torso_w, DOLL_DEPTH * 0.8, torso_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw arms (skin-colored cubes)
    arm_attach_z = torso_center_z + torso_h * 0.3
    arm_offset_x = torso_w / 2 + limb_w / 2
    
    glColor3f(0.95, 0.80, 0.72)
    glPushMatrix()
    glTranslatef(-arm_offset_x, -DOLL_DEPTH * 0.1, arm_attach_z)
    glRotatef(20, 0, 0, 1)
    glRotatef(-15, 1, 0, 0)
    glScalef(limb_w, limb_w, arm_l)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(arm_offset_x, -DOLL_DEPTH * 0.1, arm_attach_z)
    glRotatef(-20, 0, 0, 1)
    glRotatef(-15, 1, 0, 0)
    glScalef(limb_w, limb_w, arm_l)
    glutSolidCube(1.0)
    glPopMatrix()
    
    current_z += torso_h
    
    # Draw head (skin sphere + black hair)
    head_center_z = current_z + head_size / 2
    
    # Face/skin
    glColor3f(0.95, 0.80, 0.72)
    glPushMatrix()
    glTranslatef(0, 0, head_center_z)
    glutSolidSphere(head_size / 2, 16, 12)
    glPopMatrix()
    
    # Hair/cap - black like in Squid Game
    glColor3f(0.05, 0.05, 0.05)  # Black
    glPushMatrix()
    glTranslatef(0, 0, head_center_z + head_size * 0.1)
    glScalef(1.0, 1.0, 0.8)
    glutSolidSphere(head_size * 0.52, 12, 8)
    glPopMatrix()
    
    glPopMatrix()
    
    # Draw light above doll based on game state
    light_size = DOLL_BASE_HEIGHT * 0.1
    light_height = DOLL_BASE_HEIGHT + head_size * 2
    
    glPushMatrix()
    glTranslatef(DOLL_POSITION[0], DOLL_POSITION[1], light_height)
    
    if GAME_STATE == "red":
        glColor3f(1.0, 0.0, 0.0)  # Red light
    elif GAME_STATE == "yellow":
        glColor3f(1.0, 0.8, 0.0)  # Yellow light
    else:
        glColor3f(0.0, 1.0, 0.0)  # Green light
        
    glutSolidSphere(light_size, 16, 12)
    
    # Light glow effect
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    
    if GAME_STATE == "red":
        glColor4f(1.0, 0.0, 0.0, 0.3)  # Red glow
    elif GAME_STATE == "yellow":
        glColor4f(1.0, 0.8, 0.0, 0.3)  # Yellow glow
    else:
        glColor4f(0.0, 1.0, 0.0, 0.3)  # Green glow
        
    glutSolidSphere(light_size * 1.5, 12, 8)
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    
    glPopMatrix()

def draw_player():
    """Draw the player character."""
    # Check if player was caught or reached finish
    if player_was_caught:
        draw_player_caught()
        return
        
    if player_reached_finish:
        draw_player_victory()
        return
    
    glPushMatrix()
    glTranslatef(player_position[0], player_position[1], player_position[2])
    glRotatef(player_direction - 90, 0, 0, 1)
    
    # Add particle effect when speed boost is active
    if player_speed_boost_active:
        draw_speed_effect()
    
    # Player proportions
    body_w = player_width * 0.8
    body_h = player_height * 0.6
    body_d = body_w * 0.7
    head_s = player_width * 0.7
    limb_w = player_width * 0.15
    leg_h = player_height * 0.4
    arm_l = player_height * 0.35
    
    # Draw legs
    leg_center_z = leg_h / 2
    leg_offset_x = body_w * 0.3
    
    glColor3f(0.0, 0.35, 0.25)  # Dark green
    glPushMatrix()
    glTranslatef(-leg_offset_x, 0, leg_center_z)
    glScalef(limb_w, limb_w, leg_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(leg_offset_x, 0, leg_center_z)
    glScalef(limb_w, limb_w, leg_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw body
    body_center_z = leg_h + body_h / 2
    
    glColor3f(0.0, 0.45, 0.3)  # Green
    glPushMatrix()
    glTranslatef(0, 0, body_center_z)
    glScalef(body_w, body_d, body_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw head
    head_center_z = leg_h + body_h + head_s / 2
    
    glColor3f(0.9, 0.7, 0.6)  # Skin tone
    glPushMatrix()
    glTranslatef(0, 0, head_center_z)
    glScalef(head_s, head_s, head_s)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw arms
    arm_attach_z = body_center_z + body_h * 0.3
    arm_offset_x = body_w / 2 + limb_w / 2
    
    glColor3f(0.0, 0.35, 0.25)  # Dark green
    glPushMatrix()
    glTranslatef(-arm_offset_x, 0, arm_attach_z)
    glRotatef(15, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glScalef(limb_w, limb_w, arm_l)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(arm_offset_x, 0, arm_attach_z)
    glRotatef(-15, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glScalef(limb_w, limb_w, arm_l)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()

def draw_speed_effect():
    """Draw particle effect when speed boost is active."""
    glDisable(GL_LIGHTING)
    
    # Draw trail particles
    glColor4f(0.0, 0.8, 1.0, 0.7)  # Cyan glow
    
    # Simple particle trail
    for i in range(10):
        offset = -5.0 - i * 3.0  # Trail behind player
        alpha = 0.7 * (1.0 - i / 10.0)  # Fade out
        
        glPushMatrix()
        glTranslatef(0, offset, 10 + i * 2.0)
        glColor4f(0.0, 0.8, 1.0, alpha)
        glutSolidSphere(3.0 - i * 0.2, 8, 8)
        glPopMatrix()
    
    glEnable(GL_LIGHTING)

def draw_player_caught():
    """Draw player in caught/dead state."""
    glPushMatrix()
    glTranslatef(player_position[0], player_position[1], player_position[2])
    
    # Player lying on the ground
    glRotatef(player_direction, 0, 0, 1)
    glRotatef(90, 1, 0, 0)  # Rotate to lie flat
    
    # Same dimensions as normal player but lying down
    body_w = player_width * 0.8
    body_h = player_height * 0.6
    body_d = body_w * 0.7
    head_s = player_width * 0.7
    limb_w = player_width * 0.15
    leg_h = player_height * 0.4
    arm_l = player_height * 0.35
    
    # Body - darkened color to indicate "dead"
    glColor3f(0.0, 0.2, 0.15)  # Darker green
    glPushMatrix()
    glTranslatef(0, 0, 0)
    glScalef(body_w, body_d, body_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Head
    glColor3f(0.7, 0.5, 0.4)  # Darker skin tone
    glPushMatrix()
    glTranslatef(0, 0, body_h)
    glScalef(head_s, head_s, head_s)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Arms (stretched out)
    glColor3f(0.0, 0.2, 0.15)  # Darker green
    glPushMatrix()
    glTranslatef(-body_w, 0, 0)
    glScalef(arm_l, limb_w, limb_w)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(body_w, 0, 0)
    glScalef(arm_l, limb_w, limb_w)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Legs (stretched out)
    glPushMatrix()
    glTranslatef(0, 0, -body_h)
    glScalef(limb_w, limb_w, leg_h * 1.5)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw blood effect
    glDisable(GL_LIGHTING)
    glColor4f(0.9, 0.0, 0.0, 0.7)  # Red with alpha
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, -2.0)  # Center slightly below player
    
    # Create blood splatter shape
    radius = 30.0
    for i in range(13):
        angle = i * (2.0 * math.pi / 12)
        variation = random.uniform(0.7, 1.3)
        x = math.cos(angle) * radius * variation
        y = math.sin(angle) * radius * variation
        glVertex3f(x, y, -2.0)
    
    # Close the fan
    angle = 0.0
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    glVertex3f(x, y, -2.0)
    
    glEnd()
    glEnable(GL_LIGHTING)
    
    glPopMatrix()

def draw_player_victory():
    """Draw player in victory pose."""
    glPushMatrix()
    glTranslatef(player_position[0], player_position[1], player_position[2])
    glRotatef(player_direction - 90, 0, 0, 1)
    
    # Player proportions
    body_w = player_width * 0.8
    body_h = player_height * 0.6
    body_d = body_w * 0.7
    head_s = player_width * 0.7
    limb_w = player_width * 0.15
    leg_h = player_height * 0.4
    arm_l = player_height * 0.35
    
    # Draw legs
    leg_center_z = leg_h / 2
    leg_offset_x = body_w * 0.3
    
    glColor3f(0.0, 0.35, 0.25)  # Dark green
    glPushMatrix()
    glTranslatef(-leg_offset_x, 0, leg_center_z)
    glScalef(limb_w, limb_w, leg_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(leg_offset_x, 0, leg_center_z)
    glScalef(limb_w, limb_w, leg_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw body
    body_center_z = leg_h + body_h / 2
    
    glColor3f(0.0, 0.45, 0.3)  # Green
    glPushMatrix()
    glTranslatef(0, 0, body_center_z)
    glScalef(body_w, body_d, body_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw head
    head_center_z = leg_h + body_h + head_s / 2
    
    glColor3f(0.9, 0.7, 0.6)  # Skin tone
    glPushMatrix()
    glTranslatef(0, 0, head_center_z)
    glScalef(head_s, head_s, head_s)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw arms - raised for victory
    arm_attach_z = body_center_z + body_h * 0.3
    arm_offset_x = body_w / 2 + limb_w / 2
    
    glColor3f(0.0, 0.35, 0.25)  # Dark green
    
    # Left arm raised
    glPushMatrix()
    glTranslatef(-arm_offset_x, 0, arm_attach_z)
    glRotatef(15, 0, 0, 1)
    glRotatef(-120, 1, 0, 0)  # Raised up
    glScalef(limb_w, limb_w, arm_l)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Right arm raised
    glPushMatrix()
    glTranslatef(arm_offset_x, 0, arm_attach_z)
    glRotatef(-15, 0, 0, 1)
    glRotatef(-120, 1, 0, 0)  # Raised up
    glScalef(limb_w, limb_w, arm_l)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw victory particles
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    
    current_time = time.time()
    
    for i in range(20):
        angle = current_time * 2.0 + i * (math.pi / 10)
        height = math.sin(current_time * 3.0 + i) * 20.0 + 80.0
        x = math.cos(angle) * 30.0
        y = math.sin(angle) * 30.0
        z = height
        
        size = random.uniform(3.0, 7.0)
        
        # Cycle through festive colors
        color_cycle = (i % 3)
        if color_cycle == 0:
            glColor4f(1.0, 0.3, 0.3, 0.7)  # Red
        elif color_cycle == 1:
            glColor4f(0.3, 1.0, 0.3, 0.7)  # Green
        else:
            glColor4f(0.3, 0.3, 1.0, 0.7)  # Blue
            
        glPushMatrix()
        glTranslatef(x, y, z)
        glutSolidSphere(size, 8, 8)
        glPopMatrix()
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    
    glPopMatrix()

def draw_enemy(enemy):
    """Draw an enemy character."""
    if not enemy['alive']:
        draw_enemy_dead(enemy)
        return
    
    glPushMatrix()
    glTranslatef(enemy['position'][0], enemy['position'][1], enemy['position'][2])
    glRotatef(enemy['direction'] - 90, 0, 0, 1)
    
    # Apply scale factor for black enemies
    scale = enemy.get('scale', 1.0)
    glScalef(scale, scale, scale)
    
    # Enemy proportions
    body_w = ENEMY_WIDTH * 0.8
    body_h = ENEMY_HEIGHT * 0.6
    body_d = body_w * 0.7
    head_s = ENEMY_WIDTH * 0.7
    limb_w = ENEMY_WIDTH * 0.15
    leg_h = ENEMY_HEIGHT * 0.4
    arm_l = ENEMY_HEIGHT * 0.35
    
    # Draw a glowing outline around enemy to make it stand out against checkered background
    glDisable(GL_LIGHTING)
    if enemy['type'] == 'red':
        glColor4f(1.0, 0.3, 0.3, 0.7)  # Red glow
    elif enemy['type'] == 'blue':
        glColor4f(0.3, 0.3, 1.0, 0.7)  # Blue glow
    else:  # black
        glColor4f(0.5, 0.5, 0.5, 0.7)  # Gray glow
        
    glPushMatrix()
    glScalef(1.15, 1.15, 1.15)  # Slightly larger than the enemy
    glutSolidSphere(body_h * 1.5, 16, 12)
    glPopMatrix()
    glEnable(GL_LIGHTING)
    
    # Draw legs
    leg_center_z = leg_h / 2
    leg_offset_x = body_w * 0.3
    
    # Adjust leg color based on enemy type
    if enemy['type'] == 'red':
        leg_color = (0.9, 0.1, 0.1)  # Brighter red
    elif enemy['type'] == 'blue':
        leg_color = (0.1, 0.1, 0.9)  # Brighter blue
    else:  # black
        leg_color = (0.0, 0.0, 0.0)  # Pure black
        
    glColor3fv(leg_color)
    glPushMatrix()
    glTranslatef(-leg_offset_x, 0, leg_center_z)
    glScalef(limb_w, limb_w, leg_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(leg_offset_x, 0, leg_center_z)
    glScalef(limb_w, limb_w, leg_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw body
    body_center_z = leg_h + body_h / 2
    
    # Use brighter colors for better visibility
    if enemy['type'] == 'red':
        body_color = (1.0, 0.2, 0.2)  # Brighter red
    elif enemy['type'] == 'blue':
        body_color = (0.2, 0.2, 1.0)  # Brighter blue
    else:  # black
        body_color = (0.0, 0.0, 0.0)  # Pure black
    
    glColor3fv(body_color)
    glPushMatrix()
    glTranslatef(0, 0, body_center_z)
    glScalef(body_w, body_d, body_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw head
    head_center_z = leg_h + body_h + head_s / 2
    
    glColor3f(0.95, 0.85, 0.7)  # Brighter skin tone
    glPushMatrix()
    glTranslatef(0, 0, head_center_z)
    glScalef(head_s, head_s, head_s)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw arms
    arm_attach_z = body_center_z + body_h * 0.3
    arm_offset_x = body_w / 2 + limb_w / 2
    
    glColor3fv(leg_color)  # Match legs
    glPushMatrix()
    glTranslatef(-arm_offset_x, 0, arm_attach_z)
    glRotatef(15, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glScalef(limb_w, limb_w, arm_l)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(arm_offset_x, 0, arm_attach_z)
    glRotatef(-15, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glScalef(limb_w, limb_w, arm_l)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Draw health indicator above enemy based on health
    if enemy['type'] != 'red':  # Only show for enemies with >1 health
        glPushMatrix()
        glTranslatef(0, 0, head_center_z + head_s + 15)  # Positioned higher
        
        glDisable(GL_LIGHTING)
        
        # Draw health bar background
        health_width = 30.0  # Wider
        health_height = 5.0  # Taller
        
        glColor3f(0.3, 0.3, 0.3)  # Dark gray background
        glBegin(GL_QUADS)
        glVertex3f(-health_width/2, -health_height/2, 0)
        glVertex3f(health_width/2, -health_height/2, 0)
        glVertex3f(health_width/2, health_height/2, 0)
        glVertex3f(-health_width/2, health_height/2, 0)
        glEnd()
        
        # Draw current health
        max_health = 5 if enemy['type'] == 'black' else 2
        current_health = enemy['health']
        health_percent = current_health / max_health
        filled_width = health_width * health_percent
        
        # Health color from red to green
        r = 1.0 - health_percent
        g = health_percent
        b = 0.0
        
        glColor3f(r, g, b)
        glBegin(GL_QUADS)
        glVertex3f(-health_width/2, -health_height/2, 0.1)
        glVertex3f(-health_width/2 + filled_width, -health_height/2, 0.1)
        glVertex3f(-health_width/2 + filled_width, health_height/2, 0.1)
        glVertex3f(-health_width/2, health_height/2, 0.1)
        glEnd()
        
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
    
    glPopMatrix()

def draw_enemy_dead(enemy):
    """Draw an enemy in dead/eliminated state."""
    glPushMatrix()
    glTranslatef(enemy['position'][0], enemy['position'][1], enemy['position'][2])
    
    # Enemy lying on the ground
    glRotatef(enemy['direction'], 0, 0, 1)
    glRotatef(90, 1, 0, 0)  # Rotate to lie flat
    
    # Apply scale factor for black enemies
    scale = enemy.get('scale', 1.0)
    glScalef(scale, scale, scale)
    
    # Same dimensions as normal enemy but lying down
    body_w = ENEMY_WIDTH * 0.8
    body_h = ENEMY_HEIGHT * 0.6
    body_d = body_w * 0.7
    head_s = ENEMY_WIDTH * 0.7
    limb_w = ENEMY_WIDTH * 0.15
    leg_h = ENEMY_HEIGHT * 0.4
    arm_l = ENEMY_HEIGHT * 0.35
    
    # Darken color for dead enemy
    r, g, b = enemy['color']
    dead_color = (r * 0.5, g * 0.5, b * 0.5)
    
    # Body
    glColor3fv(dead_color)
    glPushMatrix()
    glTranslatef(0, 0, 0)
    glScalef(body_w, body_d, body_h)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Head
    glColor3f(0.6, 0.4, 0.3)  # Darker skin tone
    glPushMatrix()
    glTranslatef(0, 0, body_h)
    glScalef(head_s, head_s, head_s)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Arms (stretched out)
    # Adjust leg color based on enemy type
    if enemy['type'] == 'red':
        limb_color = (0.35, 0.05, 0.05)  # Dark red
    elif enemy['type'] == 'blue':
        limb_color = (0.05, 0.05, 0.35)  # Dark blue
    else:  # black
        limb_color = (0.02, 0.02, 0.02)  # Dark black
    
    glColor3fv(limb_color)
    glPushMatrix()
    glTranslatef(-body_w, 0, 0)
    glScalef(arm_l, limb_w, limb_w)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(body_w, 0, 0)
    glScalef(arm_l, limb_w, limb_w)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Legs (stretched out)
    glPushMatrix()
    glTranslatef(0, 0, -body_h)
    glScalef(limb_w, limb_w, leg_h * 1.5)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()

def draw_bullet(bullet):
    """Draw a bullet/projectile."""
    glPushMatrix()
    glTranslatef(bullet['position'][0], bullet['position'][1], bullet['position'][2])
    
    # Larger orange bullet for better visibility
    glColor3f(1.0, 0.5, 0.0)  # Orange
    glutSolidSphere(bullet['size'], 10, 8)  # Use bullet's size property
    
    # Add trail effect
    glDisable(GL_LIGHTING)
    
    angle_rad = math.radians(bullet['direction'])
    dx = -math.cos(angle_rad)
    dy = -math.sin(angle_rad)
    
    glBegin(GL_TRIANGLE_STRIP)
    
    # Create a longer trail behind the bullet
    trail_length = 50.0  # Increased from 30.0
    trail_width = 5.0   # Increased from 3.0
    
    # Vector perpendicular to bullet direction
    nx = -dy * trail_width
    ny = dx * trail_width
    
    # Trail start point (back of bullet)
    x1 = bullet['position'][0] + dx * bullet['size']
    y1 = bullet['position'][1] + dy * bullet['size']
    z1 = bullet['position'][2]
    
    # Trail end point
    x2 = x1 + dx * trail_length
    y2 = y1 + dy * trail_length
    z2 = z1
    
    glColor4f(1.0, 0.5, 0.0, 0.8)  # Start of trail (more opaque)
    glVertex3f(x1 + nx, y1 + ny, z1)
    glVertex3f(x1 - nx, y1 - ny, z1)
    
    glColor4f(1.0, 0.3, 0.0, 0.0)  # End of trail (transparent)
    glVertex3f(x2 + nx, y2 + ny, z2)
    glVertex3f(x2 - nx, y2 - ny, z2)
    
    glEnd()
    
    # Draw a small glowing effect for better visibility
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    
    glColor4f(1.0, 0.7, 0.3, 0.5)  # Orange glow
    glutSolidSphere(bullet['size'] * 1.5, 8, 8)
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    
    glPopMatrix()

def draw_powerup(powerup):
    """Draw a power-up."""
    if not powerup['active']:
        return
        
    glPushMatrix()
    glTranslatef(powerup['position'][0], powerup['position'][1], powerup['position'][2])
    
    # Rotate powerup for spinning effect
    powerup['rotation'] += 1.0
    glRotatef(powerup['rotation'], 0, 0, 1)
    
    # Draw power-up based on type
    if powerup['type'] == 'speed':
        glColor3f(0.0, 0.0, 0.0)  # Black color for visibility
        
        # Draw larger lightning bolt shape for speed power-up
        glDisable(GL_LIGHTING)
        
        # Scale up the size by 1.8x for better visibility
        scale_factor = 1.8
        
        glBegin(GL_TRIANGLES)
        # Lightning bolt shape
        glVertex3f(0, 18 * scale_factor, 0)
        glVertex3f(-9 * scale_factor, 0, 0)
        glVertex3f(0, 0, 0)
        
        glVertex3f(0, 0, 0)
        glVertex3f(9 * scale_factor, -18 * scale_factor, 0)
        glVertex3f(0, -18 * scale_factor, 0)
        
        glVertex3f(0, 0, 0)
        glVertex3f(-9 * scale_factor, 0, 0)
        glVertex3f(0, -18 * scale_factor, 0)
        
        glVertex3f(0, 18 * scale_factor, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(9 * scale_factor, 0, 0)
        glEnd()
        
        # Draw glowing effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        glColor4f(0.4, 0.4, 0.4, 0.6)  # Gray glow
        glutSolidSphere(25, 16, 12)  # Larger sphere
        
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
    
    glPopMatrix()

def draw_progress_bar():
    """Draw progress bar showing distance to finish line."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Calculate progress
    start_y = -PLAY_AREA_LENGTH / 2
    end_y = PLAY_AREA_LENGTH / 2
    total_distance = end_y - start_y
    current_distance = player_position[1] - start_y
    progress = current_distance / total_distance
    
    # Draw progress bar background with semi-transparent dark rectangle
    bar_width = 350
    bar_height = 30
    bar_x = WINDOW_WIDTH - bar_width - 20
    bar_y = WINDOW_HEIGHT - 50
    
    # Draw semi-transparent background
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(bar_x - 10, bar_y - 5)
    glVertex2f(bar_x + bar_width + 10, bar_y - 5)
    glVertex2f(bar_x + bar_width + 10, bar_y + bar_height + 5)
    glVertex2f(bar_x - 10, bar_y + bar_height + 5)
    glEnd()
    glDisable(GL_BLEND)
    
    # Draw progress bar frame
    glColor3f(0.5, 0.5, 0.5)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Draw progress
    filled_width = bar_width * progress
    
    if progress < 0.5:
        # Red to yellow gradient
        r = 1.0
        g = progress * 2.0
        b = 0.0
    else:
        # Yellow to green gradient
        r = 1.0 - (progress - 0.5) * 2.0
        g = 1.0
        b = 0.0
    
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + filled_width, bar_y)
    glVertex2f(bar_x + filled_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()
    
    # Draw percentage text
    progress_text = f"Progress: {int(progress * 100)}%"
    glColor3f(1.0, 1.0, 1.0)
    draw_text(bar_x + 10, bar_y + bar_height/2 - 5, progress_text, GLUT_BITMAP_HELVETICA_18)
    
    # Draw finish line label
    finish_label = "FINISH"
    glColor3f(1.0, 1.0, 1.0)
    draw_text(bar_x + bar_width - 60, bar_y + bar_height/2 - 5, finish_label, GLUT_BITMAP_HELVETICA_18)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glMatrixMode(GL_MODELVIEW)

def draw_score():
    """Draw player's score information."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Draw score background
    score_width = 220
    score_height = 100
    score_x = 20
    score_y = WINDOW_HEIGHT - 70
    
    # Semi-transparent dark background
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(score_x, score_y - score_height)
    glVertex2f(score_x + score_width, score_y - score_height)
    glVertex2f(score_x + score_width, score_y)
    glVertex2f(score_x, score_y)
    glEnd()
    glDisable(GL_BLEND)
    
    # Draw score text
    title_text = "SCORE"
    draw_text(score_x + 10, score_y - 20, title_text, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 0.0))
    draw_text(score_x + 10, score_y - 45, f"Score: {player_score}", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    draw_text(score_x + 10, score_y - 70, f"Time: {time_survived:.1f}s", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    draw_text(score_x + 10, score_y - 95, f"Kills: {enemies_killed}", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glMatrixMode(GL_MODELVIEW)

def draw_start_screen():
    """Draw game start screen."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Draw semi-transparent background
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()
    
    # Draw title
    title_color = (0.9, 0.1, 0.2)  # Red like in Squid Game
    draw_centered_text(GAME_TITLE, WINDOW_HEIGHT - 200, GLUT_BITMAP_HELVETICA_18, title_color)
    
    # Draw start button
    button_width = 200
    button_height = 50
    button_x = (WINDOW_WIDTH - button_width) / 2
    button_y = (WINDOW_HEIGHT - button_height) / 2
    
    glColor3f(0.9, 0.1, 0.2)  # Red for button
    glBegin(GL_QUADS)
    glVertex2f(button_x, button_y)
    glVertex2f(button_x + button_width, button_y)
    glVertex2f(button_x + button_width, button_y + button_height)
    glVertex2f(button_x, button_y + button_height)
    glEnd()
    
    # Draw button text
    glColor3f(1.0, 1.0, 1.0)
    draw_centered_text("START GAME", button_y + 15, GLUT_BITMAP_HELVETICA_18)
    
    # Draw instructions
    glColor3f(1.0, 1.0, 1.0)
    
    instructions = [
        "Controls:",
        "WASD - Movement",
        "Arrow Keys - Camera",
        "Z/X - Zoom",
        "Space - Shoot",
        "R - Restart",
        "ESC - Exit"
    ]
    
    y_pos = button_y - 100
    for instruction in instructions:
        draw_centered_text(instruction, y_pos, GLUT_BITMAP_9_BY_15)
        y_pos -= 25
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glMatrixMode(GL_MODELVIEW)

# --- Game Logic Functions ---
def update_state():
    """Update game state based on user input and timing."""
    global player_position, player_direction, last_update_time, fps_last_time, frame_count, fps
    global target_player_position, target_player_direction, camera_distance, camera_yaw, camera_pitch
    global target_camera_yaw, target_camera_pitch, STATE_TIMER, GAME_STATE, NEXT_STATE_CHANGE
    global DOLL_CURRENT_ROTATION, DOLL_TARGET_ROTATION, bullet_cooldown, player_is_moving
    global player_was_caught, player_reached_finish, last_positions, player_velocity
    global GAME_PHASE, CURRENT_GAME_TIME, player_score, time_survived, powerup_spawn_timer
    global player_speed_boost_active, player_speed_boost_timer, player_move_speed
    global STATE_CHANGE_INTERVAL_MIN, STATE_CHANGE_INTERVAL_MAX
    global notification_text, notification_timer
    
    current_time = time.time()
    delta_time = current_time - last_update_time
    delta_time = min(delta_time, 0.1)  # Cap delta time to prevent large jumps
    last_update_time = current_time
    
    # Update FPS counter
    frame_count += 1
    if current_time - fps_last_time >= 1.0:
        fps = frame_count
        frame_count = 0
        fps_last_time = current_time
    
    # Frame limiting if enabled
    if USE_FRAME_LIMITING:
        target_frame_time = 1.0 / TARGET_FPS
        sleep_time = target_frame_time - delta_time
        
        if sleep_time > 0.001:
            time.sleep(sleep_time)
            current_time = time.time()
            delta_time = current_time - (last_update_time - delta_time + target_frame_time)
            delta_time = min(delta_time, 0.1)
            last_update_time = current_time
    
    # Update notification system
    if notification_timer > 0:
        notification_timer -= delta_time
    
    # Handle start screen
    if GAME_STATE == "start":
        # Check for mouse click on start button
        if b' ' in keys_pressed:  # Use space to start for simplicity
            start_game()
            
        glutPostRedisplay()
        return
    
    # Calculate survival time
    time_survived = current_time - GAME_START_TIME
    
    # Update game difficulty based on phase
    if time_survived > GAME_PHASE * PHASE_DURATION:
        GAME_PHASE += 1
        # Adjust difficulty parameters
        STATE_CHANGE_INTERVAL_MIN = max(1.0, STATE_CHANGE_INTERVAL_MIN - 0.4)
        STATE_CHANGE_INTERVAL_MAX = max(3.0, STATE_CHANGE_INTERVAL_MAX - 0.6)
        show_notification(f"Phase {GAME_PHASE}! Difficulty increased!")
        print(f"Increasing difficulty to phase {GAME_PHASE}!")
        print(f"New timing: {STATE_CHANGE_INTERVAL_MIN:.1f}s - {STATE_CHANGE_INTERVAL_MAX:.1f}s")
    
    # Skip updates if player was caught or won
    if player_was_caught or player_reached_finish:
        glutPostRedisplay()
        return
    
    # Update game state timer
    STATE_TIMER += delta_time
    if STATE_TIMER >= NEXT_STATE_CHANGE:
        if GAME_STATE == "green":
            # First change to yellow warning
            GAME_STATE = "yellow"
            NEXT_STATE_CHANGE = 5.0  # Fixed 5-second yellow warning
            STATE_TIMER = 0
            show_notification("WARNING! Yellow light!")
        elif GAME_STATE == "yellow":
            # Then change to red
            GAME_STATE = "red"
            DOLL_TARGET_ROTATION = 0  # Face player
            NEXT_STATE_CHANGE = random.uniform(STATE_CHANGE_INTERVAL_MIN, STATE_CHANGE_INTERVAL_MAX)
            STATE_TIMER = 0
            show_notification("RED LIGHT! Stop moving!")
        else:
            # Change back to green
            GAME_STATE = "green"
            DOLL_TARGET_ROTATION = 180  # Face away
            NEXT_STATE_CHANGE = random.uniform(
                STATE_CHANGE_INTERVAL_MIN * (1.0 + 0.5 / GAME_PHASE),  # More green time early in game
                STATE_CHANGE_INTERVAL_MAX * (1.0 + 0.5 / GAME_PHASE)
            )
            STATE_TIMER = 0
            show_notification("GREEN LIGHT! Go!")
    
    # Smooth doll rotation
    rotation_diff = DOLL_TARGET_ROTATION - DOLL_CURRENT_ROTATION
    if abs(rotation_diff) > 0.5:
        rotation_step = DOLL_ROTATION_SPEED * delta_time
        if rotation_diff > 0:
            DOLL_CURRENT_ROTATION += min(rotation_step, rotation_diff)
        else:
            DOLL_CURRENT_ROTATION -= min(rotation_step, -rotation_diff)
    
    # Update camera based on input
    cam_rot_step = camera_rotation_speed * delta_time
    pitch_changed = False
    yaw_changed = False
    
    # Camera rotation - modified for head-tilting behavior
    if GLUT_KEY_LEFT in keys_pressed:
        target_camera_yaw += cam_rot_step
        yaw_changed = True
        
    if GLUT_KEY_RIGHT in keys_pressed:
        target_camera_yaw -= cam_rot_step
        yaw_changed = True
        
    if GLUT_KEY_UP in keys_pressed:
        target_camera_pitch += cam_rot_step
        pitch_changed = True
        
    if GLUT_KEY_DOWN in keys_pressed:
        target_camera_pitch -= cam_rot_step
        pitch_changed = True
    
    # Clamp camera pitch to prevent flipping
    target_camera_pitch = max(camera_pitch_min, min(camera_pitch_max, target_camera_pitch))
    
    # Calculate movement vectors based on camera orientation
    cam_yaw_rad = math.radians(camera_yaw)
    move_forward_x = math.cos(cam_yaw_rad)
    move_forward_y = math.sin(cam_yaw_rad)
    move_right_x = math.sin(cam_yaw_rad)
    move_right_y = -math.cos(cam_yaw_rad)
    
    # Initialize acceleration for this frame
    accel_x = 0.0
    accel_y = 0.0
    player_is_moving = False
    
    # Determine acceleration based on input
    if b'w' in keys_pressed:
        accel_x += move_forward_x * player_move_speed
        accel_y += move_forward_y * player_move_speed
        player_is_moving = True
        
    if b's' in keys_pressed:
        accel_x -= move_forward_x * player_move_speed
        accel_y -= move_forward_y * player_move_speed
        player_is_moving = True
        
    if b'a' in keys_pressed:
        accel_x -= move_right_x * player_move_speed
        accel_y -= move_right_y * player_move_speed
        player_is_moving = True
        
    if b'd' in keys_pressed:
        accel_x += move_right_x * player_move_speed
        accel_y += move_right_y * player_move_speed
        player_is_moving = True
    
    # Apply friction to current velocity
    player_velocity[0] *= player_friction
    player_velocity[1] *= player_friction
    
    # Apply acceleration to velocity
    if player_is_moving:
        player_velocity[0] += accel_x * delta_time
        player_velocity[1] += accel_y * delta_time
    
    # Apply velocity to position
    target_player_position[0] += player_velocity[0] * delta_time
    target_player_position[1] += player_velocity[1] * delta_time
    
    # Check movement during red light
    moving_during_red = (GAME_STATE == "red" and DOLL_CURRENT_ROTATION < 45 and 
                       (abs(player_velocity[0]) > 1.0 or abs(player_velocity[1]) > 1.0))
    
    if moving_during_red:
        player_was_caught = True
        print("You moved during red light! Game over.")
    
    # Boundary constraints
    half_play_w = PLAY_AREA_WIDTH / 2 - player_width / 2
    half_play_l = PLAY_AREA_LENGTH / 2 - player_width / 2
    
    target_player_position[0] = max(-half_play_w, min(half_play_w, target_player_position[0]))
    target_player_position[1] = max(-half_play_l, min(half_play_l, target_player_position[1]))
    
    # Update player direction if moving
    velocity_magnitude_sq = player_velocity[0]**2 + player_velocity[1]**2
    if velocity_magnitude_sq > 10.0:  # Only update direction if moving significantly
        target_player_direction = math.degrees(math.atan2(player_velocity[1], player_velocity[0]))
    
    # Camera zoom control
    zoom_changed = False
    zoom_speed = 350.0 * delta_time
    
    if b'z' in keys_pressed:
        camera_distance -= zoom_speed
        zoom_changed = True
        
    if b'x' in keys_pressed:
        camera_distance += zoom_speed
        zoom_changed = True
        
    camera_distance = max(camera_distance_min, min(camera_distance_max, camera_distance))
    
    # Debug output if enabled
    if print_debug:
        if pitch_changed:
            print(f"ARROW Key: Target Pitch -> {target_camera_pitch:.1f} | Current Distance: {camera_distance:.1f}")
            
        if yaw_changed:
            print(f"ARROW Key: Target Yaw -> {target_camera_yaw:.1f}")
            
        if zoom_changed:
            print(f"Z/X Key: Distance -> {camera_distance:.1f} | Current Target Pitch: {target_camera_pitch:.1f}")
    
    # Apply smooth player movement
    player_lerp = min(1.0, PLAYER_SMOOTHING * delta_time)
    player_position[0] += (target_player_position[0] - player_position[0]) * player_lerp
    player_position[1] += (target_player_position[1] - player_position[1]) * player_lerp
    
    # Apply smooth rotation
    player_angle_diff = (target_player_direction - player_direction + 180) % 360 - 180
    player_direction = (player_direction + player_angle_diff * player_lerp) % 360
    
    # Apply smooth camera movement
    cam_lerp = min(1.0, CAMERA_SMOOTHING * delta_time)
    
    yaw_diff = (target_camera_yaw - camera_yaw + 180) % 360 - 180
    if abs(yaw_diff) > 180:
        yaw_diff = (target_camera_yaw - camera_yaw)
    camera_yaw = (camera_yaw + yaw_diff * cam_lerp) % 360
    
    pitch_diff = target_camera_pitch - camera_pitch
    camera_pitch += pitch_diff * cam_lerp
    
    # Update weapon cooldown
    if bullet_cooldown > 0:
        bullet_cooldown -= delta_time
    
    # Check for weapon firing
    if b' ' in keys_pressed and bullet_cooldown <= 0:
        fire_weapon()
        bullet_cooldown = BULLET_COOLDOWN_TIME
    
    # Update power-up effects
    if player_speed_boost_active:
        player_speed_boost_timer -= delta_time
        if player_speed_boost_timer <= 0:
            player_speed_boost_active = False
            player_move_speed = player_base_speed
            print("Speed boost ended!")
    
    # Update powerup spawn timer
    powerup_spawn_timer -= delta_time
    if powerup_spawn_timer <= 0:
        spawn_powerup()
        powerup_spawn_timer = POWERUP_SPAWN_INTERVAL
    
    # Update bullets
    update_bullets(delta_time)
    
    # Update enemies
    update_enemies(delta_time)
    
    # Update powerups
    update_powerups(delta_time)
    
    # Check for collisions
    check_collisions()
    
    # Check for win condition (reaching finish line)
    if player_position[1] >= PLAY_AREA_LENGTH / 2:
        player_reached_finish = True
        # Calculate final score
        player_score += 10000  # Win bonus
        player_score += int(1000 / (time_survived / 60.0))  # Time bonus (better for faster completion)
        print(f"Congratulations! You reached the finish line! Final score: {player_score}")
    
    # Store last positions for movement detection
    last_positions['player'] = list(player_position)
    
    for enemy in enemies:
        if 'position' in enemy:
            enemy['last_position'] = list(enemy['position'])
    
    glutPostRedisplay()

def start_game():
    """Start the game from the starting screen."""
    global GAME_STATE, player_position, target_player_position, GAME_START_TIME
    global player_score, time_survived, enemies_killed, player_move_speed
    
    # Reset player
    player_position = list(player_start_pos)
    target_player_position = list(player_start_pos)
    
    # Reset game state
    GAME_STATE = "green"
    STATE_TIMER = 0
    NEXT_STATE_CHANGE = random.uniform(STATE_CHANGE_INTERVAL_MIN * 1.5, STATE_CHANGE_INTERVAL_MAX * 1.5)  # Extra time for first green light
    GAME_START_TIME = time.time()
    
    # Reset scoring
    player_score = 0
    time_survived = 0.0
    enemies_killed = 0
    
    # Reset speed boost
    player_speed_boost_active = False
    player_move_speed = player_base_speed
    
    # Initialize enemies
    setup_enemies()
    
    # Initialize powerups
    setup_powerups()
    powerup_spawn_timer = POWERUP_SPAWN_INTERVAL
    
    print("Game started!")

# Add notification system
notification_text = ""
notification_timer = 0
NOTIFICATION_DURATION = 3.0  # How long notifications stay on screen

def show_notification(text):
    """Display a notification message on screen."""
    global notification_text, notification_timer
    notification_text = text
    notification_timer = NOTIFICATION_DURATION

def fire_weapon():
    """Create a new bullet fired from the player."""
    global bullets
    
    # Calculate bullet direction based on player orientation
    angle_rad = math.radians(player_direction)
    
    # Starting position (slightly in front of player)
    offset = 30.0
    start_x = player_position[0] + offset * math.cos(angle_rad)
    start_y = player_position[1] + offset * math.sin(angle_rad)
    start_z = player_position[2] + player_height * 0.5
    
    # Create bullet object
    bullet = {
        'position': [start_x, start_y, start_z],
        'direction': player_direction,
        'lifetime': 3.0,  # Bullet disappears after this many seconds
        'size': BULLET_SIZE,  # Store bullet size with the bullet
        'last_position': [start_x, start_y, start_z]  # Track previous position for line collision
    }
    
    bullets.append(bullet)
    show_notification("Bullet fired!")

def update_bullets(delta_time):
    """Move bullets and handle their lifetime."""
    global bullets
    
    # Process each bullet
    for bullet in bullets[:]:
        # Store last position before moving
        bullet['last_position'] = list(bullet['position'])
        
        # Move bullet
        angle_rad = math.radians(bullet['direction'])
        bullet['position'][0] += BULLET_SPEED * math.cos(angle_rad) * delta_time
        bullet['position'][1] += BULLET_SPEED * math.sin(angle_rad) * delta_time
        
        # Update lifetime
        bullet['lifetime'] -= delta_time
        
        # Remove expired bullets
        if bullet['lifetime'] <= 0:
            bullets.remove(bullet)
            continue
        
        # Check if out of bounds
        half_play_w = PLAY_AREA_WIDTH / 2 + 100
        half_play_l = PLAY_AREA_LENGTH / 2 + 100
        
        if (abs(bullet['position'][0]) > half_play_w or 
            abs(bullet['position'][1]) > half_play_l):
            bullets.remove(bullet)

def update_enemies(delta_time):
    """Update enemy positions and check for red light violations."""
    global enemies, player_position
    
    for enemy in enemies:
        if not enemy['alive']:
            continue
            
        # Determine speed based on game state
        enemy_speed = enemy['speed']
        if GAME_STATE == "yellow":
            # During yellow light, enemies move at just 15% speed (extremely slow)
            enemy_speed *= 0.15
            
        # Only move during green or yellow light
        if GAME_STATE == "green" or GAME_STATE == "yellow" or DOLL_CURRENT_ROTATION > 45:  # Grace period during rotation
            # Calculate vector toward player
            dx = player_position[0] - enemy['position'][0]
            dy = player_position[1] - enemy['position'][1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Normalize and apply speed
                dx /= distance
                dy /= distance
                
                # Add random jitter to movement
                jitter = 0.3
                dx += random.uniform(-jitter, jitter)
                dy += random.uniform(-jitter, jitter)
                
                # Normalize again after jitter
                magnitude = math.sqrt(dx*dx + dy*dy)
                if magnitude > 0:
                    dx /= magnitude
                    dy /= magnitude
                
                # Move toward player with enemy's speed (modified by yellow light if applicable)
                enemy['position'][0] += dx * enemy_speed * delta_time
                enemy['position'][1] += dy * enemy_speed * delta_time
                
                # Update direction to face movement
                enemy['direction'] = math.degrees(math.atan2(dy, dx))
        else:
            # Check if enemy moved during red light
            enemy_moved = False
            last_pos = enemy.get('last_position', enemy['position'])
            
            dx = enemy['position'][0] - last_pos[0]
            dy = enemy['position'][1] - last_pos[1]
            move_distance = math.sqrt(dx*dx + dy*dy)
            
            # If enemy moved more than threshold during red light, it dies
            # Higher chance for red enemies (they're less cautious)
            chance_to_be_caught = 0.4  # Base chance
            if enemy['type'] == 'red':
                chance_to_be_caught = 0.6  # Higher for red enemies
            elif enemy['type'] == 'black':
                chance_to_be_caught = 0.2  # Lower for black enemies (more cautious)
                
            if move_distance > 1.0 and random.random() < chance_to_be_caught:
                enemy['alive'] = False
                print(f"A {enemy['type']} enemy was caught moving during red light!")
                
                # Add score for enemy elimination
                if enemy['type'] == 'red':
                    player_score += 100
                elif enemy['type'] == 'blue':
                    player_score += 200
                else:  # black
                    player_score += 500
                
                enemies_killed += 1

def update_powerups(delta_time):
    """Update power-ups and handle rotations."""
    global powerups
    
    for powerup in powerups:
        if not powerup['active']:
            continue
            
        # Rotate powerup for visual effect
        powerup['rotation'] += 90.0 * delta_time  # 90 degrees per second
        
        # Keep rotation between 0-360
        if powerup['rotation'] >= 360.0:
            powerup['rotation'] -= 360.0

def spawn_powerup():
    """Spawn a new powerup in the playing field."""
    global powerups
    
    # Check if we already have max powerups
    active_powerups = sum(1 for p in powerups if p['active'])
    if active_powerups >= NUM_POWERUPS:
        return
        
    # Find inactive powerup to reuse
    for powerup in powerups:
        if not powerup['active']:
            # Reposition and activate
            half_play_w = PLAY_AREA_WIDTH / 2 - 100
            powerup['position'][0] = random.uniform(-half_play_w, half_play_w)
            powerup['position'][1] = random.uniform(-PLAY_AREA_LENGTH / 4, PLAY_AREA_LENGTH / 2 - 500)
            powerup['rotation'] = 0.0
            powerup['active'] = True
            return
    
    # If no inactive powerups, create a new one
    if len(powerups) < NUM_POWERUPS * 2:  # Cap total number
        half_play_w = PLAY_AREA_WIDTH / 2 - 100
        x = random.uniform(-half_play_w, half_play_w)
        y = random.uniform(-PLAY_AREA_LENGTH / 4, PLAY_AREA_LENGTH / 2 - 500)
        
        new_powerup = {
            'position': [x, y, 15],
            'type': 'speed',
            'active': True,
            'rotation': 0.0
        }
        powerups.append(new_powerup)

def check_collisions():
    """Check for collisions between game objects."""
    global bullets, enemies, player_position, player_was_caught, powerups
    global player_speed_boost_active, player_speed_boost_timer, player_move_speed
    global player_score, enemies_killed, player_reached_finish
    
    # Check if player reached finish line - with a more lenient check
    # If player is within 95% of the way to the finish line, count it as a win
    start_y = -PLAY_AREA_LENGTH / 2
    end_y = PLAY_AREA_LENGTH / 2
    total_distance = end_y - start_y
    current_distance = player_position[1] - start_y
    progress = current_distance / total_distance
    
    # More forgiving win condition - 95% of the way counts as a win
    if progress >= 0.95:
        player_reached_finish = True
        # Calculate final score
        player_score += 10000  # Win bonus
        player_score += int(1000 / (time_survived / 60.0))  # Time bonus (better for faster completion)
        print(f"Congratulations! You reached the finish line! Final score: {player_score}")
        return  # Skip other collision checks if player won
    
    # Check bullet-enemy collisions
    for bullet in bullets[:]:
        hit_detected = False
        
        for enemy in enemies:
            if not enemy['alive']:
                continue
            
            # Get enemy size with scale factor
            enemy_scale = enemy.get('scale', 1.0)
            enemy_size = ENEMY_WIDTH * enemy_scale
            hit_radius = enemy_size * 1.5 + bullet['size']  # Much larger hit radius for easier aiming
            
            # First check - simple distance check for optimization
            dx = bullet['position'][0] - enemy['position'][0]
            dy = bullet['position'][1] - enemy['position'][1]
            dz = bullet['position'][2] - enemy['position'][2]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # If bullet is close to enemy, perform more detailed collision check
            if distance < hit_radius:
                # Actual collision detection - line segment against sphere
                # Check if the bullet's path (from last_position to position) intersects enemy
                
                # Vector from last position to current position
                move_x = bullet['position'][0] - bullet['last_position'][0]
                move_y = bullet['position'][1] - bullet['last_position'][1]
                move_z = bullet['position'][2] - bullet['last_position'][2]
                
                # Vector from last position to enemy center
                to_enemy_x = enemy['position'][0] - bullet['last_position'][0]
                to_enemy_y = enemy['position'][1] - bullet['last_position'][1]
                to_enemy_z = enemy['position'][2] - bullet['last_position'][2]
                
                # Length of movement vector
                move_length_sq = move_x*move_x + move_y*move_y + move_z*move_z
                
                if move_length_sq > 0.001:  # Avoid division by zero
                    move_length = math.sqrt(move_length_sq)
                    
                    # Normalize movement vector
                    move_x /= move_length
                    move_y /= move_length
                    move_z /= move_length
                    
                    # Project vector to enemy onto movement direction
                    dot_product = to_enemy_x*move_x + to_enemy_y*move_y + to_enemy_z*move_z
                    
                    # Clamp projection to segment length
                    dot_product = max(0, min(move_length, dot_product))
                    
                    # Find closest point on line segment to enemy center
                    closest_x = bullet['last_position'][0] + dot_product * move_x
                    closest_y = bullet['last_position'][1] + dot_product * move_y
                    closest_z = bullet['last_position'][2] + dot_product * move_z
                    
                    # Distance from closest point to enemy center
                    dx = closest_x - enemy['position'][0]
                    dy = closest_y - enemy['position'][1]
                    dz = closest_z - enemy['position'][2]
                    closest_distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                    
                    if closest_distance < enemy_size:
                        hit_detected = True
                else:
                    # If bullet hasn't moved much, just use the simple distance check
                    hit_detected = distance < enemy_size
                
                # If hit detected, process it
                if hit_detected:
                    # Reduce enemy health
                    enemy['health'] -= 1
                    
                    # Check if enemy is defeated
                    if enemy['health'] <= 0:
                        enemy['alive'] = False
                        
                        # Add score for enemy elimination
                        if enemy['type'] == 'red':
                            player_score += 100
                            show_notification("Red enemy eliminated! +100 points")
                        elif enemy['type'] == 'blue':
                            player_score += 200
                            show_notification("Blue enemy eliminated! +200 points")
                        else:  # black
                            player_score += 500
                            show_notification("Black enemy eliminated! +500 points")
                        
                        enemies_killed += 1
                        print(f"Enemy eliminated! ({enemy['type']})")
                    else:
                        if enemy['type'] == 'blue':
                            show_notification(f"Blue enemy hit! {enemy['health']}/2 health")
                        else:  # black
                            show_notification(f"Black enemy hit! {enemy['health']}/5 health")
                        print(f"Enemy hit! Health: {enemy['health']} remaining")
                    
                    # Remove bullet
                    if bullet in bullets:
                        bullets.remove(bullet)
                    
                    break  # Stop checking other enemies once we've hit one
            
        if hit_detected:
            continue  # Skip to next bullet if we already hit something
            
    # Check player-enemy collisions
    for enemy in enemies:
        if not enemy['alive']:
            continue
            
        # Calculate distance
        dx = player_position[0] - enemy['position'][0]
        dy = player_position[1] - enemy['position'][1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Adjust collision radius for black enemies
        enemy_width = ENEMY_WIDTH * enemy.get('scale', 1.0)
        
        # Check for collision
        if distance < player_width + enemy_width:
            player_was_caught = True
            print("An enemy caught you! Game over.")
            break
    
    # Check player-powerup collisions
    for powerup in powerups:
        if not powerup['active']:
            continue
            
        # Calculate distance
        dx = player_position[0] - powerup['position'][0]
        dy = player_position[1] - powerup['position'][1]
        dz = player_position[2] - powerup['position'][2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Check for collision with larger radius
        if distance < player_width + 25:  # Increased from 15 to 25
            # Apply powerup effect
            if powerup['type'] == 'speed':
                player_speed_boost_active = True
                player_speed_boost_timer = player_speed_boost_duration
                player_move_speed = player_base_speed * 1.7  # 70% speed boost
                show_notification("SPEED BOOST ACTIVATED! Run faster!")
                print("Speed boost activated!")
                
                # Add score
                player_score += 50
            
            # Deactivate powerup
            powerup['active'] = False
    
    # Check player-enemy collisions
    for enemy in enemies:
        if not enemy['alive']:
            continue
            
        # Calculate distance
        dx = player_position[0] - enemy['position'][0]
        dy = player_position[1] - enemy['position'][1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Adjust collision radius for black enemies
        enemy_width = ENEMY_WIDTH * enemy.get('scale', 1.0)
        
        # Check for collision
        if distance < player_width + enemy_width:
            player_was_caught = True
            print("An enemy caught you! Game over.")
            break
    
    # Check player-powerup collisions
    for powerup in powerups:
        if not powerup['active']:
            continue
            
        # Calculate distance
        dx = player_position[0] - powerup['position'][0]
        dy = player_position[1] - powerup['position'][1]
        dz = player_position[2] - powerup['position'][2]
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Check for collision
        if distance < player_width + 15:  # 15 = powerup radius
            # Apply powerup effect
            if powerup['type'] == 'speed':
                player_speed_boost_active = True
                player_speed_boost_timer = player_speed_boost_duration
                player_move_speed = player_base_speed * 1.7  # 70% speed boost
                print("Speed boost activated!")
                
                # Add score
                player_score += 50
            
            # Deactivate powerup
            powerup['active'] = False

def setup_camera():
    """Configure the camera position and orientation."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    aspect_ratio = float(WINDOW_WIDTH) / float(WINDOW_HEIGHT) if WINDOW_HEIGHT > 0 else 1.0
    gluPerspective(fovY, aspect_ratio, NEAR_CLIP, FAR_CLIP)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Calculate camera pivot point (slightly above player)
    pivot_z = player_position[2] + player_height * 0.6
    
    # Convert camera angles to radians
    cam_yaw_rad = math.radians(camera_yaw)
    cam_pitch_rad = math.radians(camera_pitch)
    
    # Calculate camera offset from pivot point
    offset_x = -camera_distance * math.cos(cam_yaw_rad) * math.cos(cam_pitch_rad)
    offset_y = -camera_distance * math.sin(cam_yaw_rad) * math.cos(cam_pitch_rad)
    offset_z = -camera_distance * math.sin(cam_pitch_rad)
    
    # Calculate camera position
    eye_x = player_position[0] + offset_x
    eye_y = player_position[1] + offset_y
    eye_z = pivot_z + camera_height + offset_z
    
    # Ensure camera doesn't go below ground
    min_cam_z = 5.0
    if eye_z < min_cam_z:
        eye_z = min_cam_z
    
    # Calculate look-at point
    center_x = player_position[0]
    center_y = player_position[1]
    center_z = pivot_z
    
    # Set up camera
    gluLookAt(eye_x, eye_y, eye_z,
              center_x, center_y, center_z,
              0.0, 0.0, 1.0)  # Up vector (z-axis)

# --- Event Handlers ---
def key_pressed(key, x, y):
    """Handle keyboard key press events."""
    global keys_pressed, print_debug
    
    keys_pressed.add(key.lower())
    
    # ESC to exit
    if key == b'\x1b':
        # First try with glutLeaveMainLoop, fall back to sys.exit if not available
        try:
            if bool(glutLeaveMainLoop):  # Check if function exists
                glutLeaveMainLoop()
            else:
                import sys
                sys.exit(0)
        except:
            import sys
            sys.exit(0)
        
    # P to toggle debug info
    if key == b'p':
        print_debug = not print_debug
        print(f"Debug Print: {print_debug}")
        
    # R to restart the game
    if key == b'r':
        restart_game()

def key_released(key, x, y):
    """Handle keyboard key release events."""
    keys_pressed.discard(key.lower())

def special_key_pressed(key, x, y):
    """Handle special key press events (arrow keys, etc.)."""
    keys_pressed.add(key)

def special_key_released(key, x, y):
    """Handle special key release events."""
    keys_pressed.discard(key)

def restart_game():
    """Reset the game to its initial state."""
    global player_position, target_player_position, player_direction, target_player_direction
    global player_was_caught, player_reached_finish, GAME_STATE, STATE_TIMER, NEXT_STATE_CHANGE
    global DOLL_CURRENT_ROTATION, DOLL_TARGET_ROTATION, bullets, enemies
    global player_score, time_survived, enemies_killed, GAME_START_TIME, GAME_PHASE
    global player_velocity, powerups, player_speed_boost_active, player_move_speed
    global STATE_CHANGE_INTERVAL_MIN, STATE_CHANGE_INTERVAL_MAX
    
    # Reset player
    player_position = list(player_start_pos)
    target_player_position = list(player_start_pos)
    player_direction = 90.0
    target_player_direction = 90.0
    player_was_caught = False
    player_reached_finish = False
    player_velocity = [0.0, 0.0, 0.0]
    
    # Reset speed boost
    player_speed_boost_active = False
    player_move_speed = player_base_speed
    
    # Reset game state
    GAME_STATE = "green"
    STATE_TIMER = 0
    NEXT_STATE_CHANGE = random.uniform(STATE_CHANGE_INTERVAL_MIN, STATE_CHANGE_INTERVAL_MAX)
    DOLL_CURRENT_ROTATION = 180
    DOLL_TARGET_ROTATION = 180
    GAME_START_TIME = time.time()
    GAME_PHASE = 1
    
    # Reset difficulty parameters to initial values
    STATE_CHANGE_INTERVAL_MIN = 3.0
    STATE_CHANGE_INTERVAL_MAX = 7.0
    
    # Reset scoring
    player_score = 0
    time_survived = 0
    enemies_killed = 0
    
    # Clear bullets
    bullets.clear()
    
    # Reset enemies
    setup_enemies()
    
    # Reset powerups
    setup_powerups()
    
    print("Game restarted!")

def display():
    """Main display function to render the game scene."""
    # Clear the screen
    glClearColor(FOG_COLOR[0], FOG_COLOR[1], FOG_COLOR[2], 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Get current window size (to handle full screen)
    viewport = glGetIntegerv(GL_VIEWPORT)
    window_width = viewport[2]
    window_height = viewport[3]
    
    # Calculate scaling factors for UI positioning
    width_scale = window_width / WINDOW_WIDTH
    height_scale = window_height / WINDOW_HEIGHT
    
    # Handle start screen
    if GAME_STATE == "start":
        draw_start_screen()
        glutSwapBuffers()
        return
    
    # Draw sky (no fog/lighting)
    draw_sky()
    
    # Set up camera view
    setup_camera()
    
    # Draw sun
    draw_fixed_sun()
    
    # Enable fog for distant objects
    glEnable(GL_FOG)
    
    # Draw environment elements
    draw_fixed_plants()
    draw_field()
    draw_giant_doll()
    
    # Draw game entities
    for powerup in powerups:
        if powerup['active']:
            draw_powerup(powerup)
    
    for enemy in enemies:
        draw_enemy(enemy)
    
    draw_player()
    
    for bullet in bullets:
        draw_bullet(bullet)
    
    # Disable fog for UI elements
    glDisable(GL_FOG)
    
    # Draw UI overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)  # Use current window size
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Create semi-transparent background for text to improve readability
    def draw_text_background(x, y, width, height, alpha=0.6):
        # Scale positions for current window size
        x = x * width_scale
        y = y * height_scale
        width = width * width_scale
        height = height * height_scale
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.1, 0.1, 0.1, alpha)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        glDisable(GL_BLEND)
    
    # Modified draw_text function to scale for window size
    def draw_scaled_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1.0, 1.0, 1.0)):
        # Scale positions for current window size
        x = x * width_scale
        y = y * height_scale
        
        glColor3fv(color)
        glWindowPos2f(x, y)
        for char in text:
            glutBitmapCharacter(font, ord(char))
    
    # Modified centered text function to scale for window size
    def draw_scaled_centered_text(text, y_pos, font=GLUT_BITMAP_TIMES_ROMAN_24, color=(1.0, 1.0, 1.0)):
        text_width = 0
        for char in text:
            text_width += glutBitmapWidth(font, ord(char))
        
        # Scale for window size
        x_pos = (window_width - text_width) // 2
        y_pos = y_pos * height_scale
        
        glColor3fv(color)
        glWindowPos2f(x_pos, y_pos)
        for char in text:
            glutBitmapCharacter(font, ord(char))
    
    # Draw title and fps - using more visible text colors and fonts
    title_color = (1.0, 0.2, 0.2) if GAME_STATE == "red" else (0.2, 0.9, 0.2)
    if GAME_STATE == "yellow":
        title_color = (1.0, 0.9, 0.1)  # Yellow for warning
    
    # Background for top information bar
    draw_text_background(0, WINDOW_HEIGHT - 40, WINDOW_WIDTH, 40)
    draw_scaled_text(10, WINDOW_HEIGHT - 25, f"{GAME_TITLE} - FPS: {fps}", GLUT_BITMAP_HELVETICA_18, title_color)
    
    # Draw game state indicator with translated Korean text - using larger font with background
    if GAME_STATE == "red":
        state_text = DIALOGUE_RED_LIGHT
        state_color = (1.0, 0.2, 0.2)
    elif GAME_STATE == "yellow":
        state_text = DIALOGUE_YELLOW_WARNING
        state_color = (1.0, 0.9, 0.1)
    else:  # green
        state_text = DIALOGUE_GREEN_LIGHT
        state_color = (0.2, 1.0, 0.2)
    
    # Background for game state text
    text_width = 0
    for char in state_text:
        text_width += glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    x_pos = (WINDOW_WIDTH - text_width) // 2
    
    draw_text_background(x_pos - 10, WINDOW_HEIGHT - 90, text_width + 20, 30)
    
    # Draw the actual text with high contrast
    draw_scaled_centered_text(state_text, WINDOW_HEIGHT - 75, GLUT_BITMAP_TIMES_ROMAN_24, state_color)
    
    # Draw countdown timer for state change with background
    time_left = NEXT_STATE_CHANGE - STATE_TIMER
    time_left_text = f"TIME: {time_left:.1f}s"
    
    text_width = 0
    for char in time_left_text:
        text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
    x_pos = (WINDOW_WIDTH - text_width) // 2
    
    draw_text_background(x_pos - 5, WINDOW_HEIGHT - 125, text_width + 10, 25)
    draw_scaled_centered_text(time_left_text, WINDOW_HEIGHT - 115, GLUT_BITMAP_HELVETICA_18, state_color)
    
    # Draw number of remaining bullets with background
    bullets_text = f"BULLETS: {len(bullets)}"
    text_width = 0
    for char in bullets_text:
        text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    draw_text_background(WINDOW_WIDTH - text_width - 25, WINDOW_HEIGHT - 60, text_width + 20, 25)
    draw_scaled_text(WINDOW_WIDTH - text_width - 15, WINDOW_HEIGHT - 50, bullets_text, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    # Draw current speed with background
    speed_text = f"SPEED: {player_move_speed:.0f}"
    if player_speed_boost_active:
        speed_text += " (BOOSTED!)"
    
    text_width = 0
    for char in speed_text:
        text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    draw_text_background(WINDOW_WIDTH - text_width - 25, WINDOW_HEIGHT - 90, text_width + 20, 25)
    draw_scaled_text(WINDOW_WIDTH - text_width - 15, WINDOW_HEIGHT - 80, speed_text, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    # Draw notification if active
    if notification_timer > 0:
        text_width = 0
        for char in notification_text:
            text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
        x_pos = (WINDOW_WIDTH - text_width) // 2
        
        draw_text_background(x_pos - 10, WINDOW_HEIGHT // 2 + 40, text_width + 20, 30, 0.8)
        draw_scaled_centered_text(notification_text, WINDOW_HEIGHT // 2 + 50, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 0.2))
    
    # Draw progress bar with background
    # Calculate progress for display
    start_y = -PLAY_AREA_LENGTH / 2
    end_y = PLAY_AREA_LENGTH / 2
    total_distance = end_y - start_y
    current_distance = player_position[1] - start_y
    progress = current_distance / total_distance
    
    # Draw progress bar background with semi-transparent dark rectangle
    bar_width = 350
    bar_height = 30
    bar_x = WINDOW_WIDTH - bar_width - 20
    bar_y = WINDOW_HEIGHT - 50
    
    # Draw semi-transparent background
    draw_text_background(bar_x - 10, bar_y - 5, bar_width + 20, bar_height + 10, 0.7)
    
    # Draw progress bar frame
    glColor3f(0.5, 0.5, 0.5)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(bar_x * width_scale, bar_y * height_scale)
    glVertex2f((bar_x + bar_width) * width_scale, bar_y * height_scale)
    glVertex2f((bar_x + bar_width) * width_scale, (bar_y + bar_height) * height_scale)
    glVertex2f(bar_x * width_scale, (bar_y + bar_height) * height_scale)
    glEnd()
    
    # Draw progress
    filled_width = bar_width * progress
    
    if progress < 0.5:
        # Red to yellow gradient
        r = 1.0
        g = progress * 2.0
        b = 0.0
    else:
        # Yellow to green gradient
        r = 1.0 - (progress - 0.5) * 2.0
        g = 1.0
        b = 0.0
    
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(bar_x * width_scale, bar_y * height_scale)
    glVertex2f((bar_x + filled_width) * width_scale, bar_y * height_scale)
    glVertex2f((bar_x + filled_width) * width_scale, (bar_y + bar_height) * height_scale)
    glVertex2f(bar_x * width_scale, (bar_y + bar_height) * height_scale)
    glEnd()
    
    # Draw percentage text
    progress_text = f"Progress: {int(progress * 100)}%"
    draw_scaled_text(bar_x + 10, bar_y + bar_height/2 - 5, progress_text, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    # Draw finish line label
    finish_label = "FINISH"
    draw_scaled_text(bar_x + bar_width - 60, bar_y + bar_height/2 - 5, finish_label, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    # Draw score with background
    score_width = 220
    score_height = 100
    score_x = 20
    score_y = WINDOW_HEIGHT - 70
    
    # Semi-transparent dark background
    draw_text_background(score_x, score_y - score_height, score_width, score_height, 0.7)
    
    # Draw score text
    title_text = "SCORE"
    draw_scaled_text(score_x + 10, score_y - 20, title_text, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 0.0))
    draw_scaled_text(score_x + 10, score_y - 45, f"Score: {player_score}", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    draw_scaled_text(score_x + 10, score_y - 70, f"Time: {time_survived:.1f}s", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    draw_scaled_text(score_x + 10, score_y - 95, f"Kills: {enemies_killed}", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    # Draw game over or win message with background
    if player_was_caught:
        big_message = "ELIMINATED!"
        if GAME_STATE == "red":
            detail_message = "You moved during RED LIGHT!"
        else:
            detail_message = "You were caught by an enemy!"
        
        # Background for game over message
        text_width = 0
        for char in big_message:
            text_width += glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        x_pos = (WINDOW_WIDTH - text_width) // 2
        
        draw_text_background(x_pos - 15, WINDOW_HEIGHT // 2 + 20, text_width + 30, 30, 0.8)
        draw_scaled_centered_text(big_message, WINDOW_HEIGHT // 2 + 30, GLUT_BITMAP_TIMES_ROMAN_24, (1.0, 0.2, 0.2))
        
        # Background for detail message
        text_width = 0
        for char in detail_message:
            text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
        x_pos = (WINDOW_WIDTH - text_width) // 2
        
        draw_text_background(x_pos - 10, WINDOW_HEIGHT // 2 - 10, text_width + 20, 25, 0.8)
        draw_scaled_centered_text(detail_message, WINDOW_HEIGHT // 2, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
        
        # Background for restart instruction
        restart_text = "Press R to restart"
        text_width = 0
        for char in restart_text:
            text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
        x_pos = (WINDOW_WIDTH - text_width) // 2
        
        draw_text_background(x_pos - 10, WINDOW_HEIGHT // 2 - 40, text_width + 20, 25, 0.8)
        draw_scaled_centered_text(restart_text, WINDOW_HEIGHT // 2 - 30, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
        
    elif player_reached_finish:
        # Win message
        big_message = "YOU WIN!"
        text_width = 0
        for char in big_message:
            text_width += glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        x_pos = (WINDOW_WIDTH - text_width) // 2
        
        draw_text_background(x_pos - 15, WINDOW_HEIGHT // 2 + 20, text_width + 30, 30, 0.8)
        draw_scaled_centered_text(big_message, WINDOW_HEIGHT // 2 + 30, GLUT_BITMAP_TIMES_ROMAN_24, (0.2, 1.0, 0.2))
        
        # Score message
        score_text = f"Final Score: {player_score}"
        text_width = 0
        for char in score_text:
            text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
        x_pos = (WINDOW_WIDTH - text_width) // 2
        
        draw_text_background(x_pos - 10, WINDOW_HEIGHT // 2 - 10, text_width + 20, 25, 0.8)
        draw_scaled_centered_text(score_text, WINDOW_HEIGHT // 2, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
        
        # Restart instruction
        restart_text = "Press R to restart"
        text_width = 0
        for char in restart_text:
            text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
        x_pos = (WINDOW_WIDTH - text_width) // 2
        
        draw_text_background(x_pos - 10, WINDOW_HEIGHT // 2 - 40, text_width + 20, 25, 0.8)
        draw_scaled_centered_text(restart_text, WINDOW_HEIGHT // 2 - 30, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    # Draw speed boost indicator if active
    if player_speed_boost_active:
        boost_text = f"SPEED BOOST: {player_speed_boost_timer:.1f}s"
        text_width = 0
        for char in boost_text:
            text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        draw_text_background(WINDOW_WIDTH - text_width - 25, 30, text_width + 20, 25, 0.8)
        draw_scaled_text(WINDOW_WIDTH - text_width - 15, 40, boost_text, GLUT_BITMAP_HELVETICA_18, (0.0, 0.8, 1.0))
    
    # Draw debug info if enabled
    if print_debug:
        draw_text_background(10, WINDOW_HEIGHT - 120, 400, 80, 0.6)
        
        px, py = int(player_position[0]), int(player_position[1])
        draw_scaled_text(15, WINDOW_HEIGHT - 50, f"PPos:({px},{py}) Dir:{player_direction:.0f}", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
        draw_scaled_text(15, WINDOW_HEIGHT - 70, f"Cam Y:{camera_yaw:.0f} P:{camera_pitch:.0f} D:{camera_distance:.0f}", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
        draw_scaled_text(15, WINDOW_HEIGHT - 90, f"Game: {GAME_STATE} Timer: {STATE_TIMER:.1f}/{NEXT_STATE_CHANGE:.1f}", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
        draw_scaled_text(15, WINDOW_HEIGHT - 110, f"Phase: {GAME_PHASE} Velocity: {player_velocity[0]:.1f}, {player_velocity[1]:.1f}", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    # Draw controls help with background
    controls_text = "Move: WASD | Camera: Arrows | Zoom: Z/X | Shoot: Space | Restart: R | Exit: ESC"
    text_width = 0
    for char in controls_text:
        text_width += glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    draw_text_background(10, 5, text_width + 10, 25, 0.7)
    draw_scaled_text(15, 10, controls_text, GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    
    # Restore rendering state
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glMatrixMode(GL_MODELVIEW)
    
    # Swap buffers to display the rendered scene
    glutSwapBuffers()

def print_controls():
    """Print game controls to the console."""
    print("\n--- Squid Game: Red Light Green Light Controls ---")
    print(" Player Move: WASD (Relative to Camera)")
    print(" Camera Tilt: Arrow Keys")
    print(" Camera Zoom: Z/X")
    print(" Shoot: Spacebar (Works during any light state)")
    print(" Restart Game: R")
    print(" Debug Info: P")
    print(" Exit: ESC")
    print("---------------------------------------")
    print(" Game Rules:")
    print(" - Move toward the finish line at the far end")
    print(" - FREEZE during RED LIGHT or you'll be eliminated instantly")
    print(" - YELLOW LIGHT is a warning that RED LIGHT is coming soon")
    print(" - Enemies:")
    print("   - RED: Fast, 1 hit to kill")
    print("   - BLUE: Medium speed, 2 hits to kill") 
    print("   - BLACK: Slow but big, 5 hits to kill")
    print(" - Collect speed boost power-ups for temporary faster movement")
    print(" - The game gets harder as time passes")
    print(" - Reach the white finish line to win!")
    print("---------------------------------------")

def main():
    """Initialize OpenGL and set up the game."""
    global last_update_time, fps_last_time, target_player_position, target_player_direction
    global target_camera_yaw, target_camera_pitch
    
    # Initialize target positions and orientations
    target_player_position = list(player_position)
    target_player_direction = player_direction
    target_camera_yaw = camera_yaw
    target_camera_pitch = camera_pitch
    
    # Initialize timing variables
    current_time = time.time()
    last_update_time = current_time
    fps_last_time = current_time
    
    # Initialize GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(bytes(f"{GAME_TITLE} v{GAME_VERSION}", 'utf-8'))
    
    # Set up OpenGL state
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set up lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # Set light properties
    light_pos = [sun_position[0], sun_position[1], sun_position[2], 0.0]  # Directional light
    light_ambient = [0.3, 0.3, 0.3, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]
    light_specular = [0.15, 0.15, 0.15, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    # Set global ambient light
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.35, 0.35, 0.35, 1.0])
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    
    # Set up fog
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogfv(GL_FOG_COLOR, FOG_COLOR + (1.0,))
    glFogf(GL_FOG_DENSITY, FOG_DENSITY)
    glHint(GL_FOG_HINT, GL_NICEST)
    
    # Adjust settings for performance mode
    if PERFORMANCE_MODE:
        pass  # Add performance adjustments if needed
    
    # Print controls to console
    print_controls()
    
    # Generate environment and enemies
    setup_fixed_environment()
    setup_enemies()
    setup_powerups()
    
    # Register GLUT callbacks
    glutDisplayFunc(display)
    glutKeyboardFunc(key_pressed)
    glutKeyboardUpFunc(key_released)
    glutSpecialFunc(special_key_pressed)
    glutSpecialUpFunc(special_key_released)
    glutIdleFunc(update_state)
    
    # Start the game loop
    print("Starting game... Press Space to start, ESC to exit")
    glutMainLoop()

# --- Entry Point ---
if __name__ == "__main__":
    main()