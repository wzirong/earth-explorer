#!/usr/bin/env python3
"""哈勃深空场 + 宇宙微波背景辐射(CMB)
两个 Python 生成的示意图:
1. 哈勃深空场 (Hubble Deep Field) - 用 PIL 模拟极深空的暗弱星系
2. 宇宙微波背景辐射 - Planck 卫星观测的各向异性
"""
from PIL import Image, ImageDraw, ImageFilter
import math, random, os

W, H = 4096, 4096
CX, CY = W // 2, H // 2
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')


def vignette(img, strength=0.6):
    mask = Image.new('L', (W, H), 255)
    md = ImageDraw.Draw(mask)
    ri = int(max(W, H) * 0.5)
    ro = int(max(W, H) * 0.55)
    for i in range(ri, ro, 4):
        t = (i - ri) / (ro - ri)
        a = max(0, int(255 * (1 - t) * strength))
        md.ellipse([CX - i, CY - i, CX + i, CY + i], outline=a, width=4)
    md.ellipse([CX - ro, CY - ro, CX + ro, CY + ro], outline=0, width=4)
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    black = Image.new('RGB', (W, H), (0, 0, 0))
    return Image.composite(img, black, mask)


# ── 1. 哈勃深空场 ──
def gen_hubble_deep_field():
    """模拟哈勃深空场:数千个极暗弱的遥远星系,在微小天区里"""
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')

    # 1. 少量前景亮星(带十字衍射)
    random.seed(42)
    for _ in range(40):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        b = random.randint(200, 255)
        # 亮核
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(b, b, b, 255))
        # 十字衍射
        draw.line([(x - 15, y), (x + 15, y)], fill=(b, b, b, 200), width=1)
        draw.line([(x, y - 15), (x, y + 15)], fill=(b, b, b, 200), width=1)

    # 2. 大量暗弱星系 (20000+),各种形态颜色
    # 形态分布: 不规则 40%, 椭圆 40%, 旋涡 20%
    # 颜色分布: 蓝色年轻星系 30%, 红色老年星系 50%, 中间 20%
    for _ in range(20000):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        # 大小 1-4 像素
        size = random.choice([1, 1, 1, 2, 2, 3])
        # 颜色按形态 + 年龄
        kind = random.random()
        if kind < 0.4:  # 不规则星系 (蓝)
            r = random.randint(80, 140)
            g = random.randint(110, 170)
            b = random.randint(160, 230)
            alpha = random.randint(80, 180)
        elif kind < 0.8:  # 椭圆星系 (红)
            r = random.randint(180, 240)
            g = random.randint(150, 200)
            b = random.randint(100, 160)
            alpha = random.randint(80, 180)
        else:  # 旋涡 (蓝白)
            r = random.randint(150, 200)
            g = random.randint(170, 210)
            b = random.randint(200, 240)
            alpha = random.randint(80, 180)
        # 形态变化: 椭圆有方向
        if kind >= 0.4 and kind < 0.8 and size >= 2:
            # 椭圆星系, 沿一个方向拉伸
            draw.ellipse([x - size * random.uniform(1.5, 3), y - size * 0.7,
                         x + size * random.uniform(1.5, 3), y + size * 0.7],
                        fill=(r, g, b, alpha))
        else:
            draw.ellipse([x - size, y - size, x + size, y + size], fill=(r, g, b, alpha))

    # 3. 少量亮而远的星系 (高红移)
    for _ in range(50):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        size = random.randint(4, 8)
        # 高红移星系偏红 + 模糊
        r = random.randint(200, 250)
        g = random.randint(120, 170)
        b = random.randint(60, 110)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(r, g, b, 220))

    # 4. 几十个显眼星系(借鉴真实 HDF 中有代表性的“明星星系”)
    # 位置手工布置, 表现各种典型形态
    showcase = [
        # (x, y, size, type, color)
        # 大椭圆星系 (红色老年)
        (W * 0.18, H * 0.25, 18, 'ellipse', (220, 170, 110)),
        (W * 0.72, H * 0.62, 22, 'ellipse', (230, 180, 120)),
        (W * 0.45, H * 0.78, 16, 'ellipse', (240, 190, 130)),
        # 旋涡星系 (蓝色青年)
        (W * 0.32, H * 0.55, 14, 'spiral', (130, 170, 220)),
        (W * 0.85, H * 0.30, 12, 'spiral', (110, 150, 200)),
        # 互不双星系 (星系合并)
        (W * 0.55, H * 0.20, 10, 'merger', (200, 160, 130)),
        (W * 0.65, H * 0.85, 9, 'merger', (220, 150, 120)),
        # 不规则星系
        (W * 0.25, H * 0.70, 11, 'irregular', (160, 180, 220)),
        (W * 0.78, H * 0.45, 8, 'irregular', (140, 160, 200)),
        # 边缘旋涡 (侧向)
        (W * 0.50, H * 0.42, 13, 'edgeon', (200, 180, 150)),
        (W * 0.40, H * 0.15, 10, 'edgeon', (180, 160, 140)),
        # 类星体 (高亮点)
        (W * 0.65, H * 0.32, 6, 'quasar', (255, 240, 200)),
        (W * 0.30, H * 0.85, 5, 'quasar', (255, 230, 180)),
    ]
    for x, y, size, gtype, base_col in showcase:
        x, y = int(x), int(y)
        if gtype == 'ellipse':
            # 拉伸的椭圆
            for i in range(size, 0, -1):
                t = i / size
                a = int(255 * (1 - t) * 0.95)
                draw.ellipse([x - i * 2.2, y - i * 0.7, x + i * 2.2, y + i * 0.7],
                             fill=base_col + (a,))
            # 亮核
            draw.ellipse([x - 4, y - 2, x + 4, y + 2], fill=(255, 250, 220, 255))
        elif gtype == 'spiral':
            # 旋涡: 中心亮 + 两条弯曲旋臂
            for i in range(size, 0, -1):
                t = i / size
                a = int(255 * (1 - t) * 0.85)
                draw.ellipse([x - i, y - i, x + i, y + i], fill=base_col + (a,))
            # 旋臂 (大致)
            for arm in range(2):
                for s in range(30):
                    t = s / 30
                    r = size * 0.5 + size * t
                    theta = arm * math.pi + t * 4
                    ax = x + r * math.cos(theta)
                    ay = y + r * math.sin(theta) * 0.6
                    sw = max(1, int(2 - t * 1))
                    draw.ellipse([ax - sw, ay - sw, ax + sw, ay + sw],
                                 fill=(180, 210, 250, 180))
            # 亮核
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, 255))
        elif gtype == 'merger':
            # 两个重叠核
            for cx_off, cy_off in [(0, 0), (size * 0.6, size * 0.3)]:
                cx, cy = x + cx_off, y + cy_off
                for i in range(size // 2, 0, -1):
                    t = i / (size / 2)
                    a = int(255 * (1 - t) * 0.85)
                    draw.ellipse([cx - i * 1.8, cy - i * 0.6, cx + i * 1.8, cy + i * 0.6],
                                 fill=base_col + (a,))
            # 拉伸尾
            draw.line([(x - size * 2, y), (x + size * 2, y + size * 0.3)],
                      fill=base_col + (160,), width=2)
        elif gtype == 'irregular':
            # 不规则星系: 弥散光斑
            for _ in range(size * 5):
                ax = x + random.gauss(0, size * 0.6)
                ay = y + random.gauss(0, size * 0.6)
                if not (0 < ax < W and 0 < ay < H): continue
                col = (base_col[0] + random.randint(-30, 30),
                       base_col[1] + random.randint(-20, 30),
                       base_col[2] + random.randint(-20, 30))
                col = tuple(max(0, min(255, c)) for c in col)
                rs = random.choice([1, 1, 2])
                draw.ellipse([ax - rs, ay - rs, ax + rs, ay + rs], fill=col + (180,))
        elif gtype == 'edgeon':
            # 侧向旋涡: 狭长椭圆 + 沿轴尘埃
            for i in range(size, 0, -1):
                t = i / size
                a = int(255 * (1 - t) * 0.9)
                draw.ellipse([x - i * 2.5, y - i * 0.4, x + i * 2.5, y + i * 0.4],
                             fill=base_col + (a,))
            # 中央尘埃带
            for offset in range(-1, 2):
                draw.line([(x - size * 1.8, y + offset), (x + size * 1.8, y + offset)],
                          fill=(30, 25, 20, 200), width=2)
        elif gtype == 'quasar':
            # 类星体: 极亮中心 + 微亮晕
            draw.ellipse([x - size, y - size, x + size, y + size],
                         fill=(255, 240, 180, 200))
            for i in range(size * 3, size, -1):
                t = (i - size) / (size * 2)
                a = int(180 * (1 - t) * 0.4)
                draw.ellipse([x - i, y - i, x + i, y + i],
                             fill=(255, 230, 160, a))

    img = vignette(img, strength=0.5)
    img.save(os.path.join(OUT_DIR, 'hubble_deep_field.png'))
    print('[hubble_deep_field] saved')


# ── 2. 宇宙微波背景辐射 ──
def gen_cmb():
    """模拟 Planck 卫星观测的宇宙微波背景辐射 (CMB)
    特征: 全天 2.725K 温度, 各向异性 ~10^-5 K 起伏
    颜色: 蓝(冷区) → 黄(暖区)
    """
    img = Image.new('RGB', (W, H), (50, 30, 80))
    draw = ImageDraw.Draw(img, 'RGBA')

    # 大尺度温度起伏 (低频): 用 Perlin-like 噪声 + 多层叠加
    # 简化: 用随机径向波 + 多层叠加
    for layer in range(8):
        freq = 5 + layer * 3
        amp = 80 / (1 + layer)
        scale = 600 // (layer + 1)
        random.seed(layer * 17)
        for _ in range(freq * 8):
            x = random.randint(0, W)
            y = random.randint(0, H)
            r = random.randint(50, scale + 100)
            # 暖区(黄) or 冷区(蓝)
            warm = random.random() < 0.5
            if warm:
                col = (random.randint(180, 240), random.randint(160, 200), random.randint(60, 130), int(amp))
            else:
                col = (random.randint(40, 100), random.randint(80, 140), random.randint(180, 240), int(amp))
            draw.ellipse([x - r, y - r, x + r, y + r], fill=col)

    # 加细颗粒(模拟 CMB 像素化噪声)
    random.seed(9999)
    for _ in range(50000):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        # 极微小的温度起伏
        v = random.randint(-30, 30)
        r = 150 + v
        g = 130 + v
        b = 80 + v
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        img.putpixel((x, y), (r, g, b))

    # 椭圆投影(Mollweide 风格)
    # 这里我们做椭圆遮罩
    mask = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(mask)
    a = W // 2 - 30
    b = H // 2 - 30
    md.ellipse([CX - a, CY - b, CX + a, CY + b], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(20))
    black = Image.new('RGB', (W, H), (0, 0, 0))
    img = Image.composite(img, black, mask)

    # 银河平面 (CMB 中需要扣掉)
    # 简化: 在中央画一条暗带
    mask2 = Image.new('L', (W, H), 0)
    md2 = ImageDraw.Draw(mask2)
    md2.ellipse([CX - W // 2, CY - 30, CX + W // 2, CY + 30], fill=180)
    mask2 = mask2.filter(ImageFilter.GaussianBlur(30))
    img = Image.composite(img, black, mask2)

    img.save(os.path.join(OUT_DIR, 'cmb_radiation.png'))
    print('[cmb_radiation] saved')


if __name__ == '__main__':
    gen_hubble_deep_field()
    gen_cmb()