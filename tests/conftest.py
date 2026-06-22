import sys
from pathlib import Path

# Добавляем src в путь, чтобы импорты работали
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
