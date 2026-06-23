from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from students.models import Student
from clubs.models import ClubMembership
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
import random


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


PALETTES = [
    ('#1a1a2e', '#e94560'), ('#0f3460', '#00d2ff'),
    ('#2d0a4e', '#c77dff'), ('#004e4e', '#00dfc0'),
    ('#4a0000', '#ff6b6b'), ('#003d1a', '#00ff88'),
    ('#3d1a00', '#ffaa00'), ('#1a1a3a', '#8888ff'),
    ('#1b0030', '#ff6b9d'), ('#002b36', '#2aa198'),
    ('#0b1d3a', '#f0a500'), ('#1a0000', '#ff4444'),
    ('#001f3f', '#3d9970'), ('#2c3e50', '#3498db'),
    ('#4a235a', '#8e44ad'), ('#0e6251', '#1abc9c'),
    ('#78281f', '#e74c3c'), ('#7e5109', '#f1c40f'),
    ('#1b2631', '#5dade2'), ('#512e5f', '#bb8fce'),
]


class Command(BaseCommand):
    help = 'Generate profile photos for students in clubs'

    def generate_photo(self, student):
        w, h = 200, 200
        colors = PALETTES[hash(student.id) % len(PALETTES)]
        img = Image.new('RGB', (w, h), hex_to_rgb(colors[0]))
        draw = ImageDraw.Draw(img)

        r = 100
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([w//2 - r, h//2 - r, w//2 + r, h//2 + r],
                    fill=(*hex_to_rgb(colors[1]), 80))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)

        initial = (student.first_name[0] + student.last_name[0]).upper()
        font_size = 56 if len(initial) == 1 else 48
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

        bbox = draw.textbbox((0, 0), initial, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (w - tw) // 2
        y = (h - th) // 2 - 5
        draw.text((x, y), initial, fill='white', font=font)

        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf

    def handle(self, *args, **options):
        member_ids = set(ClubMembership.objects.values_list('student_id', flat=True))
        students = [s for s in Student.objects.filter(id__in=member_ids) if not s.profile_photo]

        if not students:
            self.stdout.write('All club students already have profile photos.')
            return

        for student in students:
            buf = self.generate_photo(student)
            safe = f'{student.first_name.lower()}_{student.last_name.lower()}_{student.id}'
            filename = f'{safe}.png'
            student.profile_photo.save(filename, ContentFile(buf.getvalue()), save=True)
            self.stdout.write(f'  {student.full_name}')

        self.stdout.write(self.style.SUCCESS(f'Generated photos for {len(students)} students'))
