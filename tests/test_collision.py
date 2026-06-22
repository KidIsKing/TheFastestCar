from systems.collision import aabb_collide


class FakeRect:
    """Заглушка для pygame.Rect — нужны только 4 атрибута."""

    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom


class TestAABBCollision:
    """Тесты функции aabb_collide."""

    def test_no_collision_separated_horizontally(self):
        """Прямоугольники разделены по горизонтали — столкновения нет."""
        r1 = FakeRect(0, 0, 10, 10)
        r2 = FakeRect(20, 0, 30, 10)
        assert not aabb_collide(r1, r2)

    def test_no_collision_separated_vertically(self):
        """Прямоугольники разделены по вертикали — столкновения нет."""
        r1 = FakeRect(0, 0, 10, 10)
        r2 = FakeRect(0, 20, 10, 30)
        assert not aabb_collide(r1, r2)

    def test_collision_full_overlap(self):
        """Полное наложение — столкновение есть."""
        r1 = FakeRect(0, 0, 10, 10)
        r2 = FakeRect(0, 0, 10, 10)
        assert aabb_collide(r1, r2)

    def test_collision_partial_overlap(self):
        """Частичное наложение — столкновение есть."""
        r1 = FakeRect(0, 0, 10, 10)
        r2 = FakeRect(5, 5, 15, 15)
        assert aabb_collide(r1, r2)

    def test_collision_touching_edges(self):
        """Касание краями — считается столкновением (<= в условии)."""
        r1 = FakeRect(0, 0, 10, 10)
        r2 = FakeRect(10, 0, 20, 10)
        assert aabb_collide(r1, r2)

    def test_collision_inside(self):
        """Один прямоугольник внутри другого — столкновение есть."""
        r1 = FakeRect(0, 0, 20, 20)
        r2 = FakeRect(5, 5, 10, 10)
        assert aabb_collide(r1, r2)

    def test_no_collision_diagonal(self):
        """Прямоугольники по диагонали — столкновения нет."""
        r1 = FakeRect(0, 0, 10, 10)
        r2 = FakeRect(15, 15, 25, 25)
        assert not aabb_collide(r1, r2)
