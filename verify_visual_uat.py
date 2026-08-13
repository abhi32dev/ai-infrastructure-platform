import os
from PIL import Image, ImageDraw, ImageFont

artifact_dir = "/Users/abhi/.gemini/antigravity/brain/3c431721-b2f2-4621-b3fe-4b12e98501d5"

try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 44)
    font_sub_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    font_badge = ImageFont.truetype("/System/Library/Fonts/Monaco.dfont", 22)
except Exception:
    font_title = ImageFont.load_default()
    font_sub_title = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_badge = ImageFont.load_default()

def draw_diamond(draw, center_x, center_y, width, height, fill_color, stroke_color):
    half_w = width // 2
    half_h = height // 2
    points = [
        (center_x, center_y - half_h),
        (center_x + half_w, center_y),
        (center_x, center_y + half_h),
        (center_x - half_w, center_y)
    ]
    draw.polygon(points, fill=fill_color, outline=stroke_color, width=4)

def draw_stadium(draw, x, y, width, height, fill_color, stroke_color):
    draw.rounded_rectangle([x, y, x + width, y + height], radius=height//2, fill=fill_color, outline=stroke_color, width=4)

def draw_box(draw, x, y, width, height, fill_color, stroke_color):
    draw.rounded_rectangle([x, y, x + width, y + height], radius=14, fill=fill_color, outline=stroke_color, width=3)

def draw_arrow(draw, start_pos, end_pos, color, width=4):
    draw.line([start_pos, end_pos], fill=color, width=width)
    x1, y1 = start_pos
    x2, y2 = end_pos
    if x1 == x2:
        if y2 > y1:
            draw.polygon([(x2-10, y2-16), (x2+10, y2-16), (x2, y2)], fill=color)
        else:
            draw.polygon([(x2-10, y2+16), (x2+10, y2+16), (x2, y2)], fill=color)
    elif y1 == y2:
        if x2 > x1:
            draw.polygon([(x2-16, y2-10), (x2-16, y2+10), (x2, y2)], fill=color)
        else:
            draw.polygon([(x2+16, y2-10), (x2+16, y2+10), (x2, y2)], fill=color)

def generate_uat_screenshot_p20():
    W, H = 2200, 1600
    img = Image.new("RGB", (W, H), color="#0d1117") # SOLID DARK CANVAS - ZERO GRID
    draw = ImageDraw.Draw(img)

    c_bg_card = "#161b22"
    c_cyan = "#38bdf8"
    c_green = "#34d399"
    c_green_bg = "#092e20"
    c_gold = "#fbbf24"
    c_gold_bg = "#1f1906"
    c_rose = "#f43f5e"
    c_rose_bg = "#3b1219"

    # Title Header
    draw.text((W//2, 50), "Project 20: Data Governance & OpenLineage Catalog", fill="#ffffff", font=font_title, anchor="mm")
    draw.text((W//2, 100), "Great Expectations Data Quality Contracts, Marquez Lineage Graph & ABORT Telemetry", fill="#8b949e", font=font_sub_title, anchor="mm")

    # Start Node
    draw_stadium(draw, 700, 150, 800, 80, c_green_bg, c_green)
    draw.text((1100, 190), "▶ Start: OpenLineageCatalog.execute_job()", fill=c_green, font=font_bold, anchor="mm")

    draw_arrow(draw, (1100, 230), (1100, 300), c_cyan)

    # Step 1 Box
    draw_box(draw, 650, 300, 900, 100, c_bg_card, c_cyan)
    draw.text((1100, 335), "Run Pre-Job Data Quality Contract", fill="#ffffff", font=font_bold, anchor="mm")
    draw.text((1100, 372), "src/data_governance.py:L48", fill=c_cyan, font=font_badge, anchor="mm")

    draw_arrow(draw, (1100, 400), (1100, 470), c_cyan)

    # Decision 1 Diamond
    draw_diamond(draw, 1100, 560, 800, 180, c_gold_bg, c_gold)
    draw.text((1100, 520), "DECISION 1", fill=c_gold, font=font_bold, anchor="mm")
    draw.text((1100, 555), "Pre-Job Data Contract Passed?", fill="#ffffff", font=font_bold, anchor="mm")
    draw.text((1100, 590), "(Zero Schema / Null Offenses)", fill="#8b949e", font=font_badge, anchor="mm")

    # Left Branch (Aborted)
    draw.line([(700, 560), (350, 560)], fill=c_rose, width=4)
    draw_arrow(draw, (350, 560), (350, 700), c_rose)

    draw_box(draw, 420, 525, 220, 45, c_rose_bg, c_rose)
    draw.text((530, 547), "NO (Violations)", fill=c_rose, font=font_badge, anchor="mm")

    draw_box(draw, 50, 700, 600, 100, c_bg_card, c_rose)
    draw.text((350, 735), "Emit OpenLineage ABORT Event", fill="#ffffff", font=font_bold, anchor="mm")
    draw.text((350, 772), "Quarantine Corrupt Dataset", fill=c_rose, font=font_badge, anchor="mm")

    draw_arrow(draw, (350, 800), (350, 880), c_rose)
    draw_stadium(draw, 70, 880, 560, 80, c_rose_bg, c_rose)
    draw.text((350, 920), "✖ Pipeline Aborted", fill=c_rose, font=font_bold, anchor="mm")

    # Down Branch (Passed)
    draw_arrow(draw, (1100, 650), (1100, 740), c_green)
    draw_box(draw, 1120, 670, 220, 45, c_green_bg, c_green)
    draw.text((1230, 692), "YES (Passed)", fill=c_green, font=font_badge, anchor="mm")

    # Step 2 Box
    draw_box(draw, 650, 740, 900, 100, c_bg_card, c_cyan)
    draw.text((1100, 775), "Emit START -> Execute Job -> Register Graph", fill="#ffffff", font=font_bold, anchor="mm")
    draw.text((1100, 812), "MarquezCatalogClient.register_job()", fill=c_cyan, font=font_badge, anchor="mm")

    draw_arrow(draw, (1100, 840), (1100, 920), c_cyan)

    # Decision 2 Diamond
    draw_diamond(draw, 1100, 1010, 800, 180, c_gold_bg, c_gold)
    draw.text((1100, 970), "DECISION 2", fill=c_gold, font=font_bold, anchor="mm")
    draw.text((1100, 1005), "Did Transformation Job Complete?", fill="#ffffff", font=font_bold, anchor="mm")
    draw.text((1100, 1040), "(Marquez Lineage Graph Audit)", fill="#8b949e", font=font_badge, anchor="mm")

    # Down Success
    draw_arrow(draw, (1100, 1100), (1100, 1190), c_green)
    draw_box(draw, 1120, 1120, 220, 45, c_green_bg, c_green)
    draw.text((1230, 1142), "YES (Job Complete)", fill=c_green, font=font_badge, anchor="mm")

    draw_box(draw, 650, 1190, 900, 100, c_bg_card, c_green)
    draw.text((1100, 1225), "Emit OpenLineage COMPLETE Event", fill="#ffffff", font=font_bold, anchor="mm")
    draw.text((1100, 1262), "Register Row Metrics in Marquez", fill=c_green, font=font_badge, anchor="mm")

    draw_arrow(draw, (1100, 1290), (1100, 1370), c_green)
    draw_stadium(draw, 700, 1370, 800, 80, c_green_bg, c_green)
    draw.text((1100, 1410), "★ Lineage Graph Updated", fill=c_green, font=font_bold, anchor="mm")

    # Right Branch (Error / Exception)
    draw.line([(1500, 1010), (1850, 1010)], fill=c_rose, width=4)
    draw_arrow(draw, (1850, 1010), (1850, 1110), c_rose)
    draw_box(draw, 1530, 975, 200, 45, c_rose_bg, c_rose)
    draw.text((1630, 997), "NO (Exception)", fill=c_rose, font=font_badge, anchor="mm")

    draw_diamond(draw, 1850, 1180, 500, 140, c_gold_bg, c_gold)
    draw.text((1850, 1160), "DECISION 3", fill=c_gold, font=font_bold, anchor="mm")
    draw.text((1850, 1195), "Marquez Up?", fill="#ffffff", font=font_bold, anchor="mm")

    # Upward Retry Loop Arrow
    draw.line([(1850, 1110), (1850, 790)], fill=c_gold, width=4)
    draw_arrow(draw, (1850, 790), (1550, 790), c_gold)
    draw_box(draw, 1570, 755, 240, 45, c_gold_bg, c_gold)
    draw.text((1690, 777), "↻ YES (Retry Telemetry)", fill=c_gold, font=font_badge, anchor="mm")

    # Down Fallback
    draw_arrow(draw, (1850, 1250), (1850, 1330), c_rose)
    draw_box(draw, 1550, 1330, 600, 100, c_bg_card, c_rose)
    draw.text((1850, 1365), "Quarantine Dataset & Emit Alert", fill="#ffffff", font=font_bold, anchor="mm")
    draw.text((1850, 1402), "Log Governance Failure", fill=c_rose, font=font_badge, anchor="mm")

    out_path = os.path.join(artifact_dir, "flowchart_20_uat.png")
    img.save(out_path, "PNG")
    print(f"Generated Project 20 UAT Screenshot Verification Image: {out_path}")

generate_uat_screenshot_p20()
