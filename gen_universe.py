#!/usr/bin/env python3
"""生成宇宙大尺度结构示意图系列。
风格统一:1:1 正方形 / 纯黑+暗角 / 暖黄核心 / 冷蓝旋臂 / 红粉 HII 节点 / 无文字标注
用法:python3 gen_universe.py [local_group|virgo|laniakea|sloan]
"""
from PIL import Image, ImageDraw, ImageFilter
import math, random, sys, os

W = H = 2048
CX = CY = W // 2
OUT_DIR = os.path.join(os.path.dirname(__file__), 'data')

# ── 通用绘制工具 ────────────────────────────────────

def vignette(img, strength=0.85):
    """径向暗角: 中心 50% 完全不暗, 外圈平滑过渡"""
    mask = Image.new('L', (W, H), 255)  # 默认全保留 (白色=不暗)
    md = ImageDraw.Draw(mask)
    radius_inner = int(max(W, H) * 0.5)  # 内圈: 完全保留
    radius_outer = int(max(W, H) * 0.55)  # 外圈: 完全变黑
    for i in range(radius_inner, radius_outer, 4):
        t = (i - radius_inner) / (radius_outer - radius_inner)
        # 中心=255 (保留), 边缘=0 (变黑)
        a = max(0, int(255 * (1 - t) * strength))
        md.ellipse([CX - i, CY - i, CX + i, CY + i], outline=a, width=4)
    # 再外圈直接全黑
    md.ellipse([CX - radius_outer, CY - radius_outer, CX + radius_outer, CY + radius_outer],
               outline=0, width=4)
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    black = Image.new('RGB', (W, H), (0, 0, 0))
    return Image.composite(img, black, mask)

def scatter_stars(img, count, color_range, r_range=(1, 2)):
    """背景散落星点(带径向密度梯度:中心密、边缘稀)"""
    draw = ImageDraw.Draw(img, 'RGBA')
    for _ in range(count):
        # 拒绝采样: 中心接受率高
        u = random.random()
        v = random.random()
        # 反推半径
        d = (u ** 0.5) * (W // 2 - 50)
        ang = v * 2 * math.pi
        x = int(CX + d * math.cos(ang))
        y = int(CY + d * math.sin(ang))
        b = random.randint(*color_range)
        r = random.choice([r_range[0]] * 4 + [r_range[1]])
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(255, b + 10)))

def draw_galaxy(draw, cx, cy, radius, rotation=0, type='spiral'):
    """绘制旋涡星系（中心 + 旋臂 + 节点）"""
    # 中心棒 / 核球（径向渐变: 亮黄→暗黄→透明）
    bulge_r = int(radius * 0.22)
    for i in range(bulge_r, 0, -1):
        t = i / bulge_r
        a = int(255 * (1 - t) ** 1.2 * 0.95)
        col = (255, int(220 + 30 * t), int(160 + 60 * t), a)
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=col)
    # 棒状结构（如果是棒旋星系）：明显的横贯长棒
    if type == 'barred':
        bar_len = int(radius * 0.7)  # 更长
        bar_w_max = int(radius * 0.12)  # 比核球宽
        for dx in range(-bar_len, bar_len):
            t = abs(dx) / bar_len
            w_pro = (1 - t ** 1.8)  # 中间粗两端细更明显
            if w_pro < 0.05: continue
            bar_w = max(1, int(bar_w_max * w_pro))
            a = int(255 * w_pro * 0.85)
            # 棒颜色: 中心略亮黄白，两端偏暗黄
            for dy in range(-bar_w, bar_w + 1):
                inner_t = abs(dy) / max(bar_w, 1)
                inner_a = int(a * (1 - inner_t * 0.6))
                col_a = (255, int(220 - inner_t * 30), int(170 - inner_t * 60), inner_a)
                draw.ellipse([cx + dx - 1, cy + dy - 1, cx + dx + 1, cy + dy + 1],
                             fill=col_a)
        # 棒端点处的高亮节点（恒星形成区）
        for side in [-1, 1]:
            x_end = cx + side * int(radius * 0.6)
            for _ in range(20):
                ox = x_end + random.randint(-8, 8)
                oy = cy + random.randint(-6, 6)
                draw.ellipse([ox - 1, oy - 1, ox + 1, oy + 1], fill=(255, 220, 180, 180))
    # 旋臂（对数螺线，内粗外细）
    # 棒旋星系：旋臂从棒两端（角度 0 和 pi 的位置）甩出
    arm_phase = 1.3 if type == 'barred' else math.pi  # 棒旋的旋臂相对棒的角度
    for arm in range(2):
        base_angle = rotation + arm * arm_phase
        steps = 600
        for s in range(steps):
            t = s / steps
            r = radius * 0.15 + radius * 0.85 * t
            theta = base_angle + t * 3.4 * (1 + arm * 0.15)
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta) * 0.55  # 椭圆盘
            if not (0 < x < W and 0 < y < H): continue
            # 旋臂宽度: 内粗外细
            sw = max(1, int(12 - r / radius * 11))
            # 冷蓝白
            b = random.randint(170, 240)
            a = int(255 * (1 - (r / radius) ** 1.5) * 0.85)
            draw.ellipse([x - sw, y - sw, x + sw, y + sw],
                         fill=(b - 40, b - 20, min(255, b + 10), a))
            # 偶发 HII 红粉节点
            if random.random() < 0.08 and r < radius * 0.7:
                rs = random.randint(2, 5)
                draw.ellipse([x - rs, y - rs, x + rs, y + rs],
                             fill=(255, random.randint(80, 140), random.randint(140, 200), random.randint(180, 230)))
    # 暗尘埃带（沿旋臂内侧，棕色细丝）
    for arm in range(2):
        base_angle = rotation + arm * math.pi + 0.25
        for s in range(120):
            t = s / 120
            r = radius * 0.25 + radius * 0.5 * t
            theta = base_angle + t * 2.4
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta) * 0.55
            sw = random.randint(1, 3)
            draw.ellipse([x - sw, y - sw, x + sw, y + sw],
                         fill=(50, 35, 25, 200))



def draw_edgeon_galaxy(draw, cx, cy, radius, rotation=0):
    """侧向旋涡星系（M31 类型）：狭长椭圆盘 + 沿长轴尘埃带 + 中央鼓包"""
    long_axis = radius  # 长半轴
    short_axis = int(radius * 0.22)  # 短半轴（侧向很扁）
    # 旋转角度：水平短轴旋转 rotation 弧度
    cos_a = math.cos(rotation)
    sin_a = math.sin(rotation)
    # 盘：逐点填充
    for px in range(-long_axis, long_axis + 1):
        t_x = px / long_axis
        # 盘面亮度沿径向指数衰减
        disk_b = (1 - t_x ** 2) ** 0.6
        w_max = short_axis * disk_b
        if w_max < 1: continue
        for py in range(-int(w_max), int(w_max) + 1):
            t_y = py / max(w_max, 1)
            # 旋转坐标
            rx = px * cos_a - py * sin_a + cx
            ry = px * sin_a + py * cos_a + cy
            if not (0 < rx < W and 0 < ry < H): continue
            # 盘颜色: 外圈冷蓝，内圈暖黄
            r2 = math.hypot(t_x, t_y)
            if r2 < 0.25:
                col = (255, 235, 190, int(255 * (1 - r2 * 2) * 0.95))
            elif r2 < 0.6:
                col = (220, 200, 180, int(255 * (1 - (r2 - 0.25) * 2.5) * 0.9))
            else:
                col = (170, 190, 220, int(255 * (1 - (r2 - 0.6) * 1.5) * 0.8))
            draw.ellipse([rx - 1, ry - 1, rx + 1, ry + 1], fill=col)
    # 中央鼓包（bulge）
    bulge_r = int(short_axis * 0.9)
    for i in range(bulge_r, 0, -1):
        t = i / bulge_r
        a = int(255 * (1 - t) * 0.95)
        col = (255, 240, 200, a)
        bx = cx
        by = cy
        draw.ellipse([bx - i, by - i, bx + i, by + i], fill=col)
    # 沿长轴的尘埃带（暗色细线）
    for offset_y in range(-2, 3):
        for px in range(-int(long_axis * 0.7), int(long_axis * 0.7)):
            t_x = abs(px) / (long_axis * 0.7)
            a = int(200 * (1 - t_x ** 0.7))
            # 旋转后的位置
            rx = px * cos_a - offset_y * sin_a + cx
            ry = px * sin_a + offset_y * cos_a + cy
            if not (0 < rx < W and 0 < ry < H): continue
            # 暗尘颜色
            draw.ellipse([rx - 1, ry - 1, rx + 1, ry + 1], fill=(30, 25, 20, a))


def draw_dwarf_irregular(draw, cx, cy, size, color='blue'):
    """麦哲伦云型不规则星系:弥散斑块"""
    for _ in range(int(size * 8)):
        x = cx + random.gauss(0, size * 0.6)
        y = cy + random.gauss(0, size * 0.6)
        if not (0 < x < W and 0 < y < H): continue
        if color == 'blue':
            b = random.randint(140, 200)
            c = (b - 30, b - 10, b)
        else:
            b = random.randint(160, 220)
            c = (b, b - 20, max(0, b - 60))
        rs = random.choice([1, 1, 2])
        draw.ellipse([x - rs, y - rs, x + rs, y + rs], fill=c + (random.randint(180, 240),))

def draw_dwarf_elliptical(draw, cx, cy, size):
    """矮椭圆星系:淡黄弥散"""
    for i in range(int(size), 0, -1):
        a = int(255 * (1 - i / size) * 0.7)
        col = (220, 200, 160, a)
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=col)


# ── Level 3: 本星系群(Local Group) ────────────────────
# 范围约 1000 万光年。银河系 + M31 + M33 + 50+ 矮星系
def gen_local_group():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(42)
    scatter_stars(img, 4500, (60, 220), (1, 2))

    # 银河系 + M31 是双主结构,放左右各占半边
    # M31(仙女座):左偏上,直径略大于银河系
    # M31 仙女座：侧向，77° 倾角
    draw_edgeon_galaxy(draw, CX - 380, CY - 80, 420, rotation=0.45)
    # 银河系(Milky Way):右偏下,棒旋星系(SBbc)
    draw_galaxy(draw, CX + 400, CY + 100, 320, rotation=math.pi - 0.2, type='barred')
    # M33(三角座):中下方,中等旋涡
    draw_galaxy(draw, CX + 50, CY + 500, 200, rotation=0.6, type='spiral')

    # 大小麦哲伦云(银河系卫星,在银河系右下方)
    draw_dwarf_irregular(draw, CX + 250, CY + 240, 45, 'blue')
    draw_dwarf_irregular(draw, CX + 330, CY + 290, 32, 'blue')
    # M31 周围的卫星:M32 / M110
    draw_dwarf_elliptical(draw, CX - 310, CY - 230, 24)
    draw_dwarf_elliptical(draw, CX - 510, CY + 60, 18)
    # 散布的矮球状星系(整个本星系群各处)
    dwarf_positions = [
        (CX - 600, CY + 300, 12), (CX - 720, CY - 200, 10), (CX + 600, CY - 350, 14),
        (CX + 700, CY + 350, 11), (CX - 100, CY - 500, 10), (CX - 350, CY + 500, 13),
        (CX + 100, CY - 600, 9), (CX + 500, CY + 500, 10), (CX - 800, CY - 50, 11),
        (CX + 850, CY + 100, 12), (CX - 200, CY + 650, 10), (CX + 200, CY - 700, 9),
        (CX - 500, CY - 400, 11), (CX + 400, CY - 500, 13), (CX - 650, CY + 450, 10),
        (CX + 100, CY + 200, 9), (CX - 200, CY - 200, 8), (CX + 600, CY - 100, 10),
        (CX - 700, CY + 100, 11), (CX + 50, CY + 50, 8),
    ]
    for x, y, s in dwarf_positions:
        draw_dwarf_elliptical(draw, x, y, s)

    # 额外不规则星系点缀
    for _ in range(15):
        x = CX + random.randint(-700, 700)
        y = CY + random.randint(-700, 700)
        draw_dwarf_irregular(draw, x, y, random.randint(5, 12), random.choice(['blue', 'yellow']))

    img = vignette(img, strength=0.9)
    img.save(os.path.join(OUT_DIR, 'local_group.png'))
    print('[local_group] saved')


# ── Level 4: 室女座星系团(Virgo Cluster) ─────────
# 范围约 600 万光年,中心 M87(巨型椭圆)。本星系群位于其外围
def gen_virgo():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(123)
    scatter_stars(img, 3000, (50, 200), (1, 2))

    # M87(中心):巨型椭圆星系 cD, 直径约 12 万光年(银河系 10x)
    m87_x, m87_y = CX, CY
    # 最外层光晕 (暗物质晕暗示, 淡蓝紫)
    for i in range(700, 400, -2):
        t = (i - 400) / 300
        a = int(40 * (1 - t) * 0.6)
        draw.ellipse([m87_x - i, m87_y - i, m87_x + i, m87_y + i], fill=(90, 80, 130, a))
    # 主体光晕 (直径 ~ 600px)
    for i in range(600, 0, -2):
        a = int(255 * (1 - i / 600) * 0.85)
        col = (255, max(220, 245 - i // 8), max(200, 225 - i // 6), a)
        draw.ellipse([m87_x - i, m87_y - i, m87_x + i, m87_y + i], fill=col)
    # 核心更亮
    for i in range(120, 0, -1):
        a = int(255 * (1 - i / 120))
        draw.ellipse([m87_x - i, m87_y - i, m87_x + i, m87_y + i], fill=(255, 255, 240, a))
    # (喷流移到星系绘制之后)
    # M86 / M84(中心旁边的两个亮椭圆)
    draw_dwarf_elliptical(draw, m87_x + 180, m87_y - 100, 60)
    draw_dwarf_elliptical(draw, m87_x - 160, m87_y + 140, 55)
    # M49 / M60(次级子群)
    draw_dwarf_elliptical(draw, CX + 600, CY - 400, 70)
    draw_dwarf_elliptical(draw, CX - 550, CY + 450, 60)

    # 散布 1300 个星系(旋涡 / 不规则 / 椭圆)
    # 旋涡:30%; 椭圆:50%; 不规则:20%
    # 密度从中心向外递减
    # 真实室女星系团: E/S0 主导(70%), S 较少(20%), Irr 极少(10%)
    spiral_count = 260
    elliptical_count = 910
    irregular_count = 130

    for _ in range(spiral_count):
        # 中心密集,边缘稀疏
        d = random.random() ** 0.7
        ang = random.uniform(0, 2 * math.pi)
        r = d * (W // 2 - 50)
        x = CX + r * math.cos(ang)
        y = CY + r * math.sin(ang)
        size = random.randint(8, 35)
        rot = random.uniform(0, 2 * math.pi)
        draw_galaxy(draw, x, y, size, rotation=rot)

    for _ in range(elliptical_count):
        d = random.random() ** 0.7
        ang = random.uniform(0, 2 * math.pi)
        r = d * (W // 2 - 50)
        x = CX + r * math.cos(ang)
        y = CY + r * math.sin(ang)
        size = random.randint(4, 28)
        draw_dwarf_elliptical(draw, int(x), int(y), size)

    for _ in range(irregular_count):
        d = random.random() ** 0.7
        ang = random.uniform(0, 2 * math.pi)
        r = d * (W // 2 - 50)
        x = CX + r * math.cos(ang)
        y = CY + r * math.sin(ang)
        size = random.randint(4, 18)
        draw_dwarf_irregular(draw, int(x), int(y), size, random.choice(['blue', 'yellow']))

        # ── M87 喷流(画在星系之上, 不被遮挡) ──
    jet_dir = math.radians(-30)  # 朝右上
    # 主喷流: 锥形 + 渐变, 覆盖在所有背景星系之上
    # 喷流从 M87 边缘 (620px) 开始向外延伸, 用 line 画, RGB 直接覆盖
    start_r = 620
    jet_length = 500
    # 主喷流: 沿直线画很多小线段, 每段宽度递增
    prev_x, prev_y = m87_x + start_r * math.cos(jet_dir), m87_y + start_r * math.sin(jet_dir)
    for s in range(2, jet_length, 2):
        r = start_r + s
        x = m87_x + r * math.cos(jet_dir)
        y = m87_y + r * math.sin(jet_dir)
        if not (0 < x < W and 0 < y < H): break
        t = s / jet_length
        w = int(2 + t * 6)
        # 颜色按距离调
        if t < 0.3:
            col = (200, 225, 255)
        elif t < 0.65:
            col = (140, 190, 250)
        else:
            col = (100, 150, 230)
        # 画 2w 宽的线段 (上下左右各偏移)
        for off in range(-w, w + 1):
            px = int(x + off * math.sin(jet_dir))
            py = int(y - off * math.cos(jet_dir))
            if 0 <= px < W and 0 <= py < H:
                # 中心最亮, 边缘略暗
                fade = 1 - abs(off) / max(w + 1, 1)
                final_col = tuple(int(c * (0.6 + 0.4 * fade)) for c in col)
                draw.point((px, py), fill=final_col)
    # 沿线节点 (knots)
    for kn in [620+70, 620+140, 620+220, 620+300]:
        r = kn
        x = m87_x + r * math.cos(jet_dir)
        y = m87_y + r * math.sin(jet_dir)
        if not (0 < x < W and 0 < y < H): continue
        for _ in range(15):
            ox = x + random.randint(-6, 6)
            oy = y + random.randint(-6, 6)
            draw.ellipse([ox - 3, oy - 3, ox + 3, oy + 3], fill=(200, 220, 255, 220))
    # 反向喷流 (微弱)
    jet_dir2 = jet_dir + math.pi
    for s in range(0, 250, 2):
        r = start_r + s
        x = m87_x + r * math.cos(jet_dir2)
        y = m87_y + r * math.sin(jet_dir2)
        if not (0 < x < W and 0 < y < H): break
        width = 2
        alpha = max(0, int(180 * (1 - s / 250)))
        draw.ellipse([x - width, y - width, x + width, y + width], fill=(110, 140, 220, alpha))

    # 本星系群位置(右上角小标注:银河系 + M31 + M33 的微缩)
    lg_x, lg_y = CX + 800, CY - 700
    # 用一个淡蓝色光晕表示"本星系群在室女团的这个方向"
    for i in range(60, 0, -1):
        a = int(120 * (1 - i / 60))
        draw.ellipse([lg_x - i, lg_y - i, lg_x + i, lg_y + i], fill=(80, 130, 220, a))
    draw_galaxy(draw, lg_x, lg_y, 18, rotation=0.3)
    draw_galaxy(draw, lg_x - 25, lg_y + 15, 16, rotation=math.pi - 0.3)
    draw_galaxy(draw, lg_x + 10, lg_y + 30, 8, rotation=0.7)

    img = vignette(img, strength=0.6)  # 较弱的暗角, 让喷流和 M87 不被压暗
    img.save(os.path.join(OUT_DIR, 'virgo_cluster.png'))
    print('[virgo_cluster] saved')


# ── Level 5: 拉尼亚凯亚超星系团 ─────────────────
# 范围约 5.2 亿光年,包含 10 万个星系。
# 实际数据: Tully et al. 2014 用星系本动速度场定义边界
# 这里用程序化生成:中心吸引子(巨引源)+ 长丝状结构 + 4 个主要团
def gen_laniakea():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(7777)
    scatter_stars(img, 2500, (40, 180), (1, 2))

    # 巨引源 (Great Attractor): 中心偏下, 质量异常集中区
    ga_x, ga_y = CX, CY + 100
    for i in range(250, 0, -1):
        a = int(200 * (1 - i / 250) ** 1.3)
        col = (255, 220, 160, a)
        draw.ellipse([ga_x - i, ga_y - i, ga_x + i, ga_y + i], fill=col)
    # 巨引源核心更亮
    for i in range(80, 0, -1):
        a = int(255 * (1 - i / 80))
        draw.ellipse([ga_x - i, ga_y - i, ga_x + i, ga_y + i], fill=(255, 240, 200, a))

    # ── 长丝状结构 (filaments) ──
    # 6 条从巨引源向外延伸的长丝, 明显呈辐射状
    filaments = [
        # 角度 (从中心向外), 长度, 宽度, 密度
        (math.radians(15), 1400, 75, 900),    # 右下
        (math.radians(-35), 1300, 70, 800),   # 右上
        (math.radians(-100), 1200, 65, 700),  # 上偏左
        (math.radians(140), 1300, 70, 800),   # 左下
        (math.radians(175), 1200, 65, 700),   # 正左
        (math.radians(60), 1100, 60, 600),    # 右上偏
    ]
    for ang, length, w, density in filaments:
        # 沿长丝撒星系
        for _ in range(density):
            # 沿轴线距离 (从中心向外)
            s = random.uniform(w, length)
            # 主轴位置
            bx = ga_x + s * math.cos(ang)
            by = ga_y + s * math.sin(ang)
            # 垂直偏移 (高斯, 丝宽)
            offset = random.gauss(0, w * 0.7)
            x = bx + offset * math.cos(ang + math.pi/2)
            y = by + offset * math.sin(ang + math.pi/2)
            if not (0 < x < W and 0 < y < H): continue
            kind = random.random()
            if kind < 0.5:
                draw_dwarf_elliptical(draw, int(x), int(y), random.randint(2, 7))
            elif kind < 0.8:
                draw_dwarf_irregular(draw, int(x), int(y), random.randint(2, 5), random.choice(['blue', 'yellow']))
            else:
                draw_galaxy(draw, x, y, random.randint(3, 8), rotation=random.uniform(0, 2 * math.pi))
        # 沿丝撒 2-3 个节点星系团 (亮区)
        for node_pos in [0.35, 0.65, 0.9]:
            s = int(node_pos * length)
            bx = ga_x + s * math.cos(ang)
            by = ga_y + s * math.sin(ang)
            offset = random.gauss(0, w * 0.2)
            x = bx + offset * math.cos(ang + math.pi/2)
            y = by + offset * math.sin(ang + math.pi/2)
            if not (0 < x < W and 0 < y < H): continue
            # 节点: 亮椭圆晕
            for r2 in range(40, 0, -1):
                t2 = r2 / 40
                a = int(220 * (1 - t2) * 0.9)
                draw.ellipse([x - r2, y - r2, x + r2, y + r2], fill=(255, 230, 180, a))
            # 周围 15 颗小星系
            for _ in range(15):
                ang2 = random.uniform(0, 2 * math.pi)
                rr = random.uniform(35, 60)
                gx = x + rr * math.cos(ang2)
                gy = y + rr * math.sin(ang2)
                draw_dwarf_elliptical(draw, int(gx), int(gy), random.randint(2, 5))

    # 背景广布星系 (稀疏, 在长丝之间)
    for _ in range(1500):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        kind = random.random()
        if kind < 0.5:
            draw_dwarf_elliptical(draw, x, y, random.randint(1, 3))
        elif kind < 0.8:
            draw_dwarf_irregular(draw, x, y, random.randint(1, 2), random.choice(['blue', 'yellow']))
        else:
            draw_galaxy(draw, x, y, random.randint(2, 5), rotation=random.uniform(0, 2 * math.pi))

    # 本星系群位置 (右下角小标注)
    lg_x, lg_y = CX + 780, CY + 720
    for i in range(50, 0, -1):
        a = int(100 * (1 - i / 50))
        draw.ellipse([lg_x - i, lg_y - i, lg_x + i, lg_y + i], fill=(80, 130, 220, a))
    draw_galaxy(draw, lg_x, lg_y, 15, rotation=0.3)

    img = vignette(img, strength=0.6)
    img.save(os.path.join(OUT_DIR, 'laniakea.png'))
    print('[laniakea] saved')


def gen_sloan():
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    random.seed(31415)
    scatter_stars(img, 2000, (40, 160), (1, 1))

    # 史隆长城主墙:从左上角斜向右下角的细长带
    # 长度 W*1.4,宽度 W*0.15
    wall_x1, wall_y1 = -200, 200
    wall_x2, wall_y2 = W + 200, H - 100
    wall_len = math.hypot(wall_x2 - wall_x1, wall_y2 - wall_y1)
    wall_angle = math.atan2(wall_y2 - wall_y1, wall_x2 - wall_x1)
    wall_width = 180

    # 主墙密度梯度
    main_count = 5000
    for _ in range(main_count):
        t = random.random()
        # 沿主线
        bx = wall_x1 + (wall_x2 - wall_x1) * t
        by = wall_y1 + (wall_y2 - wall_y1) * t
        # 垂直偏移(高斯分布)
        offset = random.gauss(0, wall_width * 0.4)
        x = bx + offset * math.cos(wall_angle + math.pi / 2)
        y = by + offset * math.sin(wall_angle + math.pi / 2)
        if not (0 < x < W and 0 < y < H): continue
        kind = random.random()
        if kind < 0.45:
            draw_dwarf_elliptical(draw, int(x), int(y), random.randint(1, 4))
        elif kind < 0.78:
            draw_dwarf_irregular(draw, int(x), int(y), random.randint(1, 3), random.choice(['blue', 'yellow']))
        else:
            draw_galaxy(draw, x, y, random.randint(2, 7), rotation=random.uniform(0, 2 * math.pi))

    # 节点星系团(几个超星系团位置)
    nodes = [
        (CX - 600, CY - 250, 100),  # 主节点 1
        (CX + 200, CY + 200, 120),  # 主节点 2
        (CX + 800, CY + 600, 80),   # 末端节点
    ]
    for x, y, size in nodes:
        draw_dwarf_elliptical(draw, x, y, size // 3)
        for _ in range(50):
            ang = random.uniform(0, 2 * math.pi)
            r = random.gauss(size, size * 0.3)
            if r < 5: continue
            gx = x + r * math.cos(ang)
            gy = y + r * math.sin(ang)
            if not (0 < gx < W and 0 < gy < H): continue
            kind = random.random()
            if kind < 0.5:
                draw_dwarf_elliptical(draw, int(gx), int(gy), random.randint(2, 5))
            else:
                draw_dwarf_irregular(draw, int(gx), int(gy), random.randint(2, 4), random.choice(['blue', 'yellow']))

    # 周围其他长城(次要结构)
    # 武仙-北冕座长城:另一条已知大尺度结构
    filaments = [
        ((CX + 800, CY - 700), (CX - 200, CY + 100), 1500, 60),  # 平行结构
        ((CX - 700, CY + 700), (CX + 900, CY - 600), 1200, 50),  # 对角交叉
    ]
    for (x1, y1), (x2, y2), count, width in filaments:
        for _ in range(count):
            t = random.random()
            x = x1 + (x2 - x1) * t + random.gauss(0, width)
            y = y1 + (y2 - y1) * t + random.gauss(0, width)
            if not (0 < x < W and 0 < y < H): continue
            if random.random() < 0.7:
                draw_dwarf_elliptical(draw, int(x), int(y), random.randint(1, 3))
            else:
                draw_dwarf_irregular(draw, int(x), int(y), random.randint(1, 2), random.choice(['blue', 'yellow']))

    # 背景广布星系(可观测宇宙的暗示)
    for _ in range(4000):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        if random.random() < 0.7:
            draw_dwarf_elliptical(draw, x, y, random.randint(1, 2))
        else:
            draw_dwarf_irregular(draw, x, y, random.randint(1, 2), random.choice(['blue', 'yellow']))

    img = vignette(img)
    img.save(os.path.join(OUT_DIR, 'sloan_great_wall.png'))
    print('[sloan_great_wall] saved')


# ── 入口 ────────────────────────────────────────────
if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if target in ('all', 'local_group'):
        gen_local_group()
    if target in ('all', 'virgo'):
        gen_virgo()
    if target in ('all', 'laniakea'):
        gen_laniakea()
    if target in ('all', 'sloan'):
        gen_sloan()
    print('done')