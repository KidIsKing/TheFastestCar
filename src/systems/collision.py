from config.constants import ENEMY_MIN_GAP


def aabb_collide(hitbox1, hitbox2):
    """Проверка столкновения двух AABB-прямоугольников."""
    return (
        hitbox1.left <= hitbox2.right
        and hitbox1.right >= hitbox2.left
        and hitbox1.top <= hitbox2.bottom
        and hitbox1.bottom >= hitbox2.top
    )


def check_enemies_collision(enemies):
    """Проверка столкновений врагов друг с другом через AABB."""
    for i, enemy in enumerate(enemies):
        for other in enemies[i+1:]:
            if not aabb_collide(enemy.hitbox, other.hitbox):
                continue  # столкновения нет - идём дальше

            # Определяем, кто из врагов выше, а кто ниже
            top_enemy, bottom_enemy = (
                (enemy, other)
                if enemy.hitbox.top < other.hitbox.top
                else (other, enemy)
            )

            resolve_enemies_collision(
                top_enemy, bottom_enemy
            )  # разрешаем столкновение


def resolve_enemies_collision(top_enemy, bottom_enemy):
    """Разрешение столкновения врагов."""
    # Верхний враг замедляется до скорости нижнего
    top_enemy.speed = min(top_enemy.speed, bottom_enemy.speed)

    # Устанавливаем минимальный зазор между врагами, чтобы они не слипались
    min_gap = ENEMY_MIN_GAP
    if top_enemy.rect.bottom > bottom_enemy.rect.top - min_gap:
        top_enemy.rect.bottom = bottom_enemy.rect.top - min_gap
