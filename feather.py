import os
import sys
import pygame

# some variable declaration #############
screen = None
_running = True
_elements = []
_animations = []

# mouse tracking #############
_mouse_pos = (0, 0)
_mouse_pressed = False
_mouse_was_pressed = False

# screen management ################################
_background_color = (0, 0, 0)
screen_center_x = 0
screen_center_y = 0
screen_left = 0
screen_right = 0
screen_top = 0
screen_bottom = 0
framerate = 60
def get_screen_width(): return screen.get_width()
def get_screen_height(): return screen.get_height()
def set_window_title(title: str): 
    pygame.display.set_caption(title)
def set_window_size(width:int, height:int): 
    pygame.display.set_mode((width, height), pygame.RESIZABLE)
def set_background_color(color):
    global _background_color
    if isinstance(color, str):
        color = pygame.Color(color)
    _background_color = color
    surface = pygame.display.get_surface()
    if surface is not None:
        surface.fill(color)

# sorteres and normalizers ############################
def _sort_elements():
    _elements.sort(key=lambda element: _normalize_layer(getattr(element, 'layer', 0)), reverse=True)
def _normalize_layer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

# keys ################################################
_keys_down = set()
_previous_keys = set()
_key_aliases = {'ENTER': 'RETURN', 'ESC': 'ESCAPE', 'CTRL': 'CONTROL', 'CMD': 'GUI'}
def key_pressed(key): return _key_name(key) in _keys_down
def _key_name(key): 
    name = str(key).upper()
    return _key_aliases.get(name, name)

# game loop ##############################################################################################################
def run(_init, _update):
    global _running, screen_center_x, screen_center_y, screen_left, screen_right, screen_top, screen_bottom, screen
    _running = True

    if not pygame.get_init():
        pygame.init()

    if pygame.display.get_surface() is None:
        pygame.display.set_mode((800, 600), pygame.RESIZABLE)

    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    screen_center_x = get_screen_width() // 2
    screen_center_y = get_screen_height() // 2
    screen_left = 0
    screen_right = get_screen_width()
    screen_top = 0
    screen_bottom = get_screen_height()

    if _init is not None:
        _init()

    while _running:
        global _mouse_pos, _mouse_pressed, _mouse_was_pressed
        _mouse_was_pressed = _mouse_pressed
        _mouse_pressed = pygame.mouse.get_pressed()[0]
        _mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end()
            elif event.type == pygame.KEYDOWN:
                _keys_down.add(_key_name(pygame.key.name(event.key)))
            elif event.type == pygame.KEYUP:
                _keys_down.discard(_key_name(pygame.key.name(event.key)))

        screen = pygame.display.get_surface()
        screen.fill(_background_color)

        _update()

        elapsed_seconds = clock.get_time() / 1000

        for obj in _elements:
            if isinstance(obj, Sprite):
                obj._update_animation(elapsed_seconds)

        for obj in _elements:
            if isinstance(obj, Button):
                obj._update_state()
                screen.blit(obj.image, obj.rect)
            elif isinstance(obj, Sprite) or isinstance(obj, Label):
                screen.blit(obj.image, obj.rect)
            elif isinstance(obj, Rectangle):
                pygame.draw.rect(screen, obj.color, obj.rect)
            elif isinstance(obj, Circle):
                pygame.draw.circle(screen, obj.color, (obj.x + obj.radius, obj.y + obj.radius), obj.radius)
        
        pygame.display.flip()
        clock.tick(framerate)
def end():
    global _running
    _running = False
def add_object(obj):
    _elements.append(obj)
    _sort_elements()
def create_object(objclass, name: str, parameters: list):
    obj = objclass(*parameters)
    user_frame = sys._getframe(1)
    user_frame.f_globals[name] = obj

# Sprite ############################################################
class Sprite:
    def __init__(self, image_path, x=0, y=0, width=None, height=None, layer=0, flip_x=False, flip_y=False, animations=None):
        file_extension = os.path.splitext(image_path)[1].lower().lstrip('.')

        try:
            if file_extension in {'png', 'svg'}:                                        
                self.image = pygame.image.load(image_path).convert_alpha()
            elif file_extension in {'jpg', 'jpeg'}:
                self.image = pygame.image.load(image_path).convert()
            else:
                raise ValueError("Unsupported image format: {}".format(file_extension))
        except (FileNotFoundError, pygame.error) as e:
            raise FileNotFoundError("Could not load image '{}': {}".format(image_path, str(e)))

        self.rect = self.image.get_rect(topleft=(x, y))

        if width is not None or height is not None:
            target_width = self.rect.width if width is None else width
            target_height = self.rect.height if height is None else height
            self._resize(target_width, target_height)

        self._layer = _normalize_layer(layer)
        self._flip_x = False
        self._flip_y = False
        self.flip_x = flip_x
        self.flip_y = flip_y
        self._animations = []
        self._current_animation = None
        if animations:
            for animation in animations:
                self.add_animation(animation['name'], animation['frames'], animation['frame_rate'])
        self.current_animation = ""
        add_object(self)

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
    
    @property
    def layer(self):
        return self._layer
    
    @layer.setter
    def layer(self, value):
        self._layer = _normalize_layer(value)
        _sort_elements()

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

            try:
                if file_extension in {'png', 'svg'}:
                    loaded_image = pygame.image.load(value).convert_alpha()
                elif file_extension in {'jpg', 'jpeg'}:
                    loaded_image = pygame.image.load(value).convert()
                else:
                    raise ValueError("Unsupported image format: {}".format(file_extension))
            except (FileNotFoundError, pygame.error) as e:
                raise FileNotFoundError("Could not load image '{}': {}".format(value, str(e)))
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

    @property
    def animations(self):
        return self._animations

    def _load_animation_frame(self, frame):
        if isinstance(frame, pygame.Surface):
            return frame
        try:
            return pygame.image.load(frame).convert_alpha()
        except (FileNotFoundError, pygame.error) as e:
            raise FileNotFoundError("Could not load animation frame '{}': {}".format(frame, str(e)))

    def _set_animation_frame(self, frame):
        position = self.rect.topleft
        frame = pygame.transform.scale(frame, self.rect.size)
        frame = pygame.transform.flip(frame, self._flip_x, self._flip_y)
        self._image = frame
        self.rect = frame.get_rect(topleft=position)

    def _update_animation(self, elapsed_seconds):
        if self._current_animation is None:
            return

        animation = self._current_animation
        animation['time_since_last_frame'] += elapsed_seconds
        frame_duration = 1 / animation['frame_rate']
        while animation['time_since_last_frame'] >= frame_duration:
            animation['time_since_last_frame'] -= frame_duration
            animation['current_frame'] = (animation['current_frame'] + 1) % len(animation['frames'])
            self._set_animation_frame(animation['frames'][animation['current_frame']])
    
    def play_animation(self, name):
        if self.current_animation == name and self._current_animation is not None:
            return

        for animation in self._animations:
            if animation['name'] == name:
                self._current_animation = animation
                self.current_animation = name
                self._current_animation['current_frame'] = 0
                self._current_animation['time_since_last_frame'] = 0
                self._set_animation_frame(animation['frames'][0])
                break
        else:
            raise ValueError("Animation not found: {}".format(name))

    def add_animation(self, name, frames, frame_rate):
        if frame_rate <= 0:
            raise ValueError("frame_rate must be greater than zero")
        loaded_frames = [self._load_animation_frame(frame) for frame in frames]
        if not loaded_frames:
            raise ValueError("An animation needs at least one frame")
        animation = {
            'name': name,
            'frames': loaded_frames,
            'frame_rate': float(frame_rate),
            'current_frame': 0,
            'time_since_last_frame': 0
        }
        self._animations.append(animation)

    def colliding_with(self, other):
        return self.rect.colliderect(other.rect) if isinstance(other, Sprite) else False

# Label #############################################################
class Label:
    def __init__(self, text='', x=0, y=0, layer=0, size=36, color='black', font_name=None, rounded=True):
        self._x = x
        self._y = y
        self._text = str(text)
        self._layer = _normalize_layer(layer)
        self._size = size
        self._color = color
        self._font_name = font_name
        self._rounded = rounded
        self.font = pygame.font.Font(self._font_name, self._size)
        self._render()
        add_object(self)

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
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        self._layer = _normalize_layer(value)
        _sort_elements()
    
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

# Rectangle #########################################################
class Rectangle:
    def __init__(self, x=0, y=0, layer=0, width=30, height=30, color=(255, 255, 255)):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self._layer = _normalize_layer(layer)
        add_object(self)

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
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        if hasattr(self, 'rect'):
            self.rect.width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        if hasattr(self, 'rect'):
            self.rect.height = value
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        self._color = value
    
    @property
    def layer(self):
        return self._layer
    
    @layer.setter
    def layer(self, value):
        try:
            self._layer = int(value)
        except (TypeError, ValueError):
            self._layer = 0
        _sort_elements()

# Circle ############################################################
class Circle:
    def __init__(self, x=0, y=0, layer=0, radius=15, color=(255, 255, 255)):
        self._x = x
        self._y = y
        self._radius = radius
        self.color = color
        self._layer = _normalize_layer(layer)
        add_object(self)

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
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        self._color = value
    
    @property
    def layer(self):
        return self._layer
    
    @layer.setter
    def layer(self, value):
        try:
            self._layer = int(value)
        except (TypeError, ValueError):
            self._layer = 0
        _sort_elements()

# Button ############################################################
class Button:
    def __init__(self, idleframe, clickedframe, hoveredframe, x=0, y=0, layer=0, width=None, height=None, istoggle=False):
        self._idleframe = idleframe
        self._clickedframe = clickedframe
        self._hoveredframe = hoveredframe
        self._x = x
        self._y = y
        self._layer = _normalize_layer(layer)
        self._width = width
        self._height = height
        self._istoggle = istoggle
        self._toggled = False
        
        self.isClicked = False
        self.isDown = False
        self.isReleased = False
        self._was_over = False
        
        self._current_frame = idleframe
        self._load_image(idleframe)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        if width is not None or height is not None:
            target_width = self.rect.width if width is None else width
            target_height = self.rect.height if height is None else height
            self._resize(target_width, target_height)
        
        add_object(self)
    
    def _load_image(self, frame_path):
        file_extension = os.path.splitext(frame_path)[1].lower().lstrip('.')
        
        try:
            if file_extension in {'png', 'svg'}:
                self.image = pygame.image.load(frame_path).convert_alpha()
            elif file_extension in {'jpg', 'jpeg'}:
                self.image = pygame.image.load(frame_path).convert()
            else:
                raise ValueError("Unsupported image format: {}".format(file_extension))
        except (FileNotFoundError, pygame.error) as e:
            raise FileNotFoundError("Could not load button image '{}': {}".format(frame_path, str(e)))
    
    def _resize(self, width, height):
        width = max(1, min(int(width), 8192))
        height = max(1, min(int(height), 8192))
        position = self.rect.topleft if hasattr(self, 'rect') else (self._x, self._y)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=position)
    
    def _is_over(self):
        return self.rect.collidepoint(_mouse_pos)
    
    def _update_state(self):
        global _mouse_pressed, _mouse_was_pressed
        
        is_over = self._is_over()
        mouse_just_clicked = _mouse_pressed and not _mouse_was_pressed
        mouse_just_released = not _mouse_pressed and _mouse_was_pressed
        
        self.isClicked = False
        self.isReleased = False
        self.isDown = False
        
        if self._istoggle:
            if mouse_just_clicked and is_over:
                self._toggled = not self._toggled
                self.isClicked = True
            self.isDown = self._toggled
        else:
            if mouse_just_clicked and is_over:
                self.isClicked = True
            if _mouse_pressed and is_over:
                self.isDown = True
            if mouse_just_released and is_over:
                self.isReleased = True
        
        if self._istoggle:
            if self._toggled:
                self._set_frame(self._clickedframe)
            elif is_over:
                self._set_frame(self._hoveredframe)
            else:
                self._set_frame(self._idleframe)
        else:
            if self.isDown or _mouse_pressed and is_over:
                self._set_frame(self._clickedframe)
            elif is_over:
                self._set_frame(self._hoveredframe)
            else:
                self._set_frame(self._idleframe)
        
        self._was_over = is_over
    
    def _set_frame(self, frame_path):
        if self._current_frame != frame_path:
            position = self.rect.topleft
            size = self.rect.size
            self._load_image(frame_path)
            self.image = pygame.transform.scale(self.image, size)
            self.rect = self.image.get_rect(topleft=position)
            self._current_frame = frame_path
    
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
    def layer(self):
        return self._layer
    
    @layer.setter
    def layer(self, value):
        self._layer = _normalize_layer(value)
        _sort_elements()
