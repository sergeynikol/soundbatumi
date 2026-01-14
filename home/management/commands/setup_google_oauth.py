"""
Management command для настройки Google OAuth Social Application
Использование: python manage.py setup_google_oauth
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os
from dotenv import load_dotenv


class Command(BaseCommand):
    help = 'Настраивает Google OAuth Social Application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-id',
            type=str,
            help='Google OAuth Client ID',
        )
        parser.add_argument(
            '--secret-key',
            type=str,
            help='Google OAuth Secret Key',
        )

    def handle(self, *args, **options):
        load_dotenv()
        
        # Получаем или создаем Site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': '127.0.0.1:8000', 'name': 'localhost'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created site: {site.domain}'))
        
        # Получаем credentials
        client_id = options.get('client_id') or os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
        secret_key = options.get('secret_key') or os.getenv('GOOGLE_OAUTH2_SECRET_KEY')
        
        if not client_id or not secret_key:
            self.stdout.write(self.style.ERROR(
                'Google OAuth credentials not found!\n'
                'Please provide them via:\n'
                '1. Environment variables: GOOGLE_OAUTH2_CLIENT_ID and GOOGLE_OAUTH2_SECRET_KEY\n'
                '2. Command arguments: --client-id and --secret-key\n'
                '3. Or update manually in Django admin: /admin/socialaccount/socialapp/'
            ))
            return
        
        # Получаем или создаем Social Application
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': secret_key,
            }
        )
        
        if not created:
            google_app.client_id = client_id
            google_app.secret = secret_key
            google_app.save()
            self.stdout.write(self.style.SUCCESS('Updated Google Social Application'))
        else:
            self.stdout.write(self.style.SUCCESS('Created Google Social Application'))
        
        # Убеждаемся, что Site привязан
        if site not in google_app.sites.all():
            google_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(f'Linked site {site.domain} to Google Social Application'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Site {site.domain} is already linked'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nGoogle OAuth is configured!\n'
            f'Client ID: {client_id[:20]}...\n'
            f'Site: {site.domain}\n'
        ))
