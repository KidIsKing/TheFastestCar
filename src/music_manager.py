import pygame
from constants import ASSETS


class LoopingSound:
    """Зацикленные звуки."""

    def __init__(self, sound, channel_id, default_volume=0.3):
        self.sound = sound
        self.channel = pygame.mixer.Channel(channel_id)
        self.channel.set_volume(default_volume)
        self.default_volume = default_volume
        self.is_playing = False

    def start(self, loops=-1):
        if not self.is_playing:
            self.channel.play(self.sound, loops=loops)
            self.is_playing = True

    def stop(self):
        if self.is_playing:
            self.channel.stop()
            self.is_playing = False

    def pause(self):
        if self.is_playing:
            self.channel.pause()

    def unpause(self):
        if self.is_playing:
            self.channel.unpause()

    def set_volume(self, volume):
        self.channel.set_volume(max(0.0, min(1.0, volume)))


class MusicManager:
    """Фоновая музыка, зацикленные звуки и одноразовые эффекты."""

    # Каналы для независимого воспроизведения
    ENGINE_CHANNEL_ID = 1
    BRAKE_CHANNEL_ID = 2
    BONUS_CHANNEL_ID = 3
    DAMAGE_CHANNEL_ID = 4
    CRASH_CHANNEL_ID = 5
    DECEL_CHANNEL_ID = 6

    # Громкости по умолчанию
    MUSIC_VOLUME = 0.2
    ENGINE_VOLUME = 1
    BONUS_VOLUME = 0.25
    DAMAGE_VOLUME = 0.15
    CRASH_VOLUME = 0.35
    DECEL_VOLUME = 0.2

    def __init__(self):
        pygame.mixer.set_num_channels(8)
        self.is_music_playing = False
        self.is_music_paused = False
        pygame.mixer.music.load(ASSETS["music"])
        pygame.mixer.music.set_volume(self.MUSIC_VOLUME)

        self.engine = LoopingSound(
            pygame.mixer.Sound(ASSETS["engine_sound"]),
            self.ENGINE_CHANNEL_ID,
            self.ENGINE_VOLUME,
        )

        self.bonus_sound = pygame.mixer.Sound(ASSETS["bonus_sound"])
        self.bonus_sound.set_volume(self.BONUS_VOLUME)

        self.damage_sound = pygame.mixer.Sound(ASSETS["damage_sound"])
        self.damage_sound.set_volume(self.DAMAGE_VOLUME)

        self.crash_sound = pygame.mixer.Sound(ASSETS["car_crash_sound"])
        self.crash_sound.set_volume(self.CRASH_VOLUME)

        self.decel_sound = pygame.mixer.Sound(ASSETS["brake_sound"])
        self.decel_channel = pygame.mixer.Channel(self.DECEL_CHANNEL_ID)
        self.decel_sound.set_volume(self.DECEL_VOLUME)

        self.is_all_paused = False

    def start_music(self):
        if not self.is_music_playing:
            pygame.mixer.music.play(-1)
            self.is_music_playing = True
            self.is_music_paused = False

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_music_playing = False
        self.is_music_paused = False

    def pause_music(self):
        if self.is_music_playing and not self.is_music_paused:
            pygame.mixer.music.pause()
            self.is_music_paused = True

    def unpause_music(self):
        if self.is_music_playing and self.is_music_paused:
            pygame.mixer.music.unpause()
            self.is_music_paused = False

    def toggle_music_pause(self):
        if self.is_music_paused:
            self.unpause_music()
        else:
            self.pause_music()

    def start_engine(self):
        self.engine.start()

    def stop_engine(self):
        self.engine.stop()

    def update_engine_volume(self, speed_ratio):
        """Обновление громкости двигателя в зависимости от скорости."""
        if not self.engine.is_playing:
            return
        # Громкость от 0.15 до 0.6
        volume = 0.15 + speed_ratio * 0.45
        self.engine.set_volume(volume)

    def update_engine(self, is_accelerating, speed_ratio):
        """Обновление состояния двигателя."""
        if is_accelerating:
            self.start_engine()
            self.update_engine_volume(speed_ratio)
        else:
            self.stop_engine()

    def play_bonus(self):
        """Звук подбора бонуса."""
        pygame.mixer.Channel(self.BONUS_CHANNEL_ID).play(self.bonus_sound)

    def play_damage(self):
        """Звук получения урона."""
        pygame.mixer.Channel(self.DAMAGE_CHANNEL_ID).play(self.damage_sound)

    def play_crash(self):
        """Звук аварии."""
        pygame.mixer.Channel(self.CRASH_CHANNEL_ID).play(self.crash_sound)

    def play_decel(self):
        """Проигрывает звук понижения оборотов один раз."""
        # Если звук уже играет, он автоматически прервётся и начнётся заново
        self.decel_channel.play(self.decel_sound, loops=0)

    def stop_decel(self):
        """Прерывает звук понижения оборотов."""
        self.decel_channel.stop()

    def toggle_pause_all(self):
        if self.is_all_paused:
            self.unpause_music()
            self.engine.unpause()
            self.decel_channel.unpause()
            self.is_all_paused = False
        else:
            self.pause_music()
            self.engine.pause()
            self.decel_channel.pause()
            self.is_all_paused = True

    def stop_all(self):
        self.stop_music()
        self.engine.stop()
        self.stop_decel()
        self.is_all_paused = False
