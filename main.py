import pygame
import random
import os
import urllib.request
import json
import sys

# --- ÇALIŞMA KONUMUNU AYARLA (EXE UYUMLU) ---
if getattr(sys, 'frozen', False):
    # Eğer .exe olarak çalışıyorsa, .exe'nin bulunduğu klasörü al
    application_path = os.path.dirname(sys.executable)
else:
    # Eğer .py olarak çalışıyorsa, dosyanın bulunduğu klasörü al
    application_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(application_path)

# --- OYUN AYARLARI ---
pygame.init()
pygame.mixer.init()

# 1. EKRAN AYARLARI
real_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
info = pygame.display.Info()
REAL_W, REAL_H = real_screen.get_size()

# 2. SANAL ÇÖZÜNÜRLÜK
TARGET_HEIGHT = 360
if REAL_W > REAL_H: 
    aspect_ratio = REAL_W / REAL_H
    orientation = "LANDSCAPE"
else: 
    aspect_ratio = REAL_H / REAL_W
    orientation = "PORTRAIT"

V_H = TARGET_HEIGHT
V_W = int(V_H * aspect_ratio)

canvas = pygame.Surface((V_W, V_H)).convert()

pygame.display.set_caption("Chicken Run - v0.8.2 Final Fix")

# --- ORANSAL AYARLAR ---
PIXEL_SIZE = 2 
tavuk_boyut = PIXEL_SIZE * 12 

zemin_yukseklik = int(V_H * 0.18)
ZEMIN_SEVIYESI = V_H - zemin_yukseklik

yer_cekimi = V_H * 0.0025
ziplama_gucu = -(V_H * 0.042)

cit_genislik = PIXEL_SIZE * 11
cit_yukseklik = PIXEL_SIZE * 14

# --- RENKLER ---
GOK_GUNDUZ = (135, 206, 250)
GOK_AKSAM = (200, 100, 100)
GOK_GECE = (20, 24, 60) 

BULUT_BEYAZI = (255, 255, 255)
BULUT_GOLGESI = (200, 220, 255)
YILDIZ_RENGI = (255, 255, 200)

SPLASH_BG = (255, 215, 0)
SPLASH_TEXT = (20, 20, 20)

T_BEYAZ = (255, 255, 255)
T_SIYAH = (30, 30, 50)
T_MAVI_GOLGE = (170, 190, 230)
T_KIRMIZI = (220, 50, 50)
T_SARI = (255, 200, 50)
T_TURUNCU = (230, 120, 30)

C_KOYU_KAHVE = (70, 30, 20)
C_ORTA_KAHVE = (110, 60, 30)
C_ACIK_KAHVE = (150, 90, 50)
C_SIYAH = (40, 20, 10)

Z_CIM_TABAN = (100, 200, 60)
Z_CIM_TEL_1 = (120, 220, 70)
Z_CIM_TEL_2 = (80, 180, 50)
Z_TOPRAK_UST = (120, 80, 40)
Z_TOPRAK_ORTA = (90, 50, 30)
Z_TOPRAK_ALT = (60, 30, 20)

G_SARI_PARLAK = (255, 255, 100)
AY_BEYAZI = (240, 240, 255)
AY_GOLGESI = (180, 180, 200)

# UI RENKLERİ
UI_GOLD = (255, 215, 0)
UI_BORDER = (0, 0, 0)
UI_SHADOW = (50, 50, 50)
BTN_KIRMIZI = (200, 50, 50)
BTN_YESIL = (50, 200, 50)
BTN_CIKIS_RENK = (200, 50, 50)
UI_GREY = (150, 150, 150)

SIYAH = (0, 0, 0)
BEYAZ = (255, 255, 255)
IMZA_RENGI = (200, 0, 0)
MESAJ_RENGI = (255, 255, 255)
SKOR_GOLGESI = (50, 50, 50)
OVERLAY_RENK = (0, 0, 0, 150) 

clock = pygame.time.Clock()
FPS = 60

# --- SESLERİ YÜKLE ---
sound_enabled = True 

def load_sound(filename):
    try:
        if os.path.exists(filename):
            return pygame.mixer.Sound(filename)
    except: pass
    return None

fx_zipla = load_sound("zipla.wav")
fx_puan = load_sound("puan.wav")
fx_yanma = load_sound("yanma.wav")
fx_buton = load_sound("buton.wav")

def ses_cal(sound_obj):
    if sound_enabled and sound_obj:
        sound_obj.play()

# --- FONT ---
FONT_URL = "https://github.com/SzymonL/Minecraft-font/raw/master/Minecraft-Regular.otf"
FONT_DOSYA_ADI = "Minecraft-Regular.otf"
def font_yukle(boyut):
    try:
        if not os.path.exists(FONT_DOSYA_ADI):
            try: urllib.request.urlretrieve(FONT_URL, FONT_DOSYA_ADI)
            except: pass
        if os.path.exists(FONT_DOSYA_ADI): return pygame.font.Font(FONT_DOSYA_ADI, boyut)
        else: return pygame.font.SysFont('monospace', int(boyut*0.8), bold=True)
    except: return pygame.font.SysFont('arial', boyut, bold=True)

font_skor = font_yukle(int(V_H * 0.08))
font_mesaj = font_yukle(int(V_H * 0.12))
font_imza = font_yukle(int(V_H * 0.05))
font_versiyon = font_yukle(int(V_H * 0.04))
font_baslik = font_yukle(int(V_H * 0.15)) 
font_buton = font_yukle(int(V_H * 0.08)) 
font_rekorlar = font_yukle(int(V_H * 0.035))
font_splash = font_yukle(int(V_H * 0.12))
font_info = font_yukle(int(V_H * 0.035))
font_ui = font_yukle(int(V_H * 0.07)) 

# --- REKOR SİSTEMİ ---
REKOR_DOSYASI = "rekorlar.json"
varsayilan_rekorlar = {"KOLAY": 0, "ORTA": 0, "ZOR": 0}

def rekorlari_yukle():
    try:
        if os.path.exists(REKOR_DOSYASI):
            with open(REKOR_DOSYASI, "r") as f: return json.load(f)
    except: pass
    return varsayilan_rekorlar.copy()

def rekor_kaydet(zorluk, skor):
    global rekorlar_dict
    if skor > rekorlar_dict[zorluk]:
        rekorlar_dict[zorluk] = skor
        try:
            with open(REKOR_DOSYASI, "w") as f: json.dump(rekorlar_dict, f)
        except: pass

rekorlar_dict = rekorlari_yukle()

# --- ZORLUK AYARLARI ---
DIFFICULTY_SETTINGS = {
    "KOLAY": { "hiz_baslangic": V_W * 0.008, "hiz_artis": V_W * 0.0002, "max_hiz": V_W * 0.025, "yazi_renk": (100, 255, 100) },
    "ORTA": { "hiz_baslangic": V_W * 0.012, "hiz_artis": V_W * 0.0003, "max_hiz": V_W * 0.04, "yazi_renk": (255, 255, 100) },
    "ZOR": { "hiz_baslangic": V_W * 0.016, "hiz_artis": V_W * 0.0006, "max_hiz": float('inf'), "yazi_renk": (255, 100, 100) }
}
aktif_zorluk_adi = "ORTA"
aktif_hiz_ayarlari = DIFFICULTY_SETTINGS[aktif_zorluk_adi]

# --- YARDIMCI FONKSİYONLAR ---
def pixel_resim_olustur(grid, palet, scale):
    genislik = len(grid[0]) * scale
    yukseklik = len(grid) * scale
    surface = pygame.Surface((genislik, yukseklik), pygame.SRCALPHA)
    for r, satir in enumerate(grid):
        for c, renk_kodu in enumerate(satir):
            if renk_kodu != 0:
                renk = palet[renk_kodu]
                rect = (c * scale, r * scale, scale, scale)
                pygame.draw.rect(surface, renk, rect)
    return surface.convert_alpha()

def renk_gecisi(renk1, renk2, oran):
    r = int(renk1[0] + (renk2[0] - renk1[0]) * oran)
    g = int(renk1[1] + (renk2[1] - renk1[1]) * oran)
    b = int(renk1[2] + (renk2[2] - renk1[2]) * oran)
    return (r, g, b)

def golgeli_yazi(text, font, renk, golge_renk):
    yazi = font.render(text, False, renk)
    golge = font.render(text, False, golge_renk)
    return yazi, golge

def load_external_image(filename, target_height=None):
    try:
        if os.path.exists(filename):
            img = pygame.image.load(filename).convert_alpha()
            if target_height:
                aspect_ratio = img.get_width() / img.get_height()
                new_h = int(target_height)
                new_w = int(new_h * aspect_ratio)
                img = pygame.transform.smoothscale(img, (new_w, new_h))
            return img
        else:
            print(f"UYARI: {filename} bulunamadı!")
            fallback = pygame.Surface((32, 32))
            fallback.fill((255, 0, 255)) 
            return fallback
    except Exception as e:
        print(f"Hata: {e}")
        return pygame.Surface((32, 32))

# --- UI ÇİZİM ---
def draw_settings_icon(surface, rect, color):
    cx, cy = rect.center
    radius = rect.width // 4
    for i in range(0, 360, 45):
        vec = pygame.math.Vector2(0, -radius - 4).rotate(i)
        end_pos = (cx + int(vec.x), cy + int(vec.y))
        pygame.draw.line(surface, color, (cx, cy), end_pos, 4)
    pygame.draw.circle(surface, color, (cx, cy), radius)
    pygame.draw.circle(surface, (150, 150, 150), (cx, cy), radius // 2)

def draw_quit_icon(surface, rect, color):
    margin = rect.width // 4
    pygame.draw.line(surface, color, (rect.left + margin, rect.top + margin), (rect.right - margin, rect.bottom - margin), 4)
    pygame.draw.line(surface, color, (rect.right - margin, rect.top + margin), (rect.left + margin, rect.bottom - margin), 4)

def draw_hamburger_icon(surface, rect, color):
    margin_x = rect.width // 4
    margin_y = rect.height // 4
    gap = (rect.height - 2 * margin_y) // 2
    pygame.draw.line(surface, color, (rect.left + margin_x, rect.top + margin_y), (rect.right - margin_x, rect.top + margin_y), 3)
    pygame.draw.line(surface, color, (rect.left + margin_x, rect.centery), (rect.right - margin_x, rect.centery), 3)
    pygame.draw.line(surface, color, (rect.left + margin_x, rect.bottom - margin_y), (rect.right - margin_x, rect.bottom - margin_y), 3)

# --- GRAFİKLER ---

# 1. Dosyadan Yüklenenler
gunes_surface = load_external_image("gunes.png", target_height=70)
direk_surface = load_external_image("direk.png", target_height=130)
# HATA DÜZELTME: Arka plan için büyük lamba tanımı eklendi
lamba_bg_surface = load_external_image("lamba.png", target_height=130) 

# 2. Kodla Çizilenler

# Çit Feneri (Kodla)
fener_grid = [[0,1,1,0],[1,2,2,1],[1,2,2,1],[0,1,1,0]]
fener_palet = {1:(50,50,50), 2:G_SARI_PARLAK}
fener_surface = pixel_resim_olustur(fener_grid, fener_palet, PIXEL_SIZE)

ay_grid = [[0,0,0,1,1,0,0],[0,0,1,2,2,1,0],[0,1,2,2,2,2,1],[0,1,2,2,2,2,1],[0,1,2,2,2,2,1],[0,0,1,2,2,1,0],[0,0,0,1,1,0,0]]
ay_palet = {1:AY_GOLGESI, 2:AY_BEYAZI}
ay_surface = pixel_resim_olustur(ay_grid, ay_palet, PIXEL_SIZE * 3)

kus_grid = [[0,0,0,0,0,1,0],[0,0,0,0,1,1,0],[1,0,0,1,1,0,0],[0,1,1,1,0,0,0],[0,0,0,0,0,0,0]]
kus_palet = {1: (40, 40, 60)}
kus_surface = pixel_resim_olustur(kus_grid, kus_palet, PIXEL_SIZE)

su_grid = [[0,1,1,1,1,0],[1,2,2,3,2,1],[1,2,3,3,2,1],[0,1,1,1,1,0]]
su_palet = {1:(100,150,200), 2:(100,180,255), 3:BEYAZ}
su_surface = pixel_resim_olustur(su_grid, su_palet, PIXEL_SIZE * 2)

tavuk_grid_dur = [[0,0,0,0,1,1,1,1,1,0,0,0],[0,0,0,1,4,4,4,4,1,0,0,0],[0,0,0,1,4,4,4,4,1,1,0,0],[0,0,1,1,1,1,1,1,1,5,1,0],[0,1,2,2,2,1,2,2,1,5,5,1],[1,3,2,2,2,1,1,1,4,1,1,0],[1,3,2,2,2,3,3,1,4,1,0,0],[1,3,3,3,3,3,3,1,1,1,0,0],[1,1,3,3,3,3,1,1,0,0,0,0],[0,1,1,1,1,1,1,0,0,0,0,0],[0,0,0,1,6,1,1,6,1,0,0,0],[0,0,0,1,6,1,1,6,1,0,0,0]]
tavuk_grid_kos = [[0,0,0,0,1,1,1,1,1,0,0,0],[0,0,0,1,4,4,4,4,1,0,0,0],[0,0,0,1,4,4,4,4,1,1,0,0],[0,0,1,1,1,1,1,1,1,5,1,0],[0,1,2,2,2,1,2,2,1,5,5,1],[1,3,2,2,2,1,1,1,4,1,1,0],[1,3,2,2,2,3,3,1,4,1,0,0],[1,3,3,3,3,3,3,1,1,1,0,0],[1,1,3,3,3,3,1,1,0,0,0,0],[0,1,1,1,1,1,1,0,0,0,0,0],[0,0,1,6,1,0,1,6,1,0,0,0],[0,0,1,6,1,0,1,6,1,0,0,0]]
tavuk_palet = {1:T_SIYAH, 2:T_BEYAZ, 3:T_MAVI_GOLGE, 4:T_KIRMIZI, 5:T_SARI, 6:T_TURUNCU}
tavuk_surface_dur = pixel_resim_olustur(tavuk_grid_dur, tavuk_palet, PIXEL_SIZE)
tavuk_surface_kos = pixel_resim_olustur(tavuk_grid_kos, tavuk_palet, PIXEL_SIZE)
tavuk_splash = pixel_resim_olustur(tavuk_grid_dur, tavuk_palet, PIXEL_SIZE * 3)

cit_grid = [[0,1,1,1,0,1,1,1,0,1,1,1,0],[0,1,4,1,0,1,4,1,0,1,4,1,0],[1,1,2,1,1,1,2,1,1,1,2,1,1],[1,4,3,3,3,3,3,3,3,3,3,4,1],[1,1,2,1,1,1,2,1,1,1,2,1,1],[0,1,2,1,0,1,2,1,0,1,2,1,0],[0,1,2,1,0,1,2,1,0,1,2,1,0],[0,1,2,1,0,1,2,1,0,1,2,1,0],[0,1,2,1,0,1,2,1,0,1,2,1,0],[0,1,2,1,0,1,2,1,0,1,2,1,0],[1,1,1,1,1,1,1,1,1,1,1,1,1],[1,4,3,3,3,3,3,3,3,3,3,4,1],[1,2,2,2,2,2,2,2,2,2,2,2,1],[1,1,1,1,1,1,1,1,1,1,1,1,1]]
cit_palet = {1:C_SIYAH, 2:C_KOYU_KAHVE, 3:C_ORTA_KAHVE, 4:C_ACIK_KAHVE}
cit_surface = pixel_resim_olustur(cit_grid, cit_palet, PIXEL_SIZE)

bulut_palet = {1:BULUT_BEYAZI, 2:BULUT_GOLGESI}
bg1 = [[0,0,1,1,1,1,0,0,0,0],[0,1,1,1,1,1,1,0,0,0],[1,1,1,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1,1,1],[1,1,1,2,2,1,1,1,2,2],[1,1,2,2,2,2,1,2,2,2],[0,1,2,2,2,2,1,2,2,2],[0,0,1,2,2,2,1,2,2,0]]
bg2 = [[0,0,0,0,1,1,1,1,0,0,0,0,0,0],[0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,1,1,1,1,1,1,1,1,1,1,1,0,0],[1,1,1,1,1,1,1,1,1,1,1,1,1,0],[1,1,1,1,1,1,1,1,2,2,1,1,1,1],[1,1,1,2,2,2,2,2,2,2,2,1,2,2],[0,1,2,2,2,2,2,2,2,2,2,2,2,0],[0,0,1,2,2,2,1,1,2,2,2,2,0,0]]
bg3 = [[0,0,1,1,1,0,0],[0,1,1,1,1,1,0],[1,1,1,1,1,1,1],[1,1,1,2,2,1,1],[0,1,2,2,2,2,1],[0,0,1,2,2,1,0]]
bulut_resimleri = [pixel_resim_olustur(bg1, bulut_palet, PIXEL_SIZE * 1.5), pixel_resim_olustur(bg2, bulut_palet, PIXEL_SIZE * 1.5), pixel_resim_olustur(bg3, bulut_palet, PIXEL_SIZE * 1.5)]

# --- ZEMİN (STATİK) ---
zemin_surface = pygame.Surface((V_W, int(zemin_yukseklik))).convert_alpha()
cim_kalinlik = int(zemin_yukseklik * 0.3)
for y in range(cim_kalinlik, int(zemin_yukseklik), PIXEL_SIZE):
    for x in range(0, V_W, PIXEL_SIZE):
        renk = Z_TOPRAK_UST
        ratio = (y - cim_kalinlik) / (zemin_yukseklik - cim_kalinlik)
        if ratio > 0.3: renk = Z_TOPRAK_ORTA
        if ratio > 0.7: renk = Z_TOPRAK_ALT
        if random.random() < 0.15: renk = Z_TOPRAK_ALT
        pygame.draw.rect(zemin_surface, renk, (x, y, PIXEL_SIZE, PIXEL_SIZE))
pygame.draw.rect(zemin_surface, Z_CIM_TABAN, (0, 0, V_W, cim_kalinlik))
for x in range(0, V_W, PIXEL_SIZE):
    h = random.randint(int(PIXEL_SIZE*2), int(PIXEL_SIZE*5))
    renk = random.choice([Z_CIM_TEL_1, Z_CIM_TEL_2])
    pygame.draw.rect(zemin_surface, renk, (x, cim_kalinlik - h, PIXEL_SIZE, h))

# --- GLOBAL DEĞİŞKENLER ---
game_state = "SPLASH" 
splash_timer = 0
splash_duration = 90

ham_mesajlar = ["Allah'ına Kurban!", "Vay Anasını!", "Bravo!", "Müthişsin!", "Sen nesin be!", "İnanılmaz!", "Helal!"]
hazir_mesajlar = [golgeli_yazi(m, font_mesaj, MESAJ_RENGI, SKOR_GOLGESI) for m in ham_mesajlar]
yandin_yazi, yandin_golge = golgeli_yazi("OYUN BİTTİ", font_mesaj, MESAJ_RENGI, SKOR_GOLGESI)
imza_yazi, imza_golge = golgeli_yazi("Yapımcı: ÖBS", font_imza, IMZA_RENGI, (50,0,0))
versiyon_yazi, versiyon_golge = golgeli_yazi("v0.8.2", font_versiyon, (100,100,100), (50,50,50))
baslik_yazi, baslik_golge = golgeli_yazi("Chicken Run", font_baslik, (255, 215, 0), (100, 50, 0))
splash_yazi, splash_golge = golgeli_yazi("ÖBS GAMES PRESENTS", font_splash, SPLASH_TEXT, BEYAZ)

# Butonlar
btn_w = int(V_W * 0.2)
btn_h = int(V_H * 0.15)
padding = 10
total_w = 3 * btn_w + 2 * padding
start_x = V_W // 2 - total_w // 2

btn_kolay_rect = pygame.Rect(start_x, V_H * 0.5, btn_w, btn_h)
btn_orta_rect = pygame.Rect(start_x + btn_w + padding, V_H * 0.5, btn_w, btn_h)
btn_zor_rect = pygame.Rect(start_x + 2 * (btn_w + padding), V_H * 0.5, btn_w, btn_h)

small_btn_size = int(V_H * 0.12)

btn_menu_quit_rect = pygame.Rect(10, 10, small_btn_size, small_btn_size)
btn_settings_rect = pygame.Rect(20 + small_btn_size, 10, small_btn_size, small_btn_size)

# Gameover
btn_width = int(V_W * 0.22)
btn_height = int(V_H * 0.15)
btn_restart_rect = pygame.Rect(V_W//2 - btn_width * 1.5 - 10, V_H//2 + 40, btn_width, btn_height)
btn_menu_rect = pygame.Rect(V_W//2 - btn_width // 2, V_H//2 + 40, btn_width, btn_height)
btn_quit_rect = pygame.Rect(V_W//2 + btn_width * 0.5 + 10, V_H//2 + 40, btn_width, btn_height)

# Ayarlar
settings_win_w = int(V_W * 0.6)
settings_win_h = int(V_H * 0.7)
settings_win_rect = pygame.Rect(V_W//2 - settings_win_w//2, V_H//2 - settings_win_h//2, settings_win_w, settings_win_h)
btn_settings_close_rect = pygame.Rect(settings_win_rect.centerx - btn_w//2, settings_win_rect.bottom - btn_h - 20, btn_w, btn_h)
checkbox_rect = pygame.Rect(settings_win_rect.centerx + 20, settings_win_rect.top + 60, 30, 30)

# Pause
pause_btn_rect = pygame.Rect(10, 10, small_btn_size, small_btn_size)
pause_win_w = int(V_W * 0.5)
pause_win_h = int(V_H * 0.5)
pause_win_rect = pygame.Rect(V_W//2 - pause_win_w//2, V_H//2 - pause_win_h//2, pause_win_w, pause_win_h)
btn_resume_rect = pygame.Rect(pause_win_rect.centerx - btn_w//2, pause_win_rect.top + 40, btn_w, btn_h)
btn_pause_menu_rect = pygame.Rect(pause_win_rect.centerx - btn_w//2, pause_win_rect.top + 40 + btn_h + 10, btn_w, btn_h)

# Değişkenler
tavuk_x = int(V_W * 0.1)
tavuk_y = 0
hiz_y = 0
cit_x = 0
cit_hizi = 0
max_hiz_siniri = 0
hiz_artis_miktari = 0
skor = 0
eski_skor = -1
yazi_skor_surface = None
yazi_skor_golge = None
mesaj_suresi = 0
aktif_mesaj = None
aktif_golge = None
aktif_rect = None
bulutlar = []
yildizlar = []
kuslar = [] 
sular = []
direkler = []
tavuk_animasyon_sayaci = 0
tavuk_animasyon_hizi = 8 
blink_timer = 0 

def oyunu_sifirla():
    global tavuk_y, hiz_y, cit_x, cit_hizi, skor, eski_skor, mesaj_suresi, bulutlar, yildizlar, max_hiz_siniri, hiz_artis_miktari, tavuk_animasyon_hizi, kuslar, sular, direkler
    tavuk_y = ZEMIN_SEVIYESI - tavuk_boyut
    hiz_y = 0
    cit_x = V_W + 100
    
    cit_hizi = aktif_hiz_ayarlari["hiz_baslangic"]
    max_hiz_siniri = aktif_hiz_ayarlari["max_hiz"]
    hiz_artis_miktari = aktif_hiz_ayarlari["hiz_artis"]
    
    tavuk_animasyon_hizi = max(4, int(8 / (cit_hizi / (V_W * 0.01))))
    
    skor = 0
    eski_skor = -1
    mesaj_suresi = 0
    
    bulutlar = []
    for i in range(5):
        bx = random.randint(0, V_W)
        by = random.randint(0, int(V_H * 0.4))
        bhiz = random.uniform(V_W*0.001, V_W*0.003)
        btip = random.choice(bulut_resimleri)
        bulutlar.append([bx, by, bhiz, btip])

    yildizlar = [[random.randint(0, V_W), random.randint(0, int(V_H*0.6))] for _ in range(30)]
    
    kuslar = []
    sular = []
    direkler = [] 

oyunu_sifirla()

# --- OYUN DÖNGÜSÜ ---
calisiyor = True
while calisiyor:
    # 1. GİRDİLER
    for event in pygame.event.get():
        if event.type == pygame.QUIT: calisiyor = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            current_w, current_h = real_screen.get_size()
            scale_x = current_w / V_W
            scale_y = current_h / V_H
            vmx = mx / scale_x
            vmy = my / scale_y

            if game_state == "SPLASH":
                game_state = "MENU"

            elif game_state == "MENU":
                secilen_zorluk = None
                if btn_kolay_rect.collidepoint(vmx, vmy): secilen_zorluk = "KOLAY"
                elif btn_orta_rect.collidepoint(vmx, vmy): secilen_zorluk = "ORTA"
                elif btn_zor_rect.collidepoint(vmx, vmy): secilen_zorluk = "ZOR"
                
                if secilen_zorluk:
                    aktif_zorluk_adi = secilen_zorluk
                    aktif_hiz_ayarlari = DIFFICULTY_SETTINGS[secilen_zorluk]
                    game_state = "PLAYING"
                    oyunu_sifirla()
                    ses_cal(fx_buton)
                
                # ÇIKIŞ VE AYARLAR
                if btn_menu_quit_rect.collidepoint(vmx, vmy):
                    pygame.quit()
                    sys.exit()
                if btn_settings_rect.collidepoint(vmx, vmy):
                    game_state = "SETTINGS"
                    ses_cal(fx_buton)

            elif game_state == "SETTINGS":
                if checkbox_rect.collidepoint(vmx, vmy):
                    sound_enabled = not sound_enabled
                    if not sound_enabled: pygame.mixer.stop()
                    else: ses_cal(fx_buton)
                
                if btn_settings_close_rect.collidepoint(vmx, vmy):
                    game_state = "MENU"
                    ses_cal(fx_buton)
                    
            elif game_state == "PLAYING":
                if pause_btn_rect.collidepoint(vmx, vmy):
                    game_state = "PAUSED"
                    ses_cal(fx_buton)
                elif tavuk_y >= ZEMIN_SEVIYESI - tavuk_boyut - 10:
                    hiz_y = ziplama_gucu
                    ses_cal(fx_zipla)
            
            elif game_state == "PAUSED":
                if btn_resume_rect.collidepoint(vmx, vmy):
                    game_state = "PLAYING"
                    ses_cal(fx_buton)
                elif btn_pause_menu_rect.collidepoint(vmx, vmy):
                    game_state = "MENU"
                    ses_cal(fx_buton)

            elif game_state == "GAMEOVER":
                if current_w > current_h: 
                    if btn_restart_rect.collidepoint(vmx, vmy):
                        game_state = "PLAYING"
                        oyunu_sifirla()
                        ses_cal(fx_buton)
                    elif btn_menu_rect.collidepoint(vmx, vmy):
                        game_state = "MENU"
                        ses_cal(fx_buton)
                    elif btn_quit_rect.collidepoint(vmx, vmy):
                        pygame.quit()
                        sys.exit()
                else:
                    game_state = "PLAYING"
                    oyunu_sifirla()
                    ses_cal(fx_buton)
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                if game_state == "PLAYING":
                    if tavuk_y >= ZEMIN_SEVIYESI - tavuk_boyut - 10:
                        hiz_y = ziplama_gucu
                        ses_cal(fx_zipla)
                elif game_state == "GAMEOVER":
                    game_state = "PLAYING"
                    oyunu_sifirla()
                    ses_cal(fx_buton)
            
            if event.key == pygame.K_ESCAPE:
                if game_state == "PLAYING":
                    game_state = "PAUSED"
                elif game_state == "PAUSED" or game_state == "SETTINGS":
                    game_state = "MENU"

    # 2. FİZİK & MANTIK
    if game_state == "SPLASH":
        splash_timer += 1
        if splash_timer > splash_duration:
            game_state = "MENU"

    if game_state == "PLAYING":
        hiz_y += yer_cekimi
        tavuk_y += hiz_y
        yerde = False
        if tavuk_y >= ZEMIN_SEVIYESI - tavuk_boyut:
            tavuk_y = ZEMIN_SEVIYESI - tavuk_boyut
            hiz_y = 0
            yerde = True

        cit_x -= cit_hizi
        
        if random.randint(0, 600) == 1:
            sular.append([V_W + 50, ZEMIN_SEVIYESI - PIXEL_SIZE*2])
        
        if random.randint(0, 400) == 1: 
            kus_y = random.randint(10, int(V_H * 0.4))
            kuslar.append([V_W + 50, kus_y])

        # Direk spawn
        last_x = -999
        if direkler: last_x = direkler[-1][0]
        if V_W - last_x > 200: 
            if random.randint(0, 150) == 1: 
                # Direk tipi (gündüz mü gece mi spawn oldu)
                # 0: Direk, 1: Lamba
                # Artık çizim sırasında kontrol ediliyor, sadece koordinat
                # Ancak gece/gündüz geçişini obje bazlı tutmak daha iyi
                is_night_spawn = False
                # Skorun neresindeyiz?
                mod_skor_anlik = skor % 10000
                if mod_skor_anlik > 4500 and mod_skor_anlik < 9000:
                     is_night_spawn = True
                direkler.append([V_W + 50, ZEMIN_SEVIYESI, is_night_spawn])

        if cit_x < -cit_genislik:
            cit_x = V_W + random.randint(int(V_W*0.2), int(V_W*0.6))
            skor += 100
            
            if cit_hizi < max_hiz_siniri: cit_hizi += hiz_artis_miktari
            tavuk_animasyon_hizi = max(4, int(8 / (cit_hizi / (V_W * 0.01))))
            
            if skor > 0 and skor % 500 == 0:
                aktif_mesaj, aktif_golge = random.choice(hazir_mesajlar)
                aktif_rect = aktif_mesaj.get_rect(center=(V_W/2, V_H/3))
                mesaj_suresi = 40
                ses_cal(fx_puan)

        if skor != eski_skor:
            yazi_skor_surface, yazi_skor_golge = golgeli_yazi(f"Skor: {skor}", font_skor, SIYAH, (200,200,200))
            eski_skor = skor

        t_rect = pygame.Rect(tavuk_x + PIXEL_SIZE, tavuk_y + PIXEL_SIZE, tavuk_boyut - PIXEL_SIZE*2, tavuk_boyut - PIXEL_SIZE)
        c_rect = pygame.Rect(cit_x + PIXEL_SIZE, ZEMIN_SEVIYESI - cit_yukseklik + PIXEL_SIZE, cit_genislik - PIXEL_SIZE*2, cit_yukseklik - PIXEL_SIZE)

        if t_rect.colliderect(c_rect):
            game_state = "GAMEOVER"
            rekor_kaydet(aktif_zorluk_adi, skor)
            ses_cal(fx_yanma)

    # GÜN DÖNGÜSÜ
    render_skor = skor
    if game_state == "MENU" or game_state == "SPLASH" or game_state == "SETTINGS": render_skor = 2000

    mod_skor = render_skor % 10000 
    gece_oluyor = False
    gece_modu = False
    gok_rengi = GOK_GUNDUZ
    gunes_y = int(V_H*0.05)
    ay_x = V_W + 100
    ay_y = int(V_H*0.05)

    if mod_skor < 4000:
        oran = mod_skor / 4000
        gunes_x = (V_W - gunes_surface.get_width() - 20) - (V_W * 0.8) * oran
    elif 4000 <= mod_skor < 5000:
        gece_oluyor = True
        oran = (mod_skor - 4000) / 1000
        gok_rengi = renk_gecisi(GOK_GUNDUZ, GOK_AKSAM, oran)
        if oran > 0.5: gok_rengi = renk_gecisi(GOK_AKSAM, GOK_GECE, (oran-0.5)*2)
        gunes_x = int(V_W * 0.1)
        gunes_y = int(V_H*0.05) + int(V_H * oran)
        ay_x = V_W + 50 - (V_W * 0.2) * oran
        ay_y = V_H - (V_H * 0.9) * oran
    elif 5000 <= mod_skor < 9000:
        gece_modu = True
        gok_rengi = GOK_GECE
        gunes_y = V_H + 100
        oran = (mod_skor - 5000) / 4000
        ay_start_x = V_W - ay_surface.get_width() - int(V_W*0.05)
        ay_end_x = int(V_W * 0.1)
        ay_x = ay_start_x - (ay_start_x - ay_end_x) * oran
        ay_y = int(V_H*0.05)
    else:
        gece_oluyor = True 
        oran = (mod_skor - 9000) / 1000
        gok_rengi = renk_gecisi(GOK_GECE, GOK_GUNDUZ, oran)
        ay_x = int(V_W * 0.1)
        ay_y = int(V_H*0.05) + int(V_H * oran)
        gunes_x = V_W + 50 - (V_W * 0.2) * oran
        gunes_y = V_H - (V_H * 0.95) * oran

    # 3. ÇİZİM
    if game_state == "SPLASH":
        canvas.fill(SPLASH_BG)
        for _ in range(20):
            rx = random.randint(0, V_W)
            ry = random.randint(0, V_H)
            rc = (random.randint(200,255), random.randint(150,220), random.randint(0,100))
            pygame.draw.rect(canvas, rc, (rx, ry, 4, 4))
        splash_rect = splash_yazi.get_rect(center=(V_W//2, V_H//2 - 30))
        tavuk_splash_rect = tavuk_splash.get_rect(center=(V_W//2, V_H//2 + 30))
        canvas.blit(splash_yazi, splash_rect)
        canvas.blit(tavuk_splash, tavuk_splash_rect)
        
    else: # OYUN EKRANI
        canvas.fill(gok_rengi)

        if gece_oluyor or gece_modu:
            for yz in yildizlar: pygame.draw.rect(canvas, YILDIZ_RENGI, (yz[0], yz[1], 2, 2))

        if gunes_y < V_H + 50:
            canvas.blit(gunes_surface, (int(gunes_x), int(gunes_y)))
        if ay_x < V_W + 50:
            canvas.blit(ay_surface, (int(ay_x), int(ay_y)))

        for b in bulutlar:
            b[0] -= b[2]
            if gece_modu or (gece_oluyor and mod_skor > 4500): b[1] += V_H * 0.005
            if b[0] < -b[3].get_width() and mod_skor < 4000:
                b[0] = V_W + random.randint(0, 100)
                b[1] = random.randint(0, int(V_H * 0.4))
                b[3] = random.choice(bulut_resimleri)
            canvas.blit(b[3], (int(b[0]), int(b[1])))
        
        # DİREKLER / LAMBALAR
        for obj in direkler:
            obj[0] -= cit_hizi * 0.8 
            
            if obj[2]: # Gece objesi (LAMBA)
                lamba_y = obj[1] - lamba_bg_surface.get_height() + PIXEL_SIZE * 4
                canvas.blit(lamba_bg_surface, (int(obj[0]), int(lamba_y)))
            else: # Gündüz objesi (DİREK)
                direk_y = obj[1] - direk_surface.get_height()
                canvas.blit(direk_surface, (int(obj[0]), int(direk_y)))

        direkler = [d for d in direkler if d[0] > -200]

        for kus in kuslar:
            kus[0] -= cit_hizi * 0.5
            canvas.blit(kus_surface, (int(kus[0]), int(kus[1])))
        kuslar = [k for k in kuslar if k[0] > -20]

        canvas.blit(zemin_surface, (0, ZEMIN_SEVIYESI))
        
        for su in sular:
            su[0] -= cit_hizi 
            canvas.blit(su_surface, (int(su[0]), int(su[1])))
        sular = [s for s in sular if s[0] > -50]

        canvas.blit(cit_surface, (cit_x, ZEMIN_SEVIYESI - cit_yukseklik))
        if gece_modu or gece_oluyor:
            # Fener (Glow yok)
            canvas.blit(fener_surface, (cit_x + PIXEL_SIZE*4, ZEMIN_SEVIYESI - cit_yukseklik - PIXEL_SIZE*2))
        
        if game_state == "MENU":
            blink_timer += 1
            canvas.blit(baslik_golge, (V_W//2 - baslik_yazi.get_width()//2 + 4, V_H*0.2 + 4))
            canvas.blit(baslik_yazi, (V_W//2 - baslik_yazi.get_width()//2, V_H*0.2))
            
            r_y = V_H * 0.88
            for i, (zorluk, val) in enumerate(rekorlar_dict.items()):
                txt = f"{zorluk}: {val}"
                r_surf, _ = golgeli_yazi(txt, font_rekorlar, T_SARI, SKOR_GOLGESI)
                r_x = (V_W // 3) * i + (V_W // 6) - r_surf.get_width() // 2
                canvas.blit(r_surf, (r_x, r_y))

            for zorluk, rect in [("KOLAY", btn_kolay_rect), ("ORTA", btn_orta_rect), ("ZOR", btn_zor_rect)]:
                renk = DIFFICULTY_SETTINGS[zorluk]["yazi_renk"]
                pygame.draw.rect(canvas, renk, rect, border_radius=5)
                pygame.draw.rect(canvas, T_SIYAH, rect, 4, border_radius=5)
                yazi, _ = golgeli_yazi(zorluk, font_buton, T_SIYAH, BEYAZ)
                yazi_rect = yazi.get_rect(center=rect.center)
                canvas.blit(yazi, yazi_rect)
            
            pygame.draw.rect(canvas, BTN_KIRMIZI, btn_menu_quit_rect, border_radius=5)
            pygame.draw.rect(canvas, T_SIYAH, btn_menu_quit_rect, 2, border_radius=5)
            draw_quit_icon(canvas, btn_menu_quit_rect, T_SIYAH)

            pygame.draw.rect(canvas, UI_GREY, btn_settings_rect, border_radius=5)
            pygame.draw.rect(canvas, T_SIYAH, btn_settings_rect, 2, border_radius=5)
            draw_settings_icon(canvas, btn_settings_rect, T_SIYAH)

        elif game_state == "SETTINGS":
            overlay = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
            overlay.fill(OVERLAY_RENK)
            canvas.blit(overlay, (0,0))

            pygame.draw.rect(canvas, UI_GOLD, settings_win_rect, border_radius=10)
            pygame.draw.rect(canvas, UI_BORDER, settings_win_rect, 4, border_radius=10)

            ses_txt, _ = golgeli_yazi("SES:", font_ui, T_SIYAH, BEYAZ)
            canvas.blit(ses_txt, (settings_win_rect.centerx - 50, settings_win_rect.top + 60))

            pygame.draw.rect(canvas, T_BEYAZ, checkbox_rect)
            pygame.draw.rect(canvas, T_SIYAH, checkbox_rect, 2)
            if sound_enabled:
                pygame.draw.rect(canvas, T_SIYAH, (checkbox_rect.x + 5, checkbox_rect.y + 5, 20, 20))

            canvas.blit(imza_golge, (settings_win_rect.centerx - imza_yazi.get_width()//2 + 2, settings_win_rect.bottom - 100))
            canvas.blit(imza_yazi, (settings_win_rect.centerx - imza_yazi.get_width()//2, settings_win_rect.bottom - 102))

            pygame.draw.rect(canvas, C_ACIK_KAHVE, btn_settings_close_rect, border_radius=5)
            pygame.draw.rect(canvas, T_SIYAH, btn_settings_close_rect, 2, border_radius=5)
            close_txt, _ = golgeli_yazi("KAPAT", font_buton, T_SIYAH, BEYAZ)
            close_rect = close_txt.get_rect(center=btn_settings_close_rect.center)
            canvas.blit(close_txt, close_rect)
                
        elif game_state == "PLAYING":
            if yerde:
                tavuk_animasyon_sayaci += 1
                aktif_tavuk = tavuk_surface_dur if (tavuk_animasyon_sayaci // tavuk_animasyon_hizi) % 2 == 0 else tavuk_surface_kos
            else:
                aktif_tavuk = tavuk_surface_dur
            canvas.blit(aktif_tavuk, (tavuk_x, tavuk_y))

            # Pause Butonu
            pygame.draw.rect(canvas, UI_GOLD, pause_btn_rect, border_radius=5)
            pygame.draw.rect(canvas, UI_BORDER, pause_btn_rect, 2, border_radius=5)
            draw_hamburger_icon(canvas, pause_btn_rect, T_SIYAH)

            # Skor (Pause'un sağında)
            if yazi_skor_surface:
                skor_x = pause_btn_rect.right + 10
                canvas.blit(yazi_skor_golge, (skor_x + 1, 11))
                canvas.blit(yazi_skor_surface, (skor_x, 10))
            
            # Bilgi (Sağ Üst)
            info_txt = f"MOD: {aktif_zorluk_adi} | REKOR: {rekorlar_dict[aktif_zorluk_adi]}"
            info_surf, info_golge = golgeli_yazi(info_txt, font_info, BEYAZ, SKOR_GOLGESI)
            info_x = V_W - info_surf.get_width() - 10
            canvas.blit(info_golge, (info_x+1, 31))
            canvas.blit(info_surf, (info_x, 30))

            # Yapımcı İmzasını Geri Ekle
            imza_x = V_W - imza_yazi.get_width() - 10
            canvas.blit(imza_golge, (imza_x+1, 11)) 
            canvas.blit(imza_yazi, (imza_x, 10))
            
            if mesaj_suresi > 0 and aktif_mesaj:
                canvas.blit(aktif_golge, (aktif_rect.x+2, aktif_rect.y+2))
                canvas.blit(aktif_mesaj, aktif_rect)
                mesaj_suresi -= 1

        elif game_state == "PAUSED":
            canvas.blit(cit_surface, (cit_x, ZEMIN_SEVIYESI - cit_yukseklik))
            canvas.blit(tavuk_surface_dur, (tavuk_x, tavuk_y))

            overlay = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
            overlay.fill(OVERLAY_RENK)
            canvas.blit(overlay, (0,0))

            pygame.draw.rect(canvas, UI_GOLD, pause_win_rect, border_radius=10)
            pygame.draw.rect(canvas, UI_BORDER, pause_win_rect, 4, border_radius=10)

            pause_title, _ = golgeli_yazi("DURAKLATILDI", font_mesaj, T_SIYAH, BEYAZ)
            title_rect = pause_title.get_rect(center=(pause_win_rect.centerx, pause_win_rect.top + 40))
            canvas.blit(pause_title, title_rect)

            pygame.draw.rect(canvas, BTN_YESIL, btn_resume_rect, border_radius=5)
            pygame.draw.rect(canvas, T_SIYAH, btn_resume_rect, 2, border_radius=5)
            res_txt, _ = golgeli_yazi("DEVAM ET", font_buton, T_SIYAH, BEYAZ)
            res_r = res_txt.get_rect(center=btn_resume_rect.center)
            canvas.blit(res_txt, res_r)

            pygame.draw.rect(canvas, BTN_KIRMIZI, btn_pause_menu_rect, border_radius=5)
            pygame.draw.rect(canvas, T_SIYAH, btn_pause_menu_rect, 2, border_radius=5)
            pm_txt, _ = golgeli_yazi("MENUYE DON", font_buton, T_SIYAH, BEYAZ)
            pm_r = pm_txt.get_rect(center=btn_pause_menu_rect.center)
            canvas.blit(pm_txt, pm_r)

        elif game_state == "GAMEOVER":
            canvas.blit(cit_surface, (cit_x, ZEMIN_SEVIYESI - cit_yukseklik))
            canvas.blit(tavuk_surface_dur, (tavuk_x, tavuk_y))
            
            overlay = pygame.Surface((V_W, V_H), pygame.SRCALPHA)
            overlay.fill(OVERLAY_RENK)
            canvas.blit(overlay, (0,0))
            
            canvas.blit(yandin_golge, (V_W//2 - yandin_yazi.get_width()//2 + 4, V_H*0.2 + 4))
            canvas.blit(yandin_yazi, (V_W//2 - yandin_yazi.get_width()//2, V_H*0.2))
            
            final_skor, final_golge = golgeli_yazi(f"Skor: {skor}", font_mesaj, T_SARI, SKOR_GOLGESI)
            canvas.blit(final_golge, (V_W//2 - final_skor.get_width()//2 + 2, V_H*0.35 + 2))
            canvas.blit(final_skor, (V_W//2 - final_skor.get_width()//2, V_H*0.35))
            
            current_best = rekorlar_dict[aktif_zorluk_adi]
            rekor_txt, rekor_glg = golgeli_yazi(f"REKOR ({aktif_zorluk_adi}): {current_best}", font_imza, G_SARI_PARLAK, SKOR_GOLGESI)
            canvas.blit(rekor_glg, (V_W//2 - rekor_txt.get_width()//2 + 2, V_H*0.45 + 2))
            canvas.blit(rekor_txt, (V_W//2 - rekor_txt.get_width()//2, V_H*0.45))

            pygame.draw.rect(canvas, C_ACIK_KAHVE, btn_restart_rect)
            pygame.draw.rect(canvas, T_BEYAZ, btn_restart_rect, 2)
            yazi_tekrar, _ = golgeli_yazi("TEKRAR DENE", font_versiyon, SIYAH, SIYAH)
            tr_rect = yazi_tekrar.get_rect(center=btn_restart_rect.center)
            canvas.blit(yazi_tekrar, tr_rect)
            
            pygame.draw.rect(canvas, C_KOYU_KAHVE, btn_menu_rect)
            pygame.draw.rect(canvas, T_BEYAZ, btn_menu_rect, 2)
            yazi_menu, _ = golgeli_yazi("MENU", font_versiyon, T_BEYAZ, SIYAH)
            tm_rect = yazi_menu.get_rect(center=btn_menu_rect.center)
            canvas.blit(yazi_menu, tm_rect)

            pygame.draw.rect(canvas, BTN_CIKIS_RENK, btn_quit_rect)
            pygame.draw.rect(canvas, T_BEYAZ, btn_quit_rect, 2)
            yazi_quit, _ = golgeli_yazi("CIKIS", font_versiyon, T_BEYAZ, SIYAH)
            q_rect = yazi_quit.get_rect(center=btn_quit_rect.center)
            canvas.blit(yazi_quit, q_rect)

        if game_state != "SPLASH" and game_state != "SETTINGS" and game_state != "PAUSED":
            canvas.blit(versiyon_yazi, (5, V_H - 20))

    # 4. EKRANA BASMA
    screen_w, screen_h = real_screen.get_size()
    if screen_w < screen_h: # DİK TUTUŞ
        rotated = pygame.transform.rotate(canvas, 90)
        scaled = pygame.transform.scale(rotated, (screen_w, screen_h))
    else: # YAN TUTUŞ
        scaled = pygame.transform.scale(canvas, (screen_w, screen_h))
    real_screen.blit(scaled, (0, 0))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
