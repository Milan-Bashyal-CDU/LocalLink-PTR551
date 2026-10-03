from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg


class CustomUser(AbstractUser):
    """Extended user supporting the two primary LocalLink roles plus staff coordinators."""

    ROLE_SEEKER = 'seeker'
    ROLE_HELPER = 'helper'
    ROLE_COORDINATOR = 'coordinator'
    ROLE_CHOICES = [
        (ROLE_SEEKER, 'Support Seeker'),
        (ROLE_HELPER, 'Helper / Volunteer'),
        (ROLE_COORDINATOR, 'Coordinator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SEEKER)
    phone = models.CharField(max_length=20, blank=True)
    suburb = models.CharField(max_length=80, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    bio = models.TextField(blank=True, help_text='Short description about yourself.')
    skills = models.CharField(
        max_length=255, blank=True,
        help_text='Helpers: comma-separated skills, e.g. "IT support, gardening, tutoring".')
    is_verified = models.BooleanField(
        default=False, help_text='Set by a coordinator after an identity / police check.')

    @property
    def is_seeker(self):
        return self.role == self.ROLE_SEEKER

    @property
    def is_helper(self):
        return self.role == self.ROLE_HELPER

    @property
    def is_coordinator(self):
        return self.role == self.ROLE_COORDINATOR or self.is_staff

    def average_rating(self):
        result = self.reviews_received.aggregate(avg=Avg('rating'))['avg']
        return round(result, 1) if result else None

    def review_count(self):
        return self.reviews_received.count()

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'
