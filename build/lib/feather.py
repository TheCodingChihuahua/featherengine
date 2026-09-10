import os
import pygame

_running = True
_sprites = []
_labels = []
_rects = []

_keys_down = set()
_key_aliases = {
    'ENTER': 'RETURN',
    'ESC': 'ESCAPE',
    'CTRL': 'CONTROL',
    'CMD': 'GUI',
}


def _key_name(key):
    name = str(key).upper()
    return _key_aliases.get(name, name)


def run(_init, _update):
    global _running
    _running = True

    if not pygame.get_init():
        pygame.init()

    if pygame.display.get_surface() is None:
        pygame.display.set_mode((800, 600), pygame.RESIZABLE)

    clock = pygame.time.Clock()

    if _init is not None:
        _init()

    while _running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end()
            elif event.type == pygame.KEYDOWN:
                _keys_down.add(_key_name(pygame.key.name(event.key)))
            elif event.type == pygame.KEYUP:
                _keys_down.discard(_key_name(pygame.key.name(event.key)))

        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        _update()

        for sprite in _sprites:
            screen.blit(sprite.image, sprite.rect)

        for rect in _rects:
            pygame.draw.rect(screen, rect.color, (rect.x, rect.y, rect.width, rect.height))

        for label in _labels:
            screen.blit(label.image, label.rect)

        pygame.display.flip()
        clock.tick(60)


def end():
    global _running
    _running = False


def key_pressed(key):
    return _key_name(key) in _keys_down


def add_sprite(sprite):
    if sprite not in _sprites:
        _sprites.append(sprite)


def add_rect(rect):
    if rect not in _rects:
        _rects.append(rect)

def add_label(label):
    if label not in _labels:
        _labels.append(label)


class Sprite:
    def __init__(self, image_path, x=0, y=0, width=None, height=None, flip_x=False, flip_y=False):
        file_extension = os.path.splitext(image_path)[1].lower().lstrip('.')

        if file_extension in {'png', 'svg'}:
            self.image = pygame.image.load(image_path).convert_alpha()
        elif file_extension in {'jpg', 'jpeg'}:
            self.image = pygame.image.load(image_path).convert()
        else:
            raise ValueError("Unsupported image format: {}".format(file_extension))

        self.rect = self.image.get_rect(topleft=(x, y))

        if width is not None or height is not None:
            target_width = self.rect.width if width is None else width
            target_height = self.rect.height if height is None else height
            self._resize(target_width, target_height)

        self._flip_x = False
        self._flip_y = False
        self.flip_x = flip_x
        self.flip_y = flip_y
        add_sprite(self)

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, value):
        self.rect.x = value

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, value):
        self.rect.y = value

    @property
    def width(self):
        return self.rect.width

    @width.setter
    def width(self, value):
        self._resize(value, self.height)

    @property
    def height(self):
        return self.rect.height

    @height.setter
    def height(self, value):
        self._resize(self.width, value)

    def _resize(self, width, height):
        width = max(1, min(int(width), 8192))
        height = max(1, min(int(height), 8192))
        position = self.rect.topleft
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=position)

    @property
    def flip_x(self):
        return self._flip_x

    @flip_x.setter
    def flip_x(self, value):
        value = bool(value)
        if value != self._flip_x:
            self.image = pygame.transform.flip(self.image, True, False)
            self._flip_x = value

    @property
    def flip_y(self):
        return self._flip_y

    @flip_y.setter
    def flip_y(self, value):
        value = bool(value)
        if value != self._flip_y:
            self.image = pygame.transform.flip(self.image, False, True)
            self._flip_y = value

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        preserve_size = isinstance(value, str) and hasattr(self, 'rect')
        position = self.rect.topleft if hasattr(self, 'rect') else (0, 0)

        if isinstance(value, str):
            file_extension = os.path.splitext(value)[1].lower().lstrip('.')

            if file_extension in {'png', 'svg'}:
                loaded_image = pygame.image.load(value).convert_alpha()
            elif file_extension in {'jpg', 'jpeg'}:
                loaded_image = pygame.image.load(value).convert()
            else:
                raise ValueError("Unsupported image format: {}".format(file_extension))
        elif isinstance(value, pygame.Surface):
            loaded_image = value
        else:
            raise ValueError("Unsupported image type: {}".format(type(value)))

        if preserve_size:
            loaded_image = pygame.transform.scale(loaded_image, self.rect.size)
            loaded_image = pygame.transform.flip(
                loaded_image,
                getattr(self, '_flip_x', False),
                getattr(self, '_flip_y', False),
            )

        self._image = loaded_image
        self.rect = self.image.get_rect(topleft=position)

class Label:
    def __init__(self, x=0, y=0, text="", size=36, color=('black'), font_name=None, rounded=True):
        self._x = x
        self._y = y
        self._text = str(text)
        self._size = size
        self._color = color
        self._font_name = font_name
        self._rounded = rounded
        self.font = pygame.font.Font(self._font_name, self._size)
        self._render()
        add_label(self)

    def _render(self):
        self.image = self.font.render(self._text, self._rounded, self._color)
        self.rect = self.image.get_rect(topleft=(self._x, self._y))

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        if hasattr(self, 'rect'):
            self.rect.x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        if hasattr(self, 'rect'):
            self.rect.y = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self._render()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.font = pygame.font.Font(self._font_name, self._size)
        self._render()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._render()

    @property
    def font_name(self):
        return self._font_name

    @font_name.setter
    def font_name(self, value):
        self._font_name = value
        self.font = pygame.font.Font(self._font_name, self._size)
        self._render()

    @property
    def rounded(self):
        return self._rounded

    @rounded.setter
    def rounded(self, value):
        self._rounded = value
        self._render()

class Rectangle:
    def __init__(self, x, y, width, height, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        add_rect(self)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value