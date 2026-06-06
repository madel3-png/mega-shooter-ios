import pygame, sys, random
pygame.init()

# 1. جلب أبعاد شاشة الآيفون الفريضة لعمل Full Screen كاملة
info = pygame.display.Info()
W = info.current_w if info.current_w > 0 else 800
H = info.current_h if info.current_h > 0 else 600
if W < 100 or H < 100: W, H = 800, 600

screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Mega Shooter Mobile")

WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, GRAY = (255,255,255), (0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (128,0,128), (100,100,100)
clock = pygame.time.Clock()

FS = int(H * 0.04)
font = pygame.font.SysFont("Arial", FS)
l_font = pygame.font.SysFont("Arial", int(H * 0.06))

WEAPONS = {
    "Pistol": {"price": 0, "cooldown": 500, "damage": 1, "owned": True},
    "Rifle": {"price": 100, "cooldown": 250, "damage": 2, "owned": False},
    "Shotgun": {"price": 250, "cooldown": 600, "damage": 5, "owned": False},
    "Minigun": {"price": 500, "cooldown": 50, "damage": 3, "owned": False}
}
current_weapon, coins, current_level, in_shop, game_over, running = "Pistol", 0, 1, False, False, True

# إعداد الأزرار بنسب مئوية من حجم الشاشة للآيفون
cheat_coin_rect = pygame.Rect(0, 0, int(W * 0.2), int(H * 0.12))
cheat_weapon_rect = pygame.Rect(int(W * 0.35), 0, int(W * 0.3), int(H * 0.12))
shop_btn_rect = pygame.Rect(W - int(W * 0.22) - 10, 10, int(W * 0.22), int(H * 0.07))
exit_shop_rect = pygame.Rect(20, H - int(H * 0.12), int(W * 0.25), int(H * 0.09))

weapon_buttons = []
y_p = int(H * 0.22)
for w_n in list(WEAPONS.keys()):
    weapon_buttons.append((w_n, pygame.Rect(20, y_p, W - 40, int(H * 0.09))))
    y_p += int(H * 0.12)

class Player:
    def __init__(self):
        self.sz = int(W * 0.08)
        self.rect = pygame.Rect(W//2, H - self.sz - 20, self.sz, self.sz)
        self.last_shot = 0
    def move(self, tx):
        self.rect.centerx = tx
        self.rect.clamp_ip(screen.get_rect())
    def draw(self): pygame.draw.rect(screen, BLUE, self.rect)

class Bullet:
    def __init__(self, x, y, dmg):
        self.rect = pygame.Rect(x - int(W*0.005), y, int(W*0.01), int(H*0.03))
        self.speed, self.damage = int(H * 0.02), dmg
    def update(self): self.rect.y -= self.speed
    def draw(self): pygame.draw.rect(screen, YELLOW, self.rect)

class Enemy:
    def __init__(self, is_boss=False, lvl=1):
        self.is_boss = is_boss
        if is_boss:
            w, h = int(W * 0.25), int(H * 0.1)
            self.rect = pygame.Rect(W//2 - w//2, int(H * 0.15), w, h)
            self.hp = 5000 if lvl == 1000 else lvl * 15
            self.max_hp = self.hp
            self.speed = int(W * 0.006)
        else:
            sz = int(W * 0.07)
            self.rect = pygame.Rect(random.randint(0, W - sz), random.randint(-150, -40), sz, sz)
            self.hp = 1 + (lvl // 50)
            self.speed = random.randint(2, 5) + (lvl // 200)
    def update(self):
        if self.is_boss:
            self.rect.x += self.speed
            if self.rect.right >= W or self.rect.left <= 0: self.speed *= -1
        else: self.rect.y += self.speed
    def draw(self):
        pygame.draw.rect(screen, PURPLE if self.is_boss else RED, self.rect)
        if self.is_boss:
            pygame.draw.rect(screen, GRAY, (self.rect.x, self.rect.y - 15, self.rect.width, 8))
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 15, (self.hp / self.max_hp) * self.rect.width, 8))

player, bullets, enemies = Player(), [], []

def spawn_enemies():
    enemies.clear()
    if current_level % 10 == 0 or current_level == 1000:
        enemies.append(Enemy(is_boss=True, lvl=current_level))
    else:
        for _ in range(5 + (current_level // 10)): enemies.append(Enemy(is_boss=False, lvl=current_level))

spawn_enemies()

while running:
    screen.fill(BLACK)
    touch_active = pygame.mouse.get_pressed()[0]
    m_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not in_shop and not game_over:
                if cheat_coin_rect.collidepoint(event.pos): coins += 1000
                elif cheat_weapon_rect.collidepoint(event.pos):
                    for w in WEAPONS: WEAPONS[w]["owned"] = True
                elif shop_btn_rect.collidepoint(event.pos): in_shop = True
            elif in_shop:
                if exit_shop_rect.collidepoint(event.pos): in_shop = False
                for w_n, btn in weapon_buttons:
                    if btn.collidepoint(event.pos):
                        w_d = WEAPONS[w_n]
                        if w_d["owned"] or coins >= w_d["price"]:
                            if not w_d["owned"]: coins -= w_d["price"]; w_d["owned"] = True
                            current_weapon = w_n
            elif game_over:
                current_level, coins, game_over = 1, 0, False
                spawn_enemies()

    if not in_shop:
        if not game_over:
            if touch_active and m_pos[1] > int(H * 0.15):
                player.move(m_pos[0])
                now = pygame.time.get_ticks()
                if now - player.last_shot > WEAPONS[current_weapon]["cooldown"]:
                    bullets.append(Bullet(player.rect.centerx, player.rect.top, WEAPONS[current_weapon]["damage"]))
                    player.last_shot = now

            for b in bullets[:]:
                b.update()
                if b.rect.bottom < 0: bullets.remove(b)

            for e in enemies[:]:
                e.update()
                if not e.is_boss and e.rect.top > H:
                    e.rect.y, e.rect.x = random.randint(-150, -40), random.randint(0, W - e.rect.width)
                if e.rect.colliderect(player.rect): game_over = True

            for b in bullets[:]:
                for e in enemies[:]:
                    if b.rect.colliderect(e.rect):
                        e.hp -= b.damage
                        if b in bullets: bullets.remove(b)
                        if e.hp <= 0:
                            if e in enemies: enemies.remove(e)
                            coins += 50 if e.is_boss else 5

        if len(enemies) == 0 and not game_over:
            current_level += 1
            if current_level > 1000:
                screen.fill(BLACK)
                txt = l_font.render("YOU WIN!", True, GREEN)
                screen.blit(txt, (W//2 - txt.get_width()//2, H//2 - txt.get_height()//2))
                pygame.display.flip(); pygame.time.wait(5000); running = False
            else: spawn_enemies()

        if not game_over:
            player.draw()
            for b in bullets: b.draw()
            for e in enemies: e.draw()
            screen.blit(font.render(f"Level: {current_level}/1000", True, WHITE), (10, 10))
            screen.blit(font.render(f"Coins: {coins}", True, YELLOW), (10, 15 + FS))
            screen.blit(font.render(f"Weapon: {current_weapon}", True, GREEN), (10, 20 + (FS * 2)))
            pygame.draw.rect(screen, GRAY, shop_btn_rect, border_radius=5)
            s_t = font.render("SHOP", True, WHITE)
            screen.blit(s_t, (shop_btn_rect.x + (shop_btn_rect.width - s_t.get_width())//2, shop_btn_rect.y + (shop_btn_rect.height - s_t.get_height())//2))
            if current_level % 10 == 0:
                b_a = font.render("!!! BOSS FIGHT !!!", True, RED)
                screen.blit(b_a, (W//2 - b_a.get_width()//2, int(H * 0.11)))
        else:
            g_o = l_font.render("GAME OVER", True, RED)
            r_s = font.render("Tap Screen to Restart", True, WHITE)
            screen.blit(g_o, (W//2 - g_o.get_width()//2, H//2 - 50))
            screen.blit(r_s, (W//2 - r_s.get_width()//2, H//2 + 20))
    else:
        screen.blit(l_font.render(f"SHOP - COINS: {coins}", True, YELLOW), (20, 30))
        for w_n, btn in weapon_buttons:
            w_d = WEAPONS[w_n]
            pygame.draw.rect(screen, GRAY if w_d["owned"] else RED, btn, border_radius=5)
            st = "EQUIPPED" if current_weapon == w_n else ("OWNED (Tap)" if w_d["owned"] else f"BUY: {w_d['price']}")
            txt = font.render(f"{w_n} -> {st}", True, WHITE)
            screen.blit(txt, (btn.x + 20, btn.y + (btn.height - txt.get_height())//2))
        pygame.draw.rect(screen, BLUE, exit_shop_rect, border_radius=5)
        ex = font.render("BACK", True, WHITE)
        screen.blit(ex, (exit_shop_rect.x + (exit_shop_rect.width - ex.get_width())//2, exit_shop_rect.y + (exit_shop_rect.height - ex.get_height())//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()