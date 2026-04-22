"""
╔══════════════════════════════════════════════════════════╗
║          MAGIA PARA NAHOMY  ─  Pygame Edition            ║
║  Instalación:  pip install pygame numpy                  ║
║  Ejecución:    python nahomy_pygame.py                   ║
║  Salir:        ESC  /  Q  /  cerrar ventana              ║
╚══════════════════════════════════════════════════════════╝
"""

import pygame
import colorsys
import math
import random
import sys
from collections import deque

# ═══════════════════════════════════════════════════════════
#  CONFIGURACIÓN  ← edita aquí lo que quieras
# ═══════════════════════════════════════════════════════════
CFG = {
    "nombre"     : "Nahomy",
    "palabras"   : ["Increíble","Valiente","Amable","Inspiradora","Única",
                    "Radiante","Especial","Brillante","Soñadora","Maravillosa",
                    "Perfecta","Luminosa","Poderosa","Auténtica","Divina","Encantadora"],
    "mensaje"    : "  Para ti, que iluminas cada rincón del universo  ",
    "fullscreen" : True,          # False = ventana 1280×720
    "fps"        : 60,
    "bg"         : (3, 3, 16),
}

# ═══════════════════════════════════════════════════════════
#  INIT
# ═══════════════════════════════════════════════════════════
pygame.init()
if CFG["fullscreen"]:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption(f"Magia para {CFG['nombre']} 💖")
pygame.mouse.set_visible(False)

W, H   = screen.get_size()
CX, CY = W // 2, H // 2
clock  = pygame.time.Clock()

# ── Superficie alpha reutilizable (se limpia cada frame) ───
overlay = pygame.Surface((W, H), pygame.SRCALPHA)

# ═══════════════════════════════════════════════════════════
#  UTILIDADES DE COLOR
# ═══════════════════════════════════════════════════════════
def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h % 360 / 360,
                                   max(0, min(1, l / 100)),
                                   max(0, min(1, s / 100)))
    return (int(r * 255), int(g * 255), int(b * 255))

def hsla(h, s, l, a):
    return (*hsl(h, s, l), max(0, min(255, int(a))))

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_c(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

# ═══════════════════════════════════════════════════════════
#  FUENTES
# ═══════════════════════════════════════════════════════════
def make_font(sz, bold=True):
    for name in ["Palatino Linotype", "Palatino", "Georgia",
                 "Times New Roman", "DejaVu Serif"]:
        try:
            f = pygame.font.SysFont(name, max(8, sz), bold=bold)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.Font(None, max(8, sz))

F_NAME = make_font(int(H * .115))
F_CHAR = make_font(int(H * .026))
F_WORD = make_font(int(H * .031))
F_MSG  = make_font(int(H * .022), bold=False)

# ═══════════════════════════════════════════════════════════
#  CORAZÓN PARAMÉTRICO
# ═══════════════════════════════════════════════════════════
def heart_pts(scale, n=260):
    pts = []
    sz = min(W, H) * .067 * scale
    for i in range(n + 1):
        a = (i / n) * math.pi * 2
        x = 16 * math.pow(math.sin(a), 3)
        y = (13 * math.cos(a) - 5 * math.cos(2*a)
             - 2 * math.cos(3*a) - math.cos(4*a))
        pts.append((CX + x * sz / 16, CY + 10 - y * sz / 13))
    return pts

# ═══════════════════════════════════════════════════════════
#  CLASES DE PARTÍCULAS
# ═══════════════════════════════════════════════════════════

class Spark:
    __slots__ = ('x','y','vx','vy','life','max_life','r','color')
    def __init__(self, x, y, color, s=1.0):
        self.x, self.y   = float(x), float(y)
        self.vx = random.uniform(-1, 1) * 5 * s
        self.vy = random.uniform(-1, 1) * 5 * s - 2.2 * s
        self.life      = 0
        self.max_life  = random.randint(28, 55)
        self.r         = random.uniform(2, 4)
        self.color     = color

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += .11
        self.life += 1

    def alive(self): return self.life < self.max_life

    def draw(self, surf):
        a  = 1 - self.life / self.max_life
        r  = max(1, int(self.r * (1 - self.life / self.max_life * .4)))
        c  = (*self.color[:3], int(255 * a * a))
        # Estrella de 4 puntas
        pts = []
        for i in range(8):
            ang = i / 8 * math.pi * 2
            rad = r if i % 2 == 0 else r * .3
            pts.append((self.x + math.cos(ang) * rad,
                        self.y + math.sin(ang) * rad))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, c, [(int(p[0]), int(p[1])) for p in pts])


class Ring:
    __slots__ = ('x','y','r','max_r','life','max_life','color')
    def __init__(self, x, y, color):
        self.x, self.y  = x, y
        self.r          = 6.0
        self.max_r      = random.uniform(95, 170)
        self.life       = 0
        self.max_life   = 75
        self.color      = color[:3]

    def alive(self): return self.life < self.max_life

    def update(self):
        self.r += (self.max_r - self.r) * .09
        self.life += 1

    def draw(self, surf):
        a = int((1 - self.life / self.max_life) * 170)
        if a <= 0:
            return
        r = max(2, int(self.r))
        pygame.draw.circle(surf, (*self.color, a), (int(self.x), int(self.y)), r, 2)


class Petal:
    def __init__(self, random_y=True):
        self.x   = random.uniform(0, W)
        self.y   = random.uniform(-20, H + 40) if random_y else -20.0
        self.vy  = random.uniform(.3, 1.6)
        self.vx  = random.uniform(-.8, .8)
        self.rot = random.uniform(0, math.pi * 2)
        self.rs  = random.uniform(-.05, .05)
        self.a   = random.uniform(.3, .95)
        self.sz  = random.uniform(5, 14)
        self.hue = random.uniform(323, 355)
        self.t   = 0
        self._build_surf()

    def _build_surf(self):
        sz = int(self.sz)
        s  = pygame.Surface((sz * 4 + 4, sz * 4 + 4), pygame.SRCALPHA)
        cx = cy = sz * 2 + 2
        c1 = hsla(self.hue, 88, 82, int(self.a * 255))
        c2 = hsla(self.hue + 10, 70, 92, min(255, int(self.a * 255 + 30)))
        # Outer ellipse approximated as polygon
        pts1 = [(cx + math.cos(a) * sz * .38 - math.sin(a) * sz * .9,
                 cy + math.sin(a) * sz * .38 + math.cos(a) * sz * .9)
                for a in [i / 20 * math.pi * 2 for i in range(20)]]
        pts2 = [(cx + math.cos(a) * sz * .18 - math.sin(a) * sz * .45,
                 cy + math.sin(a) * sz * .18 + math.cos(a) * sz * .45)
                for a in [i / 12 * math.pi * 2 for i in range(12)]]
        pygame.draw.polygon(s, c1, [(int(p[0]), int(p[1])) for p in pts1])
        pygame.draw.polygon(s, c2, [(int(p[0]), int(p[1])) for p in pts2])
        self._surf = s

    def update(self):
        self.t  += 1
        self.x  += self.vx + math.sin(self.t * .009 + self.y * .008) * .8
        self.y  += self.vy
        self.rot += self.rs
        if self.y > H + 30:
            self.__init__(False)

    def draw(self, surf):
        rotated = pygame.transform.rotate(self._surf, math.degrees(-self.rot))
        w, h    = rotated.get_size()
        surf.blit(rotated, (int(self.x) - w // 2, int(self.y) - h // 2))


class ShootingStar:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.x     = random.uniform(0, W * .55)
        self.y     = random.uniform(0, H * .3)
        self.vx    = random.uniform(4, 9)
        self.vy    = random.uniform(.8, 3.5)
        self.life  = 0
        self.max_l = random.randint(32, 65)
        self.delay = random.randint(30, 380)
        self.trail = deque(maxlen=22)

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return
        self.trail.append((self.x, self.y))
        self.x += self.vx
        self.y += self.vy
        self.life += 1
        if self.life > self.max_l or self.x > W + 100:
            self._reset()

    def draw(self, surf):
        if self.delay > 0 or len(self.trail) < 2:
            return
        base_a = max(0.0, 1 - self.life / self.max_l)
        tl = list(self.trail)
        for i in range(len(tl) - 1):
            frac = i / len(tl)
            a    = int(base_a * frac * 230)
            if a < 5:
                continue
            w = max(1, int(2.5 * frac))
            pygame.draw.line(surf, (255, 255, 200, a),
                             (int(tl[i][0]), int(tl[i][1])),
                             (int(tl[i+1][0]), int(tl[i+1][1])), w)
        # Cabeza brillante
        pygame.draw.circle(surf, (255, 255, 255, int(base_a * 255)),
                           (int(self.x), int(self.y)), 3)
        # Destello en la cabeza
        pygame.draw.circle(surf, (255, 255, 180, int(base_a * 120)),
                           (int(self.x), int(self.y)), 6)


class FireworkParticle:
    __slots__ = ('x','y','vx','vy','life','max_life','r','hue')
    def __init__(self, hue):
        a        = random.uniform(0, math.pi * 2)
        spd      = random.uniform(1.5, 5.5)
        self.x = self.y = 0.0
        self.vx  = math.cos(a) * spd
        self.vy  = math.sin(a) * spd
        self.life     = 0
        self.max_life = random.randint(40, 85)
        self.r        = random.uniform(1.5, 2.8)
        self.hue      = hue

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += .07
        self.life += 1


class Firework:
    def __init__(self, x=None, y=None):
        self.x     = x if x is not None else int(W * (.12 + random.random() * .76))
        self.y     = y if y is not None else int(H * (.05 + random.random() * .42))
        self.hue   = random.uniform(0, 360)
        self.parts = [FireworkParticle(self.hue) for _ in range(34)]
        self.delay = 0 if x is not None else random.randint(60, 450)
        self.life  = 0
        self.max_l = 95

    def alive(self): return self.life < self.max_l

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            return
        self.life += 1
        for p in self.parts:
            p.update()

    def draw(self, surf):
        if self.delay > 0:
            return
        for p in self.parts:
            if p.life >= p.max_life:
                continue
            a = max(0.0, 1 - p.life / p.max_life)
            c = hsla(p.hue + p.life * 3, 100, 70, int(a * 255))
            r = max(1, int(p.r * a))
            pygame.draw.circle(surf, c,
                               (int(self.x + p.x), int(self.y + p.y)), r)


class FloatHeart:
    def __init__(self):
        self.x     = random.uniform(W * .08, W * .92)
        self.y     = float(H + 20)
        self.vy    = -random.uniform(.35, 1.2)
        self.vx    = random.uniform(-.7, .7)
        self.scale = random.uniform(.28, .9)
        self.alpha = int(random.uniform(.4, .82) * 255)
        self.hue   = random.uniform(322, 358)
        self.wobble= random.uniform(0, math.pi * 2)
        self.t     = 0
        self._build()

    def _build(self):
        sz = max(3, int(8 * self.scale))
        s  = pygame.Surface((sz * 8 + 4, sz * 8 + 4), pygame.SRCALPHA)
        c  = sz * 4 + 2
        pts = []
        for i in range(80):
            a = i / 80 * math.pi * 2
            x = 16 * math.pow(math.sin(a), 3)
            y = (13*math.cos(a) - 5*math.cos(2*a)
                 - 2*math.cos(3*a) - math.cos(4*a))
            pts.append((int(c + x * sz / 4), int(c - y * sz / 4)))
        col = hsl(self.hue, 100, 65)
        pygame.draw.polygon(s, (*col, self.alpha), pts)
        self._surf = s

    def update(self):
        self.t += 1
        self.x += self.vx + math.sin(self.t * .022 + self.wobble) * .55
        self.y += self.vy
        self.alpha = max(0, self.alpha - 1)

    def alive(self): return self.y > -40 and self.alpha > 0

    def draw(self, surf):
        s = self._surf.copy()
        s.set_alpha(self.alpha)
        w, h = s.get_size()
        surf.blit(s, (int(self.x) - w // 2, int(self.y) - h // 2))


class FloatingWord:
    def __init__(self, text):
        self.text  = text
        self._pos_init()
        self.vy    = -random.uniform(.14, .30)
        self.alpha = random.uniform(0, 1)
        self.da    = random.uniform(.003, .007)
        self.dir   = random.choice([1, -1])
        self.hue   = random.uniform(20, 70)

    def _pos_init(self):
        i   = CFG["palabras"].index(self.text) if self.text in CFG["palabras"] else 0
        col = i % 4
        row = i // 4
        self.x = W / 4 * col + W / 4 * (.1 + random.random() * .8)
        self.y = (H * (.04 + random.random() * .22) if row == 0
                  else H * (.63 + random.random() * .30))

    def update(self, t):
        self.y     += self.vy
        self.alpha += self.da * self.dir
        if self.alpha >= 1:
            self.alpha = 1
            self.dir   = -1
        if self.alpha <= 0:
            self.alpha = 0
            self.dir   = 1
            self._pos_init()

    def draw(self, surf, t):
        a = int(self.alpha * 228)
        if a < 5:
            return
        c   = hsl(self.hue + t * .2, 90, 74)
        txt = F_WORD.render(self.text, True, c)
        txt.set_alpha(a)
        surf.blit(txt, (int(self.x) - txt.get_width() // 2,
                        int(self.y) - txt.get_height() // 2))


class Glitter:
    def __init__(self):
        self.x   = random.uniform(0, W)
        self.y   = random.uniform(0, H)
        self.vy  = random.uniform(.25, .9)
        self.vx  = random.uniform(-.3, .3)
        self.sz  = random.uniform(.8, 2.2)
        self.hue = random.uniform(288, 360)
        self.t   = random.uniform(0, 100)

    def update(self):
        self.t += 1
        self.x += self.vx
        self.y += self.vy
        if self.y > H + 5:
            self.y = -5
            self.x = random.uniform(0, W)

    def draw(self, surf):
        a = int((0.2 + 0.5 * (.5 + .5 * math.sin(self.t * .04 + self.x * .1))) * 255)
        c = hsl(self.hue + self.t * .5, 100, 85)
        r = max(1, int(self.sz))
        pygame.draw.circle(surf, (*c, a), (int(self.x), int(self.y)), r)


class Typewriter:
    def __init__(self, text, speed=3):
        self.full  = text
        self.idx   = 0
        self.timer = 0
        self.speed = speed
        self.pause = 0

    def update(self):
        if self.pause > 0:
            self.pause -= 1
            return
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            if self.idx < len(self.full):
                self.idx += 1
            else:
                self.pause = CFG["fps"] * 6
                self.idx   = 0

    def draw(self, surf):
        text = self.full[:self.idx]
        if not text:
            return
        # Brillo
        glow = F_MSG.render(text, True, hsl(350, 100, 70))
        glow.set_alpha(60)
        for dx in [-2, 2]:
            surf.blit(glow, (W // 2 - glow.get_width() // 2 + dx, int(H * .935)))
        # Principal
        txt = F_MSG.render(text, True, (255, 200, 220))
        txt.set_alpha(210)
        surf.blit(txt, (W // 2 - txt.get_width() // 2, int(H * .935)))


# ═══════════════════════════════════════════════════════════
#  ESTRELLAS + CONSTELACIONES
# ═══════════════════════════════════════════════════════════
def make_stars(n=420):
    stars = []
    for _ in range(n):
        r = random.random()
        if r < .12:
            c = hsl(random.uniform(200, 240), 80, 90)
        elif r < .20:
            c = hsl(random.uniform(338, 368), 90, 90)
        else:
            c = (255, 255, 255)
        stars.append({'x': random.uniform(0, W), 'y': random.uniform(0, H),
                      'r': random.uniform(.15, 2.0),
                      'ph': random.uniform(0, math.pi*2),
                      'sp': random.uniform(.003, .025), 'c': c})
    return stars

STARS = make_stars()

# Constelaciones (un solo surface pre-renderizado)
def build_const_surf():
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    pool = STARS[:90]
    for i, s1 in enumerate(pool):
        for s2 in pool[i+1:]:
            d = math.hypot(s1['x'] - s2['x'], s1['y'] - s2['y'])
            if d < 85 and random.random() < .14:
                a = int(random.uniform(.03, .12) * 255)
                pygame.draw.line(s, (140, 160, 255, a),
                                 (int(s1['x']), int(s1['y'])),
                                 (int(s2['x']), int(s2['y'])), 1)
    return s

CONST_SURF = build_const_surf()

# ═══════════════════════════════════════════════════════════
#  HALO + CORAZONES EN ÓRBITA
# ═══════════════════════════════════════════════════════════
HALO = [{'angle': i / 32 * math.pi * 2,
          'speed': .012 + random.random() * .008,
          'c': hsl(i * 11 + 285, 100, 73)}
        for i in range(32)]

ORBIT = [{'angle': i / 8 * math.pi * 2,
           'speed': .008 + random.random() * .006,
           'r': (145 + random.random() * 32) * min(W, H) / 900,
           'scale': .28 + random.random() * .18,
           'hue': 316 + random.random() * 42}
         for i in range(8)]

def _small_heart_surf(sz, hue, alpha):
    s   = pygame.Surface((sz * 8 + 4, sz * 8 + 4), pygame.SRCALPHA)
    c2  = sz * 4 + 2
    pts = []
    for i in range(80):
        a = i / 80 * math.pi * 2
        x = 16 * math.pow(math.sin(a), 3)
        y = (13*math.cos(a) - 5*math.cos(2*a)
             - 2*math.cos(3*a) - math.cos(4*a))
        pts.append((int(c2 + x * sz / 4), int(c2 - y * sz / 4)))
    pygame.draw.polygon(s, (*hsl(hue, 100, 65), int(alpha * 255)), pts)
    return s

def draw_halo_orbit(surf, beat, t):
    hr = min(W, H) * .205 + beat * 18
    for h in HALO:
        h['angle'] += h['speed']
        px = CX + math.cos(h['angle']) * hr
        py = CY - 5 + math.sin(h['angle']) * hr * .72
        a  = int((.28 + beat * .62) * 255)
        pygame.draw.circle(surf, (*h['c'], a), (int(px), int(py)), 2)

    for o in ORBIT:
        o['angle'] += o['speed'] + beat * .003
        px = CX + math.cos(o['angle']) * o['r']
        py = CY - 5 + math.sin(o['angle']) * o['r'] * .72
        sz = max(2, int(5 * o['scale']))
        hs = _small_heart_surf(sz, o['hue'], .48 + beat * .42)
        w, h2 = hs.get_size()
        surf.blit(hs, (int(px) - w // 2, int(py) - h2 // 2))


# ═══════════════════════════════════════════════════════════
#  NOMBRE A LO LARGO DEL CORAZÓN
# ═══════════════════════════════════════════════════════════
def draw_name_on_heart(surf, pts, beat, t):
    name = CFG["nombre"]
    step = max(1, len(pts) // len(name))
    for i, pt in enumerate(pts):
        if i % step != 0:
            continue
        ci  = (i // step) % len(name)
        nxt = pts[(i + 1) % len(pts)]
        ang = math.atan2(nxt[1] - pt[1], nxt[0] - pt[0]) + math.pi / 2
        hue = 337 + math.sin(t * .04 + i * .28) * 18
        c   = hsl(hue, 100, int(65 + beat * 25))
        ch  = F_CHAR.render(name[ci], True, c)
        a   = int((.62 + beat * .38) * 255)
        ch.set_alpha(a)
        rot = pygame.transform.rotate(ch, -math.degrees(ang))
        surf.blit(rot, (int(pt[0]) - rot.get_width() // 2,
                        int(pt[1]) - rot.get_height() // 2))


# ═══════════════════════════════════════════════════════════
#  NOMBRE CENTRAL CON BRILLO
# ═══════════════════════════════════════════════════════════
def draw_center_name(surf, beat, t):
    name  = CFG["nombre"]
    color = hsl(338 + int(beat * 10), 100, int(63 + beat * 17))
    # Capas de brillo
    for bl, max_a in [(9, 70), (6, 100), (3, 80)]:
        a   = int(beat * max_a)
        if a < 5:
            continue
        gc  = hsl(340, 100, 72)
        txt = F_NAME.render(name, True, gc)
        txt.set_alpha(a)
        for dx, dy in [(-1,-1),(1,-1),(-1,1),(1,1),
                       (-2,0),(2,0),(0,-2),(0,2)]:
            surf.blit(txt, (CX + dx*bl - txt.get_width()//2,
                            CY + dy*bl - txt.get_height()//2))
    # Texto principal
    txt = F_NAME.render(name, True, color)
    txt.set_alpha(int((.88 + beat * .12) * 255))
    surf.blit(txt, (CX - txt.get_width() // 2, CY - txt.get_height() // 2))


# ═══════════════════════════════════════════════════════════
#  AURORA BOREAL
# ═══════════════════════════════════════════════════════════
def draw_aurora(surf, off):
    for i in range(6):
        y0  = H * .04 + i * 16
        amp = 28 + i * 14
        pts = [(0, 0)]
        for x in range(0, W + 8, 8):
            yy = (y0 + math.sin(x / W * math.pi * 3 + off * (.5 + i * .35)) * amp
                     + math.sin(x / W * math.pi * 6 + off * (1.8 + i * .25)) * amp * .35)
            pts.append((x, max(0, yy)))
        pts.extend([(W, 0), (0, 0)])
        c = hsl(155 + i * 22, 88, 58)
        a = int((.012 + i * .007) * 255 * 2.8)
        pygame.draw.polygon(surf, (*c, min(255, a)), pts)


# ═══════════════════════════════════════════════════════════
#  CORAZÓN — DRAW COMPLETO
# ═══════════════════════════════════════════════════════════
def draw_heart(surf, beat, t, pts):
    scale = 1 + beat * .18
    # Capas de aura exterior
    for extra, a_val in [(.24, 10), (.16, 18), (.09, 28)]:
        gp  = heart_pts(scale + extra)
        ipt = [(int(x), int(y)) for x, y in gp]
        col = hsla(345, 100, 55, a_val)
        pygame.draw.lines(surf, col, True, ipt, 4)

    # Relleno interior semi-transparente
    ipts = [(int(x), int(y)) for x, y in pts]
    fc   = hsla(345, 100, int(40 + beat * 22), int((.3 + beat * .15) * 255))
    pygame.draw.polygon(surf, fc, ipts)

    # Contorno principal (anti-aliased)
    stroke_l = hsl(350 + int(beat*10), 100, int(58 + beat*24))
    pygame.draw.aalines(surf, stroke_l, True, ipts)
    pygame.draw.lines(surf, stroke_l, True, ipts, 2)


# ═══════════════════════════════════════════════════════════
#  CURSOR MÁGICO
# ═══════════════════════════════════════════════════════════
cursor_trail = deque(maxlen=18)

def draw_cursor(surf, t):
    mx, my = pygame.mouse.get_pos()
    cursor_trail.append((mx, my))
    for i, (cx2, cy2) in enumerate(cursor_trail):
        a = int((i / len(cursor_trail)) * 180)
        r = max(1, int(8 * i / len(cursor_trail)))
        pygame.draw.circle(surf, (255, 120, 180, a), (cx2, cy2), r)
    # Cabeza del cursor
    pygame.draw.circle(surf, (255, 80, 140, 220), (mx, my), 7)
    pygame.draw.circle(surf, (255, 180, 210, 100), (mx, my), 12)


# ═══════════════════════════════════════════════════════════
#  INICIALIZAR OBJETOS
# ═══════════════════════════════════════════════════════════
petals       = [Petal() for _ in range(30)]
shots        = [ShootingStar() for _ in range(6)]
glitters     = [Glitter() for _ in range(65)]
fireworks_l  = [Firework() for _ in range(5)]
words        = [FloatingWord(w) for w in CFG["palabras"]]
typewr       = Typewriter(CFG["mensaje"])
sparks_l     : list[Spark]       = []
rings_l      : list[Ring]        = []
fhearts_l    : list[FloatHeart]  = []

# ═══════════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════
t = 0
aurora_off   = 0.0
heart_spawn  = 0

running = True
while running:
    clock.tick(CFG["fps"])
    t += 1
    aurora_off += .003

    # ── Eventos ────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
            if event.key == pygame.K_f:            # F = toggle fullscreen
                pygame.display.toggle_fullscreen()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            fireworks_l.append(Firework(mx, my))
            rings_l.append(Ring(mx, my, (255, 204, 68)))
            for _ in range(22):
                sparks_l.append(Spark(mx, my,
                    hsl(random.uniform(285, 370), 100, 76), 1.5))

    # ── Latido del corazón (patrón lub-dub real) ───────────
    period = 88
    ph = (t % period) / period
    if ph < .13:
        beat = math.sin(ph / .13 * math.pi)
    elif ph < .23:
        beat = .10
    elif ph < .36:
        beat = .78 * math.sin((ph - .23) / .13 * math.pi)
    else:
        beat = max(0.0, .78 * math.exp(-(ph - .36) * 14))
    beat  = max(0.0, beat)
    scale = 1 + beat * .18
    pts   = heart_pts(scale)

    # ── Limpiar overlay ────────────────────────────────────
    overlay.fill((0, 0, 0, 0))

    # ── Fondo ──────────────────────────────────────────────
    screen.fill(CFG["bg"])

    # Aurora boreal
    draw_aurora(overlay, aurora_off)

    # Nebulosas (radial sim con círculos concéntricos)
    for nx, ny, nr, nc, max_a in [
        (CX,        CY,        380, (130, 0,  90), 26),
        (int(W*.25),int(H*.4), 210, (55,  0, 120), 16),
        (int(W*.78),int(H*.62),190, (180, 0,  55), 15),
        (int(W*.08),int(H*.72),160, (0,   30,100), 13),
    ]:
        for step in range(5, 0, -1):
            sr = nr * step // 5
            a  = int(max_a * (1 - step / 6))
            pygame.draw.circle(overlay, (*nc, a), (nx, ny), sr)

    screen.blit(overlay, (0, 0))
    overlay.fill((0, 0, 0, 0))

    # Constelaciones (pre-renderizado)
    screen.blit(CONST_SURF, (0, 0))

    # ── Estrellas ──────────────────────────────────────────
    for s in STARS:
        a = .2 + .8 * (.5 + .5 * math.sin(t * s['sp'] + s['ph']))
        pygame.draw.circle(screen, (*s['c'], int(a * 255)),
                           (int(s['x']), int(s['y'])), max(1, int(s['r'])))

    # ── Glitter rain ───────────────────────────────────────
    for g in glitters:
        g.update()
        g.draw(overlay)

    # ── Estrellas fugaces ──────────────────────────────────
    for s in shots:
        s.update()
        s.draw(overlay)

    # ── Pétalos ────────────────────────────────────────────
    for p in petals:
        p.update()
        p.draw(overlay)

    # ── Fuegos artificiales ────────────────────────────────
    for fw in fireworks_l:
        fw.update()
        fw.draw(overlay)
    fireworks_l = [fw for fw in fireworks_l if fw.alive()]
    if len(fireworks_l) < 5 and random.random() < .003:
        fireworks_l.append(Firework())

    screen.blit(overlay, (0, 0))
    overlay.fill((0, 0, 0, 0))

    # ── Anillos expansivos ────────────────────────────────
    if beat > .85 and t % 5 == 0:
        rings_l.append(Ring(CX, CY - 10, hsl(340 + int(beat*15), 100, 68)))
    for r in rings_l:
        r.update()
        r.draw(overlay)
    rings_l = [r for r in rings_l if r.alive()]

    # ── Corazón ────────────────────────────────────────────
    draw_heart(overlay, beat, t, pts)
    draw_name_on_heart(overlay, pts, beat, t)

    # ── Halo + corazones en órbita ─────────────────────────
    draw_halo_orbit(overlay, beat, t)

    # ── Nombre central ─────────────────────────────────────
    draw_center_name(overlay, beat, t)

    screen.blit(overlay, (0, 0))
    overlay.fill((0, 0, 0, 0))

    # ── Palabras flotantes ─────────────────────────────────
    for w in words:
        w.update(t)
        w.draw(overlay, t)

    # ── Mini corazones flotando hacia arriba ───────────────
    heart_spawn += 1
    if heart_spawn >= 12:
        heart_spawn = 0
        fhearts_l.append(FloatHeart())
    for fh in fhearts_l:
        fh.update()
        fh.draw(overlay)
    fhearts_l = [fh for fh in fhearts_l if fh.alive()]

    # ── Chispas en el latido ───────────────────────────────
    if beat > .75 and t % 2 == 0:
        for i, pt in enumerate(pts):
            if i % 14 == 0 and random.random() < .32:
                sparks_l.append(Spark(pt[0], pt[1],
                    hsl(random.uniform(288, 372), 100, 78)))
        if beat > .90 and random.random() < .55:
            sparks_l.append(Spark(
                CX + random.uniform(-38, 38),
                CY + random.uniform(-38, 38),
                (255, 205, 68), 1.7))
    for sp in sparks_l:
        sp.update()
        sp.draw(overlay)
    sparks_l = [sp for sp in sparks_l if sp.alive()]

    # ── Destellos aleatorios ───────────────────────────────
    if t % 28 == 0:
        c = hsl(random.uniform(18, 65), 100, 85)
        rx, ry = random.uniform(0, W), random.uniform(0, H)
        pygame.draw.circle(overlay, (*c, 170),
                           (int(rx), int(ry)), random.randint(2, 4))

    # ── Cursor mágico ──────────────────────────────────────
    draw_cursor(overlay, t)

    # ── Typewriter ─────────────────────────────────────────
    typewr.update()
    typewr.draw(overlay)

    screen.blit(overlay, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()



