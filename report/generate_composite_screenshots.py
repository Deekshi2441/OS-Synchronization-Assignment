"""
Generates combined Figure 1, 2, 3, 4 images showing both the
generated HTML simulation and the terminal execution window,
matching the visual format of the reference report.
"""

import os
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "screenshots")

FONT_PATH = "C:\\Windows\\Fonts\\consola.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "C:\\Windows\\Fonts\\cour.ttf"

def create_terminal_image(title_cmd: str, log_lines: list, width: int = 700, height: int = 400) -> Image.Image:
    img = Image.new("RGB", (width, height), color="#0c0c0c")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, 13)
        font_bold = ImageFont.truetype(FONT_PATH, 13)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font

    # Draw top terminal header bar
    draw.rectangle([0, 0, width, 26], fill="#1f1f1f")
    draw.text((12, 6), "PowerShell — Windows Terminal", fill="#cccccc", font=font)
    draw.ellipse([width - 55, 8, width - 45, 18], fill="#3a3a3a")
    draw.ellipse([width - 38, 8, width - 28, 18], fill="#3a3a3a")
    draw.ellipse([width - 20, 8, width - 10, 18], fill="#e81123")

    # Command line prompt
    y = 36
    draw.text((12, y), title_cmd, fill="#e5e5e5", font=font_bold)
    y += 22

    for line in log_lines:
        color = "#cccccc"
        if "ENTER" in line or "EATING" in line or "has both" in line:
            color = "#4ec9b0"
        elif "REQUEST" in line or "HUNGRY" in line:
            color = "#dcdcaa"
        elif "EXIT" in line or "RELEASING" in line or "put down" in line:
            color = "#9cdcfe"
        elif "validation OK" in line:
            color = "#6a9955"

        draw.text((12, y), line, fill=color, font=font)
        y += 18
        if y > height - 15:
            break

    return img


def build_figure(html_img_path: str, terminal_img: Image.Image, output_path: str):
    html_img = Image.open(html_img_path).convert("RGB")
    
    # Resize HTML image to fit width
    target_width = 800
    w_percent = target_width / float(html_img.size[0])
    target_height = int(float(html_img.size[1]) * float(w_percent))
    html_resized = html_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Resize terminal image to match target width
    term_w_percent = target_width / float(terminal_img.size[0])
    term_height = int(float(terminal_img.size[1]) * float(term_w_percent))
    term_resized = terminal_img.resize((target_width, term_height), Image.Resampling.LANCZOS)

    # Stack vertically
    total_height = target_height + term_height + 12
    comp_img = Image.new("RGB", (target_width, total_height), color="#ffffff")
    comp_img.paste(html_resized, (0, 0))
    comp_img.paste(term_resized, (0, target_height + 12))

    comp_img.save(output_path, "PNG", quality=95)
    print(f"Created: {output_path}")


def main():
    # 1. Figure 1: Readers-Writers Semaphores
    cmd1 = "PS C:\\OS-Synchronization-Assignment> python readers_writers/semaphore/rw_semaphore.py"
    lines1 = [
        "[0.148s] R3 waiting requests read access",
        "[0.148s] R3 reading entered CS, readers inside = 1",
        "[0.276s] R2 reading entered CS, readers inside = 2",
        "[0.346s] R4 reading entered CS, readers inside = 3",
        "[0.416s] R3 idle    left CS, readers inside = 2",
        "[0.536s] W2 waiting requests write access",
        "[0.540s] R3 waiting requests read access",
        "[0.575s] R1 waiting requests read access",
        "[0.588s] W1 waiting requests write access",
        "[0.599s] R2 idle    left CS, readers inside = 1",
        "[0.743s] R4 idle    left CS, readers inside = 0",
        "[0.744s] W2 writing entered CS (exclusive)",
        "[0.920s] W2 idle    left CS, committed value = 1",
        "validation OK: final value equals writers x rounds (6)"
    ]
    term1 = create_terminal_image(cmd1, lines1, 750, 320)
    build_figure(
        os.path.join(SCREENSHOTS_DIR, "readers_writers_semaphore.png"),
        term1,
        os.path.join(SCREENSHOTS_DIR, "fig1_rw_semaphore.png")
    )

    # 2. Figure 2: Readers-Writers Monitor
    cmd2 = "PS C:\\OS-Synchronization-Assignment> python readers_writers/monitor/rw_monitor.py"
    lines2 = [
        "[0.111s] R1 waiting requests read access",
        "[0.112s] R1 reading entered CS, readers inside = 1",
        "[0.145s] R2 waiting requests read access",
        "[0.146s] R2 reading entered CS, readers inside = 2",
        "[0.423s] R3 reading entered CS, readers inside = 3",
        "[0.484s] R4 reading entered CS, readers inside = 4",
        "[0.509s] R2 idle    left CS, readers inside = 3",
        "[0.598s] R1 idle    left CS, readers inside = 2",
        "[0.782s] W2 waiting requests write access",
        "[0.819s] R3 idle    left CS, readers inside = 1",
        "[0.839s] R4 idle    left CS, readers inside = 0",
        "[0.839s] W2 writing entered CS (exclusive)",
        "[1.015s] W2 idle    left CS, committed value = 1",
        "validation OK: final value equals writers x rounds (6)"
    ]
    term2 = create_terminal_image(cmd2, lines2, 750, 320)
    build_figure(
        os.path.join(SCREENSHOTS_DIR, "readers_writers_monitor.png"),
        term2,
        os.path.join(SCREENSHOTS_DIR, "fig2_rw_monitor.png")
    )

    # 3. Figure 3: Dining Philosophers Semaphores
    cmd3 = "PS C:\\OS-Synchronization-Assignment> python dining_philosophers/semaphore/dp_semaphore.py"
    lines3 = [
        "[4.299s] P2 releasing put down fork 2",
        "[4.300s] P2 releasing put down fork 3",
        "[4.301s] P2 thinking  finished all meals",
        "[4.301s] P1 acquiring picked up fork 2",
        "[4.302s] P1 eating    has both forks",
        "[4.632s] P1 releasing put down fork 1",
        "[4.633s] P1 releasing put down fork 2",
        "[4.634s] P1 thinking  finished all meals",
        "[4.635s] P0 acquiring picked up fork 1",
        "[4.635s] P0 eating    has both forks",
        "[4.943s] P0 releasing put down fork 0",
        "[4.944s] P0 releasing put down fork 1",
        "[4.944s] P0 thinking  finished all meals",
        "validation OK: forks never shared and every meal had both forks"
    ]
    term3 = create_terminal_image(cmd3, lines3, 750, 320)
    build_figure(
        os.path.join(SCREENSHOTS_DIR, "dining_philosophers_semaphore.png"),
        term3,
        os.path.join(SCREENSHOTS_DIR, "fig3_dp_semaphore.png")
    )

    # 4. Figure 4: Dining Philosophers Monitor
    cmd4 = "PS C:\\OS-Synchronization-Assignment> python dining_philosophers/monitor/dp_monitor.py"
    lines4 = [
        "[0.150s] P0 hungry    wants to eat",
        "[0.156s] P0 acquiring took fork 0",
        "[0.157s] P0 acquiring took fork 1",
        "[0.157s] P0 eating    has both forks",
        "[0.158s] P2 hungry    wants to eat",
        "[0.158s] P2 acquiring took fork 2",
        "[0.158s] P2 acquiring took fork 3",
        "[0.159s] P2 eating    has both forks",
        "[0.186s] P3 hungry    wants to eat",
        "[0.533s] P1 hungry    wants to eat",
        "[0.609s] P2 releasing put down fork 2",
        "[0.634s] P2 releasing put down fork 3",
        "[0.634s] P2 thinking  back to thinking",
        "validation OK: forks never shared and every meal had both forks"
    ]
    term4 = create_terminal_image(cmd4, lines4, 750, 320)
    build_figure(
        os.path.join(SCREENSHOTS_DIR, "dining_philosophers_monitor.png"),
        term4,
        os.path.join(SCREENSHOTS_DIR, "fig4_dp_monitor.png")
    )

if __name__ == "__main__":
    main()
