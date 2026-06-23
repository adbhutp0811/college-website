from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from clubs.models import Club
from io import BytesIO
import random
from PIL import Image, ImageDraw, ImageFont
import os


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def hex_to_rgba(h, a):
    return (*hex_to_rgb(h), a)


class Command(BaseCommand):
    help = 'Generate AI-themed profile images for all clubs and cells'

    def get_colors(self, name):
        palettes = [
            ('#1a1a2e', '#16213e', '#0f3460', '#e94560'),
            ('#0f0c29', '#302b63', '#24243e', '#00d2ff'),
            ('#000428', '#004e92', '#1a1a2e', '#00f2fe'),
            ('#0d1117', '#161b22', '#21262d', '#58a6ff'),
            ('#1b0030', '#2d0a4e', '#3d1a6e', '#c77dff'),
            ('#002626', '#004e4e', '#0e7a7a', '#00dfc0'),
            ('#1a0000', '#4a0000', '#8a0000', '#ff6b6b'),
            ('#001f0a', '#003d1a', '#006b2e', '#00ff88'),
            ('#1a0a00', '#3d1a00', '#6b3000', '#ffaa00'),
            ('#0a0a1a', '#1a1a3a', '#2a2a5a', '#8888ff'),
        ]
        idx = hash(name) % len(palettes)
        return palettes[idx]

    def generate_image(self, club):
        w, h = 400, 400
        colors = self.get_colors(club.name)
        img = Image.new('RGB', (w, h), hex_to_rgb(colors[0]))

        for i in range(3):
            cx = random.randint(50, 350)
            cy = random.randint(50, 350)
            r = random.randint(100, 250)
            alpha = random.randint(20, 60)
            overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                                 fill=hex_to_rgba(colors[i + 1], alpha))
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        overlay2 = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        overlay2_draw = ImageDraw.Draw(overlay2)
        for _ in range(random.randint(5, 12)):
            x = random.randint(0, w)
            y = random.randint(0, h)
            s = random.randint(2, 6)
            overlay2_draw.ellipse([x - s, y - s, x + s, y + s], fill=hex_to_rgba(colors[-1], 128))
        img = Image.alpha_composite(img.convert('RGBA'), overlay2).convert('RGB')

        short = club.name.replace(' Club', '').replace(' Cell', '').replace(' (ICC)', '')
        lines = []
        for word in short.split():
            if lines and len(lines[-1]) + len(word) < 18:
                lines[-1] += ' ' + word
            else:
                lines.append(word)

        font_size = 36 if len(short) < 12 else 28 if len(short) < 20 else 22
        try:
            font_paths = [
                'C:\\Windows\\Fonts\\segoeui.ttf',
                'C:\\Windows\\Fonts\\arial.ttf',
                'C:\\Windows\\Fonts\\calibri.ttf',
            ]
            font = None
            for fp in font_paths:
                if os.path.exists(fp):
                    font = ImageFont.truetype(fp, font_size)
                    break
            if not font:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(img)

        total_h = len(lines) * (font_size + 6)
        start_y = (h - total_h) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (w - tw) // 2
            y = start_y + i * (font_size + 6)
            draw.text((x + 2, y + 2), line, fill='#00000040', font=font)
            draw.text((x, y), line, fill='white', font=font)

        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf

    def handle(self, *args, **options):
        clubs = Club.objects.filter(is_active=True)
        for club in clubs:
            buf = self.generate_image(club)
            safe = club.name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("&","and").replace("/", "_").replace("\\", "_")
            filename = f'{safe}.png'
            club.image.save(filename, ContentFile(buf.getvalue()), save=True)
            self.stdout.write(f'  {club.name}')

        self.stdout.write(self.style.SUCCESS(f'Generated profile images for {clubs.count()} clubs'))
