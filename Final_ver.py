import pygame
import random
import math

##
##                       _oo0oo_
##                      o8888888o
##                      88" . "88
##                      (| -_- |)
##                      0\  =  /0
##                    ___/`---'\___
##                  .' \\|     |// '.
##                 / \\|||  :  |||// \
##                / _||||| -:- |||||- \
##               |   | \\\  -  /// |   |
##               | \_|  ''\---/''  |_/ |
##               \  .-\__  '-'  ___/-. /
##             ___'. .'  /--.--\  `. .'___
##          ."" '<  `.___\_<|>_/___.' >' "".
##         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
##         \  \ `_.   \_ __\ /__ _/   .-` /  /
##     =====`-.____`.___ \_____/___.-`___.-'=====
##                       `=---='
##
##
##     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##
##               佛祖保佑         永無BUG
##
##
##

# 初始化 Pygame
pygame.init()
p = 0
ew = pygame.image.load('cockroach1.png')
start_img = pygame.image.load('start_btn.png')
hard1_img = pygame.image.load('hard1.png')
hard2_img = pygame.image.load('hard2.png')
hard3_img = pygame.image.load('hard3.png')
bullet_img = pygame.image.load('bullet.png')
player_img = pygame.image.load('player.png')
bomb_img = pygame.image.load('bomb.png')
blood_img = pygame.image.load('blood.png')
# 設置遊戲視窗
window_width, window_height = 800, 600
win = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("cocokill")

# 定義顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY1 = (112, 128, 144)
GREY2 = (47, 79, 79)
GREY3 = (119, 136, 153)
LIGHT_BLUE = (51, 153, 255)
BROWN = (204, 102, 0)
OBSTACLE_COLOR = [GREY1, GREY2, GREY3]

# 設定角色參數
player_size = 20
player_speed = 5
player_health = 500000  # 玩家生命值

# 設定子彈參數
bullet_size = 5
bullet_speed = 25
bullets = []

# 設定敵人參數
enemy_size = 25
enemy_speed = 5
enemy_health = 5
num_enemies = 20
enemies = []
enemy_bullets = []
enemy_bullet_speed = 5

# 設定原子彈參數
bomb_size = 40
bomb_health = 40
bombs = []

# blood setup
bloods = []

# 設定地圖參數
tile_size = 25
map_width, map_height = 150, 150  # 地图尺寸（比窗口更大）
map_pixel_width, map_pixel_height = map_width * tile_size, map_height * tile_size

# 初始化玩家位置在地圖中央
player_x, player_y = map_pixel_width // 2, map_pixel_height // 2


# 生成一條彎曲的走廊
def generate_corridor_map():
    game_map = [[1 for _ in range(map_width)] for _ in range(map_height)]
    x, y = map_width // 2, map_height // 2
    game_map[y][x] = 0

    for _ in range(map_width * map_height // 2):
        direction = random.choice(['up', 'down', 'left', 'right'])
        if direction == 'up' and y > 1:
            y -= 1
        elif direction == 'down' and y < map_height - 2:
            y += 1
        elif direction == 'left' and x > 1:
            x -= 1
        elif direction == 'right' and x < map_width - 2:
            x += 1
        game_map[y][x] = 0
        if random.random() > 0.7:
            game_map[y][x - 1] = 0
            game_map[y][x + 1] = 0
            game_map[y - 1][x] = 0
            game_map[y + 1][x] = 0
    # 地圖邊緣視角問題debug
    for i in range(map_width):
        for j in range(0, 20):
            game_map[j][i] = 1
            game_map[map_height - (j + 1)][i] = 1

    for i in range(map_height):
        for j in range(0, 20):
            game_map[i][j] = 1
            game_map[i][map_width - (j + 1)] = 1

    return game_map


game_map = generate_corridor_map()


# 碰撞情況
def is_collision(new_x, new_y):
    tile_x = int(new_x) // tile_size
    tile_y = int(new_y) // tile_size
    if game_map[tile_y][tile_x] == 1:
        return True
    return False


# 再地圖中隨機生成敵人
def generate_enemies():
    for _ in range(num_enemies):
        while True:
            enemy_x = random.randint(0, map_pixel_width - enemy_size)
            enemy_y = random.randint(0, map_pixel_height - enemy_size)
            if not is_collision(enemy_x, enemy_y) and not is_collision(enemy_x + 1, enemy_y) and not is_collision(enemy_x, enemy_y + 1) and not is_collision(enemy_x + 1, enemy_y + 1):
                enemies.append({'x': enemy_x, 'y': enemy_y, 'health': enemy_health,
                                'dir': random.choice(['up', 'down', 'left', 'right'])})
                break

def generate_bomb():
    while True:
        bomb_x = random.randint(0, map_pixel_width - bomb_size)
        bomb_y = random.randint(0, map_pixel_height - bomb_size)
        if not is_collision(bomb_x, bomb_y) and not is_collision(bomb_x + 1, bomb_y) and not is_collision(bomb_x, bomb_y + 1) and not is_collision(bomb_x + 1, bomb_y + 1):
            bombs.append({'x': bomb_x, 'y': bomb_y, 'health': bomb_health})
            break

generate_enemies()
generate_bomb()

# 開始介面
class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        win.blit(self.image, self.rect)

        return action

start_button = Button(window_width/2-279/2, window_height/2-126/2, start_img)
mode1_button = Button(window_width/2-279/2, window_height/4-126/2, hard1_img)
mode2_button = Button(window_width/2-279/2, window_height/2-126/2, hard2_img)
mode3_button = Button(window_width/2-279/2, window_height/4*3-126/2, hard3_img)
main_menu = True
mode_menu = True
mode = 0



run = True
clock = pygame.time.Clock()
enemy_move_tick = 0
enemy_shoot_tick = 0
enemy_killed = 0
while main_menu or mode_menu :
    clock.tick(20)
    # 開始介面
    if main_menu == True:
        win.fill(GREY1)
        if start_button.draw():
            main_menu = False
    elif mode_menu == True:
        win.fill(GREY1)
        if mode1_button.draw():
            mode = 1
            mode_menu = False
        elif mode2_button.draw():
            mode = 2
            mode_menu = False
        elif mode3_button.draw():
            mode = 3
            mode_menu = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
while run:
    clock.tick(30)
    img = pygame.transform.scale(ew, (27, 40))
    img = pygame.transform.rotate(img, 50 + p * 4)
    bullet_img = pygame.transform.scale(bullet_img, (20, 20))
    bomb_img = pygame.transform.scale(bomb_img, (40, 40))
    player_img = pygame.transform.scale(player_img, (20, 20))
    blood_img = pygame.transform.scale(blood_img, (40, 40))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 發射子彈
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction_x = mouse_x + (player_x - window_width // 2)
            direction_y = mouse_y + (player_y - window_height // 2)
            angle = math.atan2(direction_y - player_y, direction_x - player_x)
            bullet_dx = bullet_speed * math.cos(angle)
            bullet_dy = bullet_speed * math.sin(angle)
            bullets.append({
                'x': player_x + player_size // 2,
                'y': player_y + player_size // 2,
                'dx': bullet_dx,
                'dy': bullet_dy
            })

    # 獲取案件狀態
    keys = pygame.key.get_pressed()

    new_x, new_y = player_x, player_y

    if keys[pygame.K_a] and player_x > 0:
        new_x -= player_speed
    if keys[pygame.K_d] and player_x < map_pixel_width - player_size:
        new_x += player_speed
    if keys[pygame.K_w] and player_y > 0:
        new_y -= player_speed
    if keys[pygame.K_s] and player_y < map_pixel_height - player_size:
        new_y += player_speed

    # 檢查新位置是否碰撞
    if not is_collision(new_x, new_y):
        player_x, player_y = new_x, new_y

    # 更新子彈位置
    new_bullets = []
    for bullet in bullets:
        bullet['x'] += bullet['dx']
        bullet['y'] += bullet['dy']

        if 0 <= bullet['x'] < map_pixel_width and 0 <= bullet['y'] < map_pixel_height:
            if not is_collision(bullet['x'], bullet['y']):
                new_bullets.append(bullet)

    bullets = new_bullets

    # 檢查子彈有沒有射到人
    for bullet in bullets:
        for enemy in enemies:
            if (enemy['x'] - 3 < bullet['x'] < enemy['x'] + 3 + enemy_size and
                    enemy['y'] - 3 < bullet['y'] < enemy['y'] + 3 + enemy_size):
                enemy['health'] -= 1
                if enemy['health'] <= 0:
                    bloods.append({'x':enemy['x'],'y':enemy['y']})
                    enemies.remove(enemy)
                    enemy_killed += 1
                if bullet in bullets:
                    bullets.remove(bullet)
                break
        for bomb in bombs:
            if (bomb['x'] - 3 < bullet['x'] < bomb['x'] + 3 + bomb_size and
                bomb['y'] - 3 < bullet['y'] < bomb['y'] + 3 + bomb_size):
                bomb['health'] -= 1
                if bomb['health'] <= 0:
                    enemy_killed += len(enemies)
                    for enemy in enemies:
                        bloods.append({'x': enemy['x'], 'y': enemy['y']})
                    enemies.clear()
                    bombs.clear()
                    bloods.clear()
                    enemy_bullets.clear()
                    generate_bomb()
                if bullet in bullets:
                    bullets.remove(bullet)
                break

    # 更新敵人位置
    enemy_move_tick += 1
    enemy_shoot_tick += 1

    if enemy_move_tick > 1:  # 敵人移動
        for enemy in enemies:
            direction = random.choice(['up', 'down', 'left', 'right'])
            if direction == 'up' and enemy['y'] > 0 and not is_collision(enemy['x'], enemy['y'] - enemy_speed):
                enemy['y'] -= enemy_speed
            elif direction == 'down' and enemy['y'] < map_pixel_height - enemy_size and not is_collision(enemy['x'],
                                                                                                         enemy[
                                                                                                             'y'] + enemy_speed):
                enemy['y'] += enemy_speed
            elif direction == 'left' and enemy['x'] > 0 and not is_collision(enemy['x'] - enemy_speed, enemy['y']):
                enemy['x'] -= enemy_speed
            elif direction == 'right' and enemy['x'] < map_pixel_width - enemy_size and not is_collision(
                    enemy['x'] + enemy_speed, enemy['y']):
                enemy['x'] += enemy_speed
        enemy_move_tick = 0

    if enemy_shoot_tick > 60:  # 敵人射擊
        for enemy in enemies:
            angle = math.atan2(player_y - enemy['y'], player_x - enemy['x'])
            bullet_dx = enemy_bullet_speed * math.cos(angle)
            bullet_dy = enemy_bullet_speed * math.sin(angle)
            enemy_bullets.append({
                'x': enemy['x'] + enemy_size // 2,
                'y': enemy['y'] + enemy_size // 2,
                'dx': bullet_dx,
                'dy': bullet_dy
            })
        enemy_shoot_tick = 0

    # 更新敵人子彈位置
    new_enemy_bullets = []
    for bullet in enemy_bullets:
        bullet['x'] += bullet['dx']
        bullet['y'] += bullet['dy']

        if 0 <= bullet['x'] < map_pixel_width and 0 <= bullet['y'] < map_pixel_height:
            if not is_collision(bullet['x'], bullet['y']):
                new_enemy_bullets.append(bullet)
    enemy_bullets = new_enemy_bullets
    # 子彈有沒有射到人
    for bullet in enemy_bullets:
        if (player_x < bullet['x'] < player_x + player_size and
                player_y < bullet['y'] < player_y + player_size):
            player_health -= 1
            if player_health <= 0:
                run = False  # 游戏结束
            enemy_bullets.remove(bullet)

    # 計算視角左上方位置
    offset_x = player_x - window_width // 2
    offset_y = player_y - window_height // 2

    # 確保視角不會超出邊界
    offset_x = max(0, min(offset_x, map_pixel_width - window_width))
    offset_y = max(0, min(offset_y, map_pixel_height - window_height))

    # 繪製地圖
    win.fill(WHITE)
    for row in range(map_height):
        for col in range(map_width):
            color = GREY3 if game_map[row][col] == 1 else WHITE
            pygame.draw.rect(win, color,
                             (col * tile_size - offset_x, row * tile_size - offset_y, tile_size, tile_size))

    # 繪製血
    for blood in bloods:

        win.blit(blood_img,(blood['x'] - offset_x, blood['y'] - offset_y))

    # 繪製角色
    win.blit(player_img, (player_x - offset_x, player_y - offset_y))

    # 繪製子弹
    for bullet in bullets:
        # pygame.draw.rect(win, BLUE, (bullet['x'] - offset_x, bullet['y'] - offset_y, bullet_size, bullet_size))
        win.blit(bullet_img, (bullet['x'] - offset_x, bullet['y'] - offset_y))
    # 繪製敌人
    for enemy in enemies:
        win.blit(img, (enemy['x'] - offset_x , enemy['y'] - offset_y))

    # 繪製敌人的子弹
    for bullet in enemy_bullets:
        pygame.draw.rect(win, BLACK, (bullet['x'] - offset_x, bullet['y'] - offset_y, bullet_size, bullet_size))

    for bomb in bombs:
        win.blit(bomb_img, (bomb['x'] - offset_x, bomb['y'] - offset_y))



    # 繪製玩家生命值
    font = pygame.font.SysFont(None, 24)
    health_text = font.render(f'Health: {player_health}', True, BLACK)
    enemy_killed_text = font.render(f'Enemy_killed: {enemy_killed}', True, BLACK)
    win.blit(health_text, (10, 10))
    win.blit(enemy_killed_text, (10, 40))
    if mode == 3:
        if p % 10 == 0:
            generate_enemies()
    else:
        if p % 500 == 0:
            generate_enemies()
    p += 1
    if p > 10000:
        p = 0

    pygame.display.update()

pygame.quit()