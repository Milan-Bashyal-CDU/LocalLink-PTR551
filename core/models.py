from django.conf import settings
from django.db import models
from django.urls import reverse

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    """A type of support that can be requested, e.g. Technology Help, Social Visit."""
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=40, blank=True,
                            help_text='Bootstrap icon name, e.g. "laptop".')

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class HelpRequest(models.Model):
    """A task a seeker needs help with. Helpers make offers against it."""

    URGENCY_LOW = 'low'
    URGENCY_MEDIUM = 'medium'
    URGENCY_HIGH = 'high'
    URGENCY_CHOICES = [
        (URGENCY_LOW, 'Low — within a couple of weeks'),
        (URGENCY_MEDIUM, 'Medium — within a few days'),
        (URGENCY_HIGH, 'High — as soon as possible'),
    ]

    STATUS_OPEN = 'open'
    STATUS_MATCHED = 'matched'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_MATCHED, 'Matched'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_made')
    helper = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='requests_assigned')
    title = models.CharField(max_length=140)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='requests')
    suburb = models.CharField(max_length=80)
    is_remote_ok = models.BooleanField(
        default=False, help_text='Can this be done remotely (e.g. phone / video)?')
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default=URGENCY_MEDIUM)
    preferred_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('request_detail', args=[self.pk])

    @property
    def status_badge(self):
        return {
            self.STATUS_OPEN: 'success',
            self.STATUS_MATCHED: 'info',
            self.STATUS_IN_PROGRESS: 'primary',
            self.STATUS_COMPLETED: 'secondary',
            self.STATUS_CANCELLED: 'dark',
        }.get(self.status, 'secondary')

    @property
    def urgency_badge(self):
        return {'low': 'secondary', 'medium': 'warning', 'high': 'danger'}.get(self.urgency, 'secondary')

    def pending_offers(self):
        return self.offers.filter(status=Offer.STATUS_PENDING)

    def has_review_from(self, user):
        return self.reviews.filter(reviewer=user).exists()


class Offer(models.Model):
    """A helper's offer to take on a request."""
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]

    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='offers')
    helper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers_made')
    message = models.TextField(help_text='Introduce yourself and how you can help.')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('request', 'helper')

    def __str__(self):
        return f'Offer by {self.helper} on "{self.request}"'


class Review(models.Model):
    """Feedback left after a completed request."""
    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('request', 'reviewer')

    def __str__(self):
        return f'{self.rating}/5 for {self.reviewee} by {self.reviewer}'


class Message(models.Model):
    """Lightweight messaging between the two parties on a request."""
    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender} on "{self.request}"'
