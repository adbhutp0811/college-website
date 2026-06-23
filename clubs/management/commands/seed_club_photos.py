from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from clubs.models import Club
from urllib.request import urlopen
from urllib.error import URLError
from io import BytesIO


TOPIC_MAP = {
    'drama': 'theatre,stage',
    'music': 'music,concert',
    'debate': 'debate,podium',
    'photography': 'photography,camera',
    'robotics': 'robot,technology',
    'coding': 'coding,programming',
    'sports': 'sports,athletes',
    'literary': 'books,literature',
    'dance': 'dance,dancer',
    'entrepreneurship': 'startup,business',
    'anti-ragging': 'college,campus',
    'cultural': 'culture,festival',
    'equal opportunity': 'diversity,inclusion',
    'grievance': 'justice,balance',
    'complaints': 'committee,meeting',
    'iqac': 'quality,education',
    'nss': 'social-service,volunteer',
    'placement': 'career,interview',
    'research': 'research,laboratory',
    'startup': 'startup,innovation',
    'sc/st': 'diversity,equality',
    'women': 'women,empowerment',
}


def get_keyword(club_name):
    name = club_name.lower()
    for key, val in TOPIC_MAP.items():
        if key in name:
            return val
    return 'college,students'


class Command(BaseCommand):
    help = 'Download club-relevant aesthetic photos for all clubs and cells'

    def handle(self, *args, **options):
        clubs = Club.objects.filter(is_active=True)
        success = 0

        for club in clubs:
            keyword = get_keyword(club.name)
            url = f'https://loremflickr.com/400/400/{keyword}'
            url_g = f'https://loremflickr.com/g/400/400/{keyword}'

            for attempt_url in (url, url_g):
                try:
                    resp = urlopen(attempt_url, timeout=15)
                    if resp.url == attempt_url or resp.status == 200:
                        buf = BytesIO(resp.read())
                        if len(buf.getvalue()) > 5000:
                            break
                except Exception:
                    continue
            else:
                self.stdout.write(self.style.WARNING(f'  Failed {club.name}'))
                continue

            safe = club.name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('&', 'and').replace('/', '_').replace('\\', '_')
            filename = f'{safe}.jpg'
            club.image.save(filename, ContentFile(buf.getvalue()), save=True)
            self.stdout.write(f'  {club.name} ({keyword})')
            success += 1

        self.stdout.write(self.style.SUCCESS(f'Downloaded photos for {success}/{clubs.count()} clubs'))
