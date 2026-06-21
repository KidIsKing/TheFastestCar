# Constans
WIDTH = 1100
HEIGHT = 800

BUTTON_WIDTH = 197
BUTTON_HEIGHT = 100

START_Y_POS_PLAYER = 600

# Хитбоксы
PLAYER_HITBOX_DECREASE = (-110, 0)
ENEMY_HITBOX_DECREASE = (-180, 0)

# Ограничения дороги
ROAD_LEFT_BORDER = 120
ROAD_RIGHT_BORDER = WIDTH - 120

LANE_POSITIONS = [130, 320, 510, 700]  # X-координаты полос для спавна врагов

# Визуальные смещения
PLAYER_OFFSET_X = -1
ENEMY_OFFSET_X = -3

ENEMY_MIN_GAP = 5

ROAD_SPEED = 8

# Параметры скорости
BASE_WORLD_SPEED = 8
MAX_WORLD_SPEED = 18
MIN_WORLD_SPEED = 3
ACCELERATION_SMOOTHING = 0.03
DECELERATION_SMOOTHING = 0.05
MAX_PLAYER_OFFSET_Y = 100

FPS = 60

# Здоровье игрока
PLAYER_MAX_HEALTH = 100
PLAYER_INVULNERABLE_DURATION = 60  # длительность неуязвимости

# Урон (гауссово распределение)
BASE_DAMAGE = 15
DAMAGE_SPREAD = 6  # стандартное отклонение (разброс)
DAMAGE_MIN = 5
DAMAGE_MAX = 15

# Полоска здоровья
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 25
HEALTH_BAR_X = 20
HEALTH_BAR_Y = 20
HEALTH_BAR_BORDER = 3

# Типы бонусов
BONUS_TYPES = ["hp", "ex"]
MIN_BONUSES_COUNT = 1
MAX_BONUSES_COUNT = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Fade
FADE_SPEED = 10
MAX_FADE_ALPHA = 150

# Assets
ASSETS_PATH = "assets/"
ASSETS = {
    # Меню
    "main_background": ASSETS_PATH + "images/background_menu.png",
    "green_button": ASSETS_PATH + "images/buttons/green_button.png",
    "green_button_hover": ASSETS_PATH + "images/buttons/green_button_hover.png",
    "red_button": ASSETS_PATH + "images/buttons/red_button.png",
    "red_button_hover": ASSETS_PATH + "images/buttons/red_button_hover.png",
    "click_sound": ASSETS_PATH + "sounds/click.mp3",
    # Игра
    "player_car": ASSETS_PATH + "images/cars/player_car.png",
    "enemy_car": ASSETS_PATH + "images/cars/enemy_car.png",
    "road": ASSETS_PATH + "images/road.png",
    "hp": ASSETS_PATH + "images/bonuses/hp.png",
    "ex": ASSETS_PATH + "images/bonuses/ex.png",
    "bonus_sound": ASSETS_PATH + "sounds/bonus.mp3",
    "damage_sound": ASSETS_PATH + "sounds/damage.mp3",
    "car_crash_sound": ASSETS_PATH + "sounds/car_crash.mp3"
}
