# yourapp/management/commands/generate_passwords.py
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Generate hashed passwords for sample users'

    # def handle(self, *args, **options):
    #     passwords = [
    #         'password1', 'password2', 'password3', 'password4', 'password5',
    #         'password6', 'password7', 'password8', 'password9', 'password10',
    #         'password11', 'password12', 'password13', 'password14', 'password15',
    #         'password16', 'password17', 'password18', 'password19', 'password20'
    #     ]
    #     hashed_passwords = [make_password(password) for password in passwords]
    #
    #     for hashed_password in hashed_passwords:
    #         self.stdout.write(self.style.SUCCESS(hashed_password))

    def handle(self, *args, **options):
        base_username = 'user'
        base_password = 'password'

        for i in range(11, 51):  # Generate usernames user11, user12, ..., user50
            username = f'{base_username}{i}'
            password = base_password

            User.objects.create_user(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username}'))
