import random
import shutil
import os

from django.core.management.base import BaseCommand
from common.models import User
from members.models import UserProfile
from conf.settings import MEDIA_ROOT


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        fist delete all used users than
        create fresh ones :)

        """
        delete_users = User.objects.filter(
            is_staff=False,
        ).delete()

        # delete avatar files
        path = (MEDIA_ROOT + '/privat')
        shutil.rmtree(path)
        os.mkdir(path)

        owner = User.objects.create_user(
            username='john.doe@example.app',
            email='john.doe@example.app',
            first_name='John',
            last_name='Doe',
            password='try3000'
        )

        profile = UserProfile.objects.create(
            user=owner,
            is_owner_admin=True,
            email_is_verified=True,
            owner=owner,
        )
        profile.save()

        # now create 100 employees
        MEMBERS_COUNT = 99

        FIRST_NAME = [
            'Hiro', 'Teiki', 'Moana', 'Manua', 'Marama',
            'Teiva', 'Teva', 'Maui', 'Tehei', 'Tamatoa',
            'Ioane', 'Tapuarii', 'Ben', 'Jonas', 'Leon',
            'Paul', 'Noah', 'Elias', 'Felix', 'Maximilian',
            'Emil', 'Anton', 'Max', 'Theo', 'Matteo', 'Liam',
            'Moritz', 'Julian', 'Leo', 'David', 'Alexander',
            'Milan', 'Philipp', 'Tim', 'Samuel', 'Tom',
            'Leonard', 'Jonathan', 'Hannes', 'Linus',
            'Jan', 'Fabian', 'Vincent', 'Mika', 'Adrian',
            'Till', 'Simon'

        ]

        LAST_NAME = [
            'Tiare',  'Hinano',  'Poema',  'Maeva',  'Hina',
            'Vaea',  'Titaua',  'Moea',  'Moeata',  'Tarita',
            'Titaina',  'Teura',  'Heikapu',  'Mareva', 'Müller',
            'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer',
            'Wagner', 'Becker', 'Schulz', 'Hoffmann', 'Schäfer',
            'Koch', 'Bauer', 'Richter', 'Klein', 'Wolf', 'Neumann',
            'Schwarz', 'Zimmermann', 'Braun', 'Krüger', 'Hofmann',
            'Hartmann', 'Lange', 'Schmitt', 'Werner', 'Schmitz',
            'Krause', 'Meier', 'Lehmann'
        ]

        for i in range(MEMBERS_COUNT):
            first_name = "".join(random.choice(FIRST_NAME))
            last_name = "".join(random.choice(LAST_NAME))

            username_count = User.objects.filter(
                username__startswith=first_name + last_name
            ).count()

            if username_count < 1:
                name = '%s%s' % (first_name, last_name)
            else:
                name = '%s%s%s' % (first_name, last_name, username_count *1000 )

            member = User.objects.create_user(
                username=name.lower() + '@example.app',
                first_name=first_name,
                last_name=last_name,
                email=name.lower() + '@example.app'
            )
            profile = UserProfile.objects.create(
                user=member,
                owner=owner
            )
            profile.save()
