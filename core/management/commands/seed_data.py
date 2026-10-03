from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import CustomUser
from core.models import Category, HelpRequest, Offer, Review


CATEGORIES = [
    ('Technology Help', 'laptop', 'Devices, internet, apps and online safety.'),
    ('Social Visit & Companionship', 'cup-hot', 'A friendly chat, a walk, reducing isolation.'),
    ('Transport & Errands', 'bag', 'Shopping, appointments, picking things up.'),
    ('Gardening & Yard', 'tree', 'Weeding, mowing, light outdoor work.'),
    ('Tutoring & Literacy', 'book', 'Homework help, reading, English practice.'),
    ('Home & Admin', 'house-gear', 'Forms, bills, small household tasks.'),
]


class Command(BaseCommand):
    help = 'Populate the database with demo categories, users and requests.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding LocalLink demo data…')

        cats = {}
        for name, icon, desc in CATEGORIES:
            c, _ = Category.objects.get_or_create(
                name=name, defaults={'slug': slugify(name), 'icon': icon, 'description': desc})
            cats[name] = c

        # Coordinator / admin
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser(
                'admin', 'admin@locallink.test', 'adminpass123',
                role=CustomUser.ROLE_COORDINATOR, first_name='Site', last_name='Coordinator')

        def mkuser(username, role, first, last, suburb, skills='', verified=False):
            u, created = CustomUser.objects.get_or_create(
                username=username,
                defaults=dict(role=role, first_name=first, last_name=last,
                              suburb=suburb, postcode='0810', skills=skills,
                              is_verified=verified, email=f'{username}@locallink.test'))
            if created:
                u.set_password('password123')
                u.save()
            return u

        seekers = [
            mkuser('margaret', CustomUser.ROLE_SEEKER, 'Margaret', 'Ellis', 'Nightcliff'),
            mkuser('tom', CustomUser.ROLE_SEEKER, 'Tom', 'Nguyen', 'Casuarina'),
            mkuser('ruth', CustomUser.ROLE_SEEKER, 'Ruth', 'Okoye', 'Parap'),
        ]
        helpers = [
            mkuser('aisha', CustomUser.ROLE_HELPER, 'Aisha', 'Khan', 'Casuarina',
                   'IT support, tutoring', verified=True),
            mkuser('james', CustomUser.ROLE_HELPER, 'James', 'Barnes', 'Nightcliff',
                   'gardening, transport', verified=True),
            mkuser('wei', CustomUser.ROLE_HELPER, 'Wei', 'Chen', 'Parap',
                   'companionship, admin', verified=False),
        ]

        samples = [
            ('margaret', 'Technology Help', 'Set up video calls to see my grandchildren',
             'I have a new tablet but cannot work out how to make video calls. '
             'Would love someone patient to show me step by step.', 'Nightcliff',
             HelpRequest.URGENCY_MEDIUM, True),
            ('tom', 'Transport & Errands', 'Lift to a medical appointment on Thursday',
             'I need a lift to Royal Darwin Hospital on Thursday morning and back. '
             'I use a walking frame.', 'Casuarina', HelpRequest.URGENCY_HIGH, False),
            ('ruth', 'Gardening & Yard', 'Help trimming an overgrown hedge',
             'My front hedge has gotten out of control and I can no longer manage it myself.',
             'Parap', HelpRequest.URGENCY_LOW, False),
            ('margaret', 'Social Visit & Companionship', 'A weekly chat over a cuppa',
             'Since my husband passed I would enjoy a friendly weekly visit and conversation.',
             'Nightcliff', HelpRequest.URGENCY_LOW, False),
            ('tom', 'Technology Help', 'Help recovering a locked email account',
             'I am locked out of my email and have important messages I need to read.',
             'Casuarina', HelpRequest.URGENCY_MEDIUM, True),
        ]
        by_username = {u.username: u for u in seekers}
        created_reqs = []
        for uname, cat, title, desc, suburb, urg, remote in samples:
            r, created = HelpRequest.objects.get_or_create(
                seeker=by_username[uname], title=title,
                defaults=dict(description=desc, category=cats[cat], suburb=suburb,
                              urgency=urg, is_remote_ok=remote,
                              preferred_date=date.today() + timedelta(days=5)))
            created_reqs.append(r)

        # One completed + matched example with a review
        demo = created_reqs[0]
        if demo.status == HelpRequest.STATUS_OPEN:
            Offer.objects.get_or_create(request=demo, helper=helpers[0],
                                        defaults={'message': 'Happy to help — I tutor IT and love teaching.'})
            demo.helper = helpers[0]
            demo.status = HelpRequest.STATUS_COMPLETED
            demo.save()
            Review.objects.get_or_create(
                request=demo, reviewer=demo.seeker, reviewee=helpers[0],
                defaults={'rating': 5, 'comment': 'Aisha was so patient and kind. I can now call my family!'})

        self.stdout.write(self.style.SUCCESS(
            'Done. Superuser: admin / adminpass123. Demo users password: password123'))
