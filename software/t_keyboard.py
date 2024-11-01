import pygame
import sys
import textwrap
import time
from t_complete import TextPredictor

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AR Interface")

BACKGROUND = (240, 240, 245)
TEXT_COLOR = (20, 20, 20)
BUTTON_OUTLINE = (100, 100, 110)
TEXT_BOX_BG = (255, 255, 255)
CURSOR_COLOR = (0, 0, 0)

NUMBER_KEY = (173, 216, 230)
LETTER_KEY = (220, 220, 220)
SPECIAL_KEY = (144, 238, 144)
FUNCTION_KEY = (255, 200, 150)
ARROW_KEY = (255, 255, 150)

font = pygame.font.Font("CooperLtBT-Regular.ttf", 20)

text_box = pygame.Rect(20, 20, WIDTH - 40, 100)
user_text = ''
cursor_pos = 0

option_rects = [
    pygame.Rect(20, 140, (WIDTH - 60) // 2, 60),
    pygame.Rect((WIDTH + 20) // 2, 140, (WIDTH - 60) // 2, 60),
    pygame.Rect(20, 210, (WIDTH - 60) // 2, 60),
    pygame.Rect((WIDTH + 20) // 2, 210, (WIDTH - 60) // 2, 60)
]
options = ['', '', '', '']

keys = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'clear'],
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'delete'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '&', '<-', '->'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '?', '!', '$'],
    ['space']
]

key_rects = []
key_size = (WIDTH - 40) // 12
keyboard_width = 12 * key_size
start_y = 290
start_x = (WIDTH - keyboard_width) // 2

for y, row in enumerate(keys):
    for x, key in enumerate(row):
        if key == 'space':
            key_rect = pygame.Rect(start_x, start_y + (y * key_size), keyboard_width, key_size)
        elif key in ['clear', 'delete']:
            key_rect = pygame.Rect(start_x + (10 * key_size), start_y + (y * key_size), 2 * key_size, key_size)
        else:
            key_rect = pygame.Rect(start_x + (x * key_size), start_y + (y * key_size), key_size, key_size)
        key_rects.append((key_rect, key))

def get_key_color(key):
    if key.isdigit():
        return NUMBER_KEY
    elif key.isalpha():
        return LETTER_KEY
    elif key in ['clear', 'delete', 'space']:
        return FUNCTION_KEY
    elif key in ['<-', '->']:
        return ARROW_KEY
    else:
        return SPECIAL_KEY

def draw_gradient_rect(surface, color, rect):
    pygame.draw.rect(surface, color, rect)
    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(gradient, (255, 255, 255, 50), gradient.get_rect(), 0)
    gradient_rect = gradient.get_rect(topleft=rect.topleft)
    surface.blit(gradient, gradient_rect)

def draw_text_wrapped(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top + 10
    lineSpacing = -2
    
    fontHeight = font.size("Tg")[1] 

    while text:
        i = 1
        while font.size(text[:i])[0] < rect.width - 20 and i < len(text):
            i += 1

        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left + 10, y))
        y += fontHeight + lineSpacing

        text = text[i:]

    return text

def draw_interface():
    screen.fill(BACKGROUND)
    
    pygame.draw.rect(screen, TEXT_BOX_BG, text_box)
    pygame.draw.rect(screen, BUTTON_OUTLINE, text_box, 2)
    draw_text_wrapped(screen, user_text, TEXT_COLOR, text_box, font)

    lines = textwrap.wrap(user_text[:cursor_pos], width=(text_box.width - 20) // font.size('x')[0])
    cursor_y = text_box.y + 5 + (len(lines) - 1) * font.get_linesize()
    cursor_x = text_box.x + 10 + font.size(lines[-1] if lines else '')[0]
    pygame.draw.line(screen, CURSOR_COLOR, (cursor_x, cursor_y), (cursor_x, cursor_y + font.get_linesize()), 2)

    for rect, option in zip(option_rects, options):
        draw_gradient_rect(screen, LETTER_KEY, rect)
        pygame.draw.rect(screen, BUTTON_OUTLINE, rect, 2)
        option_surface = font.render(option, True, TEXT_COLOR)
        option_rect = option_surface.get_rect(center=rect.center)
        screen.blit(option_surface, option_rect)

    for rect, key in key_rects:
        draw_gradient_rect(screen, get_key_color(key), rect)
        pygame.draw.rect(screen, BUTTON_OUTLINE, rect, 1)
        key_surface = font.render(str(key), True, TEXT_COLOR)
        key_rect = key_surface.get_rect(center=rect.center)
        screen.blit(key_surface, key_rect)

    pygame.display.flip()

def handle_key_press(key):
    global user_text, cursor_pos
    if key == '<-':
        cursor_pos = max(cursor_pos - 1, 0)
    elif key == '->':
        cursor_pos = min(cursor_pos + 1, len(user_text))
    elif key == 'delete':
        if cursor_pos > 0:
            user_text = user_text[:cursor_pos-1] + user_text[cursor_pos:]
            cursor_pos -= 1
    elif key == 'clear':
        user_text = ''
        cursor_pos = 0
    elif key == 'space':
        user_text = user_text[:cursor_pos] + ' ' + user_text[cursor_pos:]
        cursor_pos += 1
    else:
        user_text = user_text[:cursor_pos] + key + user_text[cursor_pos:]
        cursor_pos += 1

predictor = TextPredictor()
predictor.load_common_words()

last_click_time = 0
click_delay = 0.4

running = True 
while running:
    if not predictor.is_trained:
        predictor.train_model()

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if text_box.collidepoint(event.pos):
                cursor_pos = len(user_text)
            for rect, key in key_rects:
                if rect.collidepoint(event.pos):
                    current_time = time.time()
                    if current_time - last_click_time > click_delay:
                        handle_key_press(key)
                        last_click_time = current_time
                        
                        predictions = predictor.predict(user_text)
                        options = predictions[:4]
                        while len(options) < 4:
                            options.append('')
            
            for rect, option in zip(option_rects, options):
                if rect.collidepoint(event.pos) and option:
                    user_text += f" {option.split()[-1]}"
                    cursor_pos = len(user_text)
                    
                    predictions = predictor.predict(user_text)
                    options = predictions[:4]
                    while len(options) < 4:
                        options.append('')

    draw_interface()

pygame.quit()
sys.exit()