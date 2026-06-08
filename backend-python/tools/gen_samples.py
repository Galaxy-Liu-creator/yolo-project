"""生成 6 张吊装作业现场占位样例图（1280x720）。

运行：python tools/gen_samples.py
不含任何真实公司名，仅作演示占位。
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent.parent / "app" / "static" / "samples"
W, H = 1280, 720

# 每张图：背景色、标题、场景文案
SAMPLES = [
    ("sample_01.jpg", (38, 50, 62), "井场 · 吊装作业现场", "作业人员进入机械旋转半径内"),
    ("sample_02.jpg", (45, 40, 60), "钻井平台 · 吊装作业现场", "作业人员进入吊物下方"),
    ("sample_03.jpg", (32, 56, 50), "管材堆场 · 吊装作业现场", "人员越过电子围栏"),
    ("sample_04.jpg", (56, 46, 34), "设备吊装区 · 吊装作业现场", "未佩戴安全帽"),
    ("sample_05.jpg", (40, 44, 60), "井场 · 吊装作业现场", "违规指挥吊装"),
    ("sample_06.jpg", (50, 38, 44), "设备吊装区 · 吊装作业现场", "吊物捆绑 / 索具不规范"),
]


def _font(size: int):
    # 尝试常见中文字体，退回默认字体
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_one(name: str, bg, title: str, subtitle: str):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # 网格背景，模拟监控画面
    grid = (bg[0] + 18, bg[1] + 18, bg[2] + 18)
    for x in range(0, W, 80):
        d.line([(x, 0), (x, H)], fill=grid, width=1)
    for y in range(0, H, 80):
        d.line([(0, y), (W, y)], fill=grid, width=1)

    # 模拟地面 / 吊臂示意
    d.line([(0, 540), (W, 540)], fill=(90, 90, 90), width=3)          # 地面线
    d.line([(900, 120), (1080, 300)], fill=(120, 130, 150), width=10)  # 吊臂
    d.line([(1080, 120), (1080, 320)], fill=(120, 130, 150), width=8)  # 立柱
    d.rectangle([1040, 320, 1130, 400], outline=(120, 180, 110), width=4)  # 吊物示意
    d.ellipse([360, 420, 420, 540], outline=(220, 90, 90), width=4)        # 人员示意

    # 标题与场景
    f_title = _font(46)
    f_sub = _font(34)
    f_small = _font(24)
    d.text((40, 40), "油田吊装作业安全视频智能分析系统", fill=(235, 235, 235), font=f_title)
    d.text((40, 110), title, fill=(180, 210, 240), font=f_sub)
    d.text((40, 160), f"违章示例：{subtitle}", fill=(240, 200, 120), font=f_sub)
    d.text((40, H - 50), "DEMO 占位图 · 仅供演示", fill=(150, 150, 150), font=f_small)

    # 角标尺寸
    d.text((W - 220, H - 50), f"{W}×{H}", fill=(150, 150, 150), font=f_small)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img.save(OUT_DIR / name, quality=85)
    print("written", OUT_DIR / name)


def main():
    for name, bg, title, sub in SAMPLES:
        draw_one(name, bg, title, sub)
    print("done, total", len(SAMPLES))


if __name__ == "__main__":
    main()
