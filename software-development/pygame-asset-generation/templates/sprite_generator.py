"""
Sprite generator template for Pygame projects.
Copy and modify for your character classes.
"""
from PIL import Image, ImageDraw
import os

OUTPUT_DIR = 'assets/sprites'
SPRITE_WIDTH = 40
SPRITE_HEIGHT = 60


def create_sprite(width=SPRITE_WIDTH, height=SPRITE_HEIGHT):
    """Create a transparent RGBA sprite."""
    return Image.new('RGBA', (width, height), (0, 0, 0, 0))


def draw_player_class(name):
    """Draw a player sprite. Modify colors and shapes per class."""
    img = create_sprite()
    d = ImageDraw.Draw(img)
    
    # Example: simple blocky character
    # Head
    d.rectangle([10, 5, 30, 20], fill=(100, 150, 200))
    # Body
    d.rectangle([8, 20, 32, 45], fill=(85, 153, 255))
    # Legs
    d.rectangle([10, 45, 20, 60], fill=(60, 120, 200))
    d.rectangle([20, 45, 30, 60], fill=(60, 120, 200))
    
    return img


def draw_enemy(type_name):
    """Draw an enemy sprite. Modify per enemy type."""
    img = create_sprite()
    d = ImageDraw.Draw(img)
    
    # Example: red enemy
    d.rectangle([8, 10, 32, 40], fill=(255, 100, 100))
    d.point((14, 20), fill=(255, 255, 255))  # eye
    d.point((26, 20), fill=(255, 255, 255))  # eye
    
    return img


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate player sprites
    for class_name in ['knight', 'rogue', 'mage', 'heavy']:
        path = os.path.join(OUTPUT_DIR, f'player_{class_name}.png')
        draw_player_class(class_name).save(path)
        print(f'Saved: {path}')
    
    # Generate enemy sprites
    for enemy_type in ['regular', 'elite', 'boss']:
        path = os.path.join(OUTPUT_DIR, f'enemy_{enemy_type}.png')
        draw_enemy(enemy_type).save(path)
        print(f'Saved: {path}')


if __name__ == '__main__':
    main()
