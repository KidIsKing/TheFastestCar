from entities.bonus import Bonus
from config.constants import MAX_BONUSES_ON_SCREEN, ASSETS


def check_bonus_spawn(bonus_director, player, current_world_speed, bonuses):
    """Проверка необходимости спавна бонуса через режиссёра."""
    if len(bonuses) >= MAX_BONUSES_ON_SCREEN:
        return bonuses

    bonus_type = bonus_director.should_spawn_bonus(
        player,
        current_world_speed
        )

    if bonus_type is not None:
        count = bonus_director.get_bonus_count()

        count = min(count, MAX_BONUSES_ON_SCREEN - len(bonuses))

        for _ in range(count):
            bonuses.append(Bonus(ASSETS[bonus_type], bonus_type))

    return bonuses
