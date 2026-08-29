#!/usr/bin/env python3
"""生成逼真银河系俯视图 (参照真实银河系照片风格)
特征: 中心亮黄色核球, 旋臂淡蓝白(年轻恒星), 暗尘埃带(棕色), 大量星点
"""
from PIL import Image, ImageDraw, ImageFilter
import math, random

W, H = 1920, 1200
CX, CY = W // 2, H // 2
MAX_R = min(W, H) // 2 - 40

img = Image.new('RGB', (W, H), (3, 5, 14))
draw = ImageDraw.Draw(img, 'RGBA')
random.seed(7)

# ── 背景星空 (真实照片风格: 白点带轻微蓝色) ──
for _ in range(1800):
    x, y = random.randint(0, W-1), random.randint(0, H-1)
    b = random.randint(80, 220)
    bl = random.randint(max(0, b-40), b)
    r = random.choice([1, 1, 1, 1, 2])
    draw.ellipse([x, y, x+r, y+r], fill=(b, bl, min(255, bl+10), 255))

# ── 星系盘基础亮度 (径向指数衰减 + 噪声) ──
base = Image.new('L', (W, H), 0)
bdraw = ImageDraw.Draw(base)
for _ in range(90000):
    # 指数分布: 中心密集
    t = random.random()
    r = MAX_R * (-math.log(1 - t * 0.985)) / 4.2
    if r > MAX_R: continue
    a = random.uniform(0, 2 * math.pi)
    # 椭圆压缩 (0.42)
    x = CX + r * math.cos(a)
    y = CY + r * math.sin(a) * 0.42
    if 0 <= x < W and 0 <= y < H:
        # 中心更亮
        bright = max(1, int(150 * math.exp(-r / (MAX_R * 0.30))))
        bdraw.point((int(x), int(y)), bright)
base = base.filter(ImageFilter.GaussianBlur(6))
draw = ImageDraw.Draw(img, 'RGBA')

# ── 旋臂 (淡蓝白色, 对数螺旋, 更像真实) ──
def spiral_arm(angle0, color, width_factor=1.0):
    pts = []
    for i in range(260):
        t = i / 260
        r = MAX_R * (0.10 + t * 0.92)
        # 对数螺旋: theta = a * ln(r/r0)
        theta = angle0 + 2.6 * math.log(1 + t * 9)
        x = CX + r * math.cos(theta)
        y = CY + r * math.sin(theta) * 0.42
        pts.append((x, y))
    draw.line(pts, fill=color, width=int(14 * width_factor), joint='curve')

# 两条主臂 (银河系主要是2条主臂 + 附属臂)
spiral_arm(0,       (170, 190, 215, 26))
spiral_arm(math.pi, (170, 190, 215, 26))
spiral_arm(0.9,     (150, 175, 205, 16))
spiral_arm(0.9 + math.pi, (150, 175, 205, 16))

# ── 暗尘埃带 (棕色丝带, 沿旋臂边缘) ──
def dust_band(angle0, offset=0.25):
    pts = []
    for i in range(200):
        t = i / 200
        r = MAX_R * (0.22 + t * 0.75)
        theta = angle0 + 2.6 * math.log(1 + t * 9) + offset
        x = CX + r * math.cos(theta)
        y = CY + r * math.sin(theta) * 0.42
        pts.append((x, y))
    draw.line(pts, fill=(60, 45, 35, 40), width=10, joint='curve')
dust_band(0.35)
dust_band(0.35 + math.pi)
dust_band(1.25)
dust_band(1.25 + math.pi)

# ── 银河系棒 (略亮黄, 中央质量聚集) ──
bar_half = MAX_R * 0.35
bar_w = MAX_R * 0.05
# 棒本身: 中间亮黄, 两端过渡到冷蓝
for dx in range(-int(bar_half), int(bar_half)):
    t = abs(dx) / bar_half
    # 中心偏黄, 两端偏暖棕
    if t < 0.4:
        col = (220, 200, 160, int(40 * (1 - t * 0.5)))
    else:
        col = (180, 150, 110, int(35 * (1 - t)))
    # 棒中间高一些 (厚度)
    w = int(bar_w * (1 - t * 0.3))
    for dy in range(-w, w + 1):
        inner_t = abs(dy) / max(w, 1)
        a = int(col[3] * (1 - inner_t * 0.6))
        draw.ellipse([CX+dx-1, CY+dy-1, CX+dx+1, CY+dy+1],
                     fill=(col[0], col[1], col[2], a))

# ── 叠加明亮星点 (沿盘分布, 不包含中心区域) ──
# ── 叠加明亮星点 (沿盘分布) ──
# 中心 18% 半径内不画星点 (黑心区域)
center_keepout = MAX_R * 0.18
for _ in range(30000):
    r = MAX_R * math.sqrt(random.random())
    if r < center_keepout: continue
    a = random.uniform(0, 2 * math.pi)
    x = CX + r * math.cos(a)
    y = CY + r * math.sin(a) * 0.42
    if not (0 <= x < W and 0 <= y < H): continue
    # 盘中心偏黄, 旋臂偏蓝白
    hot = random.random() < 0.4
    if hot:
        c = (255, 235, 190)
    else:
        c = (200, 215, 235)
    bright = random.randint(60, 255) * math.exp(-r / (MAX_R * 0.55))
    if bright < 25: continue
    size = random.uniform(1, 2.8)
    draw.ellipse([x-size, y-size, x+size, y+size],
                 fill=(int(c[0]*bright/255), int(c[1]*bright/255), int(c[2]*bright/255), 255))

# ── 大星点带十字光芒 (少数亮星, 增加真实感) ──
for _ in range(40):
    r = MAX_R * random.uniform(0.18, 0.95)  # 从黑心边缘开始
    a = random.uniform(0, 2 * math.pi)
    x = CX + r * math.cos(a)
    y = CY + r * math.sin(a) * 0.42
    b = random.randint(180, 255)
    size = random.uniform(2.5, 5)
    draw.ellipse([x-size, y-size, x+size, y+size], fill=(b, b, b, 255))
    # 十字光芒
    for s in range(1, 4):
        draw.line([x-s*3, y, x+s*3, y], fill=(b, b, b, 80), width=1)
        draw.line([x, y-s*3, x, y+s*3], fill=(b, b, b, 80), width=1)

# ── 中心 Sgr A* 标记已移除 (2026-08-29) ──
# 之前画的 EHT 风格黑阴影+不对称光环视觉上像几何标记,不像真实黑洞照片,摘掉
# 保留自然渲染的核球即可

# ── 整体微柔化 + 对比度增强 ──
img = img.filter(ImageFilter.GaussianBlur(0.8))
from PIL import ImageEnhance
img = ImageEnhance.Contrast(img).enhance(1.15)
img = ImageEnhance.Brightness(img).enhance(1.02)

img.save('/Users/w/earth-explorer/data/galaxy_diagram.png')
print('真实风格银河系图已生成')
