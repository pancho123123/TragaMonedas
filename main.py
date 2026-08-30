import pygame, random
from random import randint
from collections import Counter


WIDTH = 800
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = ( 255, 255, 255)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont("serif", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_bar(surface, x, y, color, percentage):
    BAR_LENGHT = 143
    BAR_HEIGHT = 1
    fill_width = (percentage / 100) * BAR_LENGHT
    #border = pygame.Rect(x, y, BAR_LENGHT, BAR_HEIGHT)
    fill_x = x + BAR_LENGHT - fill_width    
    fill = pygame.Rect(fill_x, y, fill_width, BAR_HEIGHT)
    pygame.draw.rect(surface, color, fill)
    #pygame.draw.rect(surface, BLACK, border, 2)

def load_img(path):
    img = pygame.image.load(path).convert()
    img.set_colorkey(WHITE)
    return img

PLANT_DATA = {
    "girasol":{
        "carta":load_img("img/girasol_carta.png"),
        "plantada":load_img("img/girasol1.png")
},
    "lanzaguisante":{
        "carta":load_img("img/lanzaguisante_carta.png"),
        "plantada":load_img("img/lanzaguisante1.png")    
},
    "hielo":{
        "carta":load_img("img/hielo_carta.png"),
        "plantada":load_img("img/hielo1.png")
},
    "nuez":{
        "carta":load_img("img/nuez_carta.png"),
        "plantada":load_img("img/nuez1.png"),
        "plantada2":load_img("img/nuez3.png"),
        "plantada3":load_img("img/nuez3.png")
}
}

tipos_lista = list(PLANT_DATA.keys())
cartas_activas = []

GRID_COLS = 9
GRID_ROWS = 5
CELL_W = 80
CELL_H = 100
GRID_START_X = 50
GRID_START_Y = 100

GRID_POSITIONS = []
for fila in range(GRID_ROWS):
    for col in range(GRID_COLS):
        x = GRID_START_X + col * CELL_W
        y = GRID_START_Y + fila * CELL_H
        GRID_POSITIONS.append((x,y))

plantas_ocupadas = []
planta_arrastrando = None
imagen_fantasma = None

def get_posicion_mas_cercana(mouse_pos):
    mx, my = mouse_pos
    mas_cercana = None
    dist_min = 99999
    for (gx, gy) in GRID_POSITIONS:
        # centro de la celda
        cx = gx + CELL_W // 2
        cy = gy + CELL_H // 2
        dist = ((mx - cx)**2 + (my - cy)**2)**0.5
        if dist < dist_min:
            dist_min = dist
            mas_cercana = (gx, gy)
    return mas_cercana

class Zombie(pygame.sprite.Sprite):
    def __init__(self,num,plants):
        super().__init__()
        self.num = num
        self.image = zombie_img[num]
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = 900
        self.rect.bottom = random.choice([170,270,370,470,570])
        self.hp = zombie_hp[num]
        self.speed = 0.1
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.state = 0
        self.freeze_time = 7000
        self.last_hit = 0
        self.cooldown_ataque = 500
        self.last_attack = 0
        self.walk_counter = True
        self.estado = "walk"
        self.objetivo = None
        self.plants = plants

    def update(self):
        now = pygame.time.get_ticks() 
        if self.num == 2:        
            if self.hp <= 370:        
                self.image = zombie_img[1]
        if self.num == 1:
            if self.hp <= 200:
                self.image = zombie_img[0]       
        if self.hp <= 0:
            self.kill()
        for p in plants:
            if p not in self.plants:
                self.plants.add(p)
        if self.estado == "atacando":
            if self.objetivo not in self.plants:
                self.estado = "walk"
                self.objetivo = None
            else:
                self.attack()
                return
        if self.estado == "walk":
            for p in self.plants:
                mismo_carril = abs(p.rect.centery- self.rect.centery) < 30
                tocando = self.rect.colliderect(p.rect)
                if mismo_carril and tocando:
                    self.estado = "atacando"
                    self.objetivo = p
                    return
            self.move()
        if self.state == 1:
            if now -self.last_hit > self.freeze_time:
                self.state = 0
    def move(self):
        if self.state == 0:
            self.pos_x -= self.speed
        else:
            self.pos_x -= self.speed/2

        self.rect.x = int(self.pos_x)

    def attack(self):
        now = pygame.time.get_ticks()
        if now - self.last_attack > self.cooldown_ataque:
            num = randint(0,1)
            if num == 0:            
                crunch.play()
            else:
                crunch2.play()
            self.objetivo.hp -= 10
            self.last_attack = pygame.time.get_ticks()

class Plant(pygame.sprite.Sprite):
    def __init__(self, num, x, y, state=0):
        super().__init__()
        self.num = num 
        self.state = state
        self.image = PLANT_DATA[tipos_lista[num]]["carta"]
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = plant_hp[num]
        self.spawn_time = 30000
        self.start_time = pygame.time.get_ticks()
        if num == 1 or num == 2:
            self.ultimo_ataque = 0
            self.velocidad_ataque = 1500
        if num == 0:
            self.ultimo_sol = 0
            self.sun_time = randint(7000,17000)

    def update(self):
        now = pygame.time.get_ticks() 
        if self.state == 1:     
            if self.hp <= 0:
                self.kill()
                plantas_ocupadas.remove((self.rect.x,self.rect.y))
            if self.num == 3:
                if self.hp <= 50:
                    self.image = PLANT_DATA[tipos_lista[3]]["plantada2"]
            if self.num == 0:
                if now -  self.ultimo_sol >= self.sun_time:
                    sun = Sun(self.rect.x,self.rect.y)
                    suncrown = SunCrown(sun)
                    all_sprites.add(sun,suncrown)
                    suns.add(sun) 
                    self.ultimo_sol = pygame.time.get_ticks()
                    self.sun_time = randint(7000,17000)
            if self.num == 1 or self.num == 2:
                if now - self.ultimo_ataque >= self.velocidad_ataque:
                    self.shoot()
                    self.ultimo_ataque = pygame.time.get_ticks()
        elif self.state == 0:
            if now - self.start_time >= self.spawn_time:
                self.kill() 

    def shoot(self):
        if self.num == 1:
            disparo.play()
            guisante = Guisante(self.rect.right,self.rect.y,0)
        elif self.num == 2:
            disparo.play()
            guisante = Guisante(self.rect.right,self.rect.y,1)
        all_sprites.add(guisante)
        guisantes.add(guisante)

class Sun(pygame.sprite.Sprite):
    def __init__(self,x,y,speed=0):
        super().__init__()
        self.image = pygame.image.load("img/sol.png")
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pos_y = float(self.rect.y)
        self.speed = speed

    def update(self):
        self.pos_y += self.speed 
        self.rect.y = int(self.pos_y)

class SunCrown(pygame.sprite.Sprite):
    def __init__(self,sun):
        super().__init__()
        self.sun = sun
        self.image = pygame.image.load("img/sun_crown.png")
        self.image.set_colorkey(WHITE)
        self.image.set_alpha(150)
        self.rect = self.image.get_rect()
        self.rect.x = sun.rect.x - 21
        self.rect.y = sun.rect.y - 22
        self.pos_y = float(self.rect.y)

    def update(self):
        self.rect.x = self.sun.rect.x - 21
        self.rect.y = self.sun.rect.y - 22
        if self.sun not in all_sprites:
            self.kill()

class Diam(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load("img/diam1.png")
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Guisante(pygame.sprite.Sprite):
    def __init__(self,x,y,num):
        super().__init__()
        self.num = num
        if num == 0:
            self.image = pygame.image.load("img/guis.png")
        else :
            self.image = pygame.image.load("img/guis_hielo3.png")
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y        
        self.speed = 4

    def update(self):
        self.rect.x += self.speed
        
        if self.rect.x > 1000:
            self.kill()

class Palanca(pygame.sprite.Sprite):
    def __init__(self,pos=0):
        super().__init__()
        self.pos = pos
        self.image = stick_img[0]
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH//2 + 85
        self.rect.y = 10
        self.cooldown = 4500
        self.last_thrown = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.pos == 0:
            self.image = stick_img[0]
            self.image.set_colorkey(WHITE) 
            self.rect.y = 10
        else:
            self.image = stick_img[1]
            self.image.set_colorkey(WHITE)
            self.rect.y = 20 + 35
        if self.pos == 1:
            if now - self.last_thrown >= self.cooldown:
                self.pos = 0

            
def giro_palanca():
    palanca.pos = 1
    num1 = randint(0,5)
    num2 = randint(0,5)
    num3 = randint(0,5)
    numeros = [num1,num2,num3]
    img_tragamonedas.clear()
    img_tragamonedas.append(plant_img[num1])
    img_tragamonedas.append(plant_img[num2])
    img_tragamonedas.append(plant_img[num3])
    conteo = Counter(numeros)
    numero_repetido, veces_repetido = conteo.most_common(1)[0]
    if veces_repetido == 3:
        print(numero_repetido)
        print(veces_repetido)
        if numero_repetido != 4 and numero_repetido != 5:
            for i in range(3):
                plant = Plant(numero_repetido,WIDTH//2-randint(50,100),100)
                all_sprites.add(plant)
                cartas_activas.append(plant)
        else:
            if numero_repetido == 4:
                for i in range(10):
                    sun = Sun(WIDTH//2-randint(50,100),100)
                    suncrown = SunCrown(sun)
                    all_sprites.add(sun, suncrown)
                    suns.add(sun)
            else:
                for i in range(3):
                    diam = Diam(WIDTH//2-randint(50,100),100)
                    all_sprites.add(diam)
                    diams.add(diam)
    elif veces_repetido == 2:
        print(numero_repetido)
        print(veces_repetido)
        if numero_repetido != 4 and numero_repetido != 5:
            plant = Plant(numero_repetido,WIDTH//2-randint(50,100),100)
            all_sprites.add(plant)
            cartas_activas.append(plant)
        else:
            if numero_repetido == 4:
                for i in range(3):
                    sun = Sun(WIDTH//2-randint(50,100),100)
                    suncrown = SunCrown(sun)
                    all_sprites.add(sun, suncrown)
                    suns.add(sun)
            else:
                diam = Diam(WIDTH//2-randint(50,100),100)
                all_sprites.add(diam)
                diams.add(diam)
    
zombie_img = []
zombie_list = ["img/zombie1.png", "img/cono1.png", "img/cubeta1.png"]
for img in zombie_list:
    zombie_img.append(pygame.image.load(img))
plant_img = []
plant_list = ["img/girasol2.png", "img/lanzaguisante2.png","img/hielo2.png","img/nuez4.png","img/sol2.png","img/diam1.png"]
for img in plant_list:
    plant_img.append(pygame.image.load(img))
stick_img = []
stick_list = ["img/stick1.png","img/stick2.png"]
for img in stick_list:
    stick_img.append(pygame.image.load(img))
diam_img = pygame.image.load("img/diam1.png")

fond_img = pygame.image.load("img/fond.png")
fond_img.set_colorkey(WHITE)

zombie_hp = [200,370,1100]
plant_hp = [100,100,100,1000]

crunch = pygame.mixer.Sound("sound/crunch.mp3")
crunch2 = pygame.mixer.Sound("sound/crunch2.mp3")
disparo = pygame.mixer.Sound("sound/disparo.mp3")
click1 = pygame.mixer.Sound("sound/click1.mp3")
not_enought_sun = pygame.mixer.Sound("sound/not_enought_sun.mp3")
win = pygame.mixer.Sound("sound/win.mp3")
pause = pygame.mixer.Sound("sound/pause.mp3")
plant_planted = pygame.mixer.Sound("sound/plant_planted.mp3")
plant_selected = pygame.mixer.Sound("sound/plant_selected.mp3")
fin = pygame.mixer.Sound("sound/fin.mp3")


score = 50

all_sprites = pygame.sprite.Group()
guisantes = pygame.sprite.Group()
suns = pygame.sprite.Group()
diams = pygame.sprite.Group()
zombies = pygame.sprite.Group()
plants = pygame.sprite.Group()

palanca = Palanca()
all_sprites.add(palanca)
img_tragamonedas = []
zombie_spawn_time = 10000
zombie_count = 0
sun_spawn_time = randint(3000,9000)
money = 0

carga1 = False

running = True
while running:
    clock.tick(60)
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            if palanca.pos == 0:
                if score >= 25:
                    giro_palanca()
                    score -= 25
                    palanca.last_thrown = pygame.time.get_ticks()
                else:
                    not_enought_sun.play()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            pause.play()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        waiting = False
                        pause.play()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for sun in suns:
                if sun.rect.left -16  <= mouse_x <= sun.rect.right + 16 and sun.rect.top - 16 <= mouse_y <= sun.rect.bottom + 16:
                    sun.kill()
                    score += 25
            for d in diams:
                if d.rect.left  <= mouse_x <= d.rect.right and d.rect.top <= mouse_y <= d.rect.bottom:
                    d.kill()
                    money += 1000
            if WIDTH//2 + 100 <= mouse_x <= WIDTH//2 + 200 and 20 <= mouse_y <= 100:
                if palanca.pos == 0:
                    if score >= 25:
                        giro_palanca()
                        score -= 25
                        palanca.last_thrown = pygame.time.get_ticks()
                    else:
                        not_enought_sun.play()
            mx, my = event.pos
            #Caso A: No estoy arrastrando nada y hago click en una carta
            if planta_arrastrando is None:
            # recorre tus cartas (stick_img)
                for carta in cartas_activas:
                    if carta.rect.collidepoint(mx, my):
                        # empiezo a arrastrar
                        plant_selected.play()
                        planta_arrastrando = carta
                        imagen_fantasma = PLANT_DATA[tipos_lista[carta.num]]["plantada"]
                        cartas_activas.remove(carta)
                        break

            #Caso B: Ya estoy arrastrando y hago click
            else:
                pos_grilla = get_posicion_mas_cercana((mx, my))

                #Solo planta si no está ocupada
                if pos_grilla not in plantas_ocupadas:
                    # Crea la planta definitiva
                    plant_planted.play()
                    plant = planta_arrastrando
                    plant.rect.x = pos_grilla[0]
                    plant.rect.y = pos_grilla[1]
                    plant.image = PLANT_DATA[tipos_lista[plant.num]]["plantada"]  
                    plant.state = 1
                    #all_sprites.add(plant)
                    plantas_ocupadas.append(pos_grilla)
                    planta_arrastrando = None
                    imagen_fantasma = None
                    plants.add(plant)
                else:
                    if event.button == 3:
                        planta_arrastrando = None
                        imagen_fantasma = None
    if carga1:
        carga1 = False
#        for p in all_sprites:
#            if isinstance(palanca, Palanca):
#                pass
#            else:           
#                p.kill()
        all_sprites.empty()
        palanca = Palanca()
        all_sprites.add(palanca)
        score = 50
        plantas_ocupadas.clear()
        zombie_count = 0

    for zombie in zombies:
        for guisante in guisantes:
            if pygame.sprite.collide_rect(zombie,guisante):
                guisante.kill()
                zombie.hp -= 20
                if guisante.num == 1:
                    zombie.state = 1
                    zombie.last_hit = pygame.time.get_ticks()
              
    if now > sun_spawn_time:
        sun = Sun(randint(50,600),0,1)
        suncrown = SunCrown(sun)
        all_sprites.add(sun,suncrown)
        suns.add(sun)
        sun_spawn_time = now + randint(8000,11000)

    if now > zombie_spawn_time:
        if zombie_count > 40:        
            zombie = Zombie(random.choice([0,0,0,0,0,0,0,0,1,1,2]),plants)
            all_sprites.add(zombie)
            zombies.add(zombie)
            zombie_count += 1
        elif zombie_count > 7:
            zombie = Zombie(random.choice([0,0,0,0,1]),plants)
            all_sprites.add(zombie)
            zombies.add(zombie)
            zombie_count += 1
        else:
            zombie = Zombie(0,plants)
            all_sprites.add(zombie)
            zombies.add(zombie)
            zombie_count += 1
        zombie_spawn_time = now + 7000

    for zombie in zombies:
        if zombie.rect.right < 0:
            zombie.kill()
            fin.play()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        waiting = False
                        carga1 = True
    if score >= 2000:
        win.play()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False
                    carga1 = True

    screen.fill(BLACK)
    screen.blit(fond_img,(0,0))
    draw_text(screen,f"{score}",20,50,63,BLACK)
    if len(img_tragamonedas)>2:
        screen.blit(img_tragamonedas[0],(WIDTH//2-142,15))
        screen.blit(img_tragamonedas[1],(WIDTH//2-83,15))
        screen.blit(img_tragamonedas[2],(WIDTH//2-24,15))
    all_sprites.update()
    all_sprites.draw(screen)
    if planta_arrastrando is not None:
        mx, my = pygame.mouse.get_pos()
        x = mx - imagen_fantasma.get_width()//2
        y = my - imagen_fantasma.get_height()//2
        fantasma = imagen_fantasma.copy()
        fantasma.set_alpha(150) #0 invisible, 255 solido
        screen.blit(fantasma,(x,y))
    draw_bar(screen,WIDTH -192,HEIGHT - 17,(255,255,125),score /20)
    draw_bar(screen,WIDTH -192,HEIGHT - 16,(233,244,114),score /20)
    draw_bar(screen,WIDTH -192,HEIGHT - 15,(200,228,95),score /20)
    draw_bar(screen,WIDTH -192,HEIGHT - 14,(164,211,74),score /20)
    draw_bar(screen,WIDTH -192,HEIGHT - 13,(121,189,52),score /20)
    draw_bar(screen,WIDTH -192,HEIGHT - 12,(82,170,31),score /20)
    draw_bar(screen,WIDTH -192,HEIGHT - 11,(49,154,12),score /20)
    draw_text(screen,f"{score} / 2000 Sun",13,WIDTH - 120,HEIGHT - 22,(223,193,97))
    pygame.display.flip()
