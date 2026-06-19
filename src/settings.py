from constants import (
    BASE_WORLD_SPEED, MAX_WORLD_SPEED, MIN_WORLD_SPEED,
    ACCELERATION_SMOOTHING, DECELERATION_SMOOTHING, MAX_PLAYER_OFFSET_Y
)


class Settings:
    """Настройки и переменные, влияющие на игру."""

    def __init__(self):
        self.oncoming_traffic_enabled = False

        # Параметры логики скорости
        self.base_world_speed = BASE_WORLD_SPEED
        self.max_world_speed = MAX_WORLD_SPEED
        self.min_world_speed = MIN_WORLD_SPEED

        self.acceleration_smoothing = ACCELERATION_SMOOTHING  # плавность разгона
        self.deceleration_smoothing = DECELERATION_SMOOTHING  # плавность торможения

        self.max_player_offset_y = MAX_PLAYER_OFFSET_Y  # смещение по OY при разгоне


settings = Settings()
