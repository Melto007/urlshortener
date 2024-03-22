from django.db import models
from django.conf import settings

class URLShortener(models.Model):
    original_url = models.URLField(max_length=255, null=True, blank=True, unique=True)
    short_url = models.URLField(max_length=255, null=True, blank=True, unique=True)
    expired_at = models.DateTimeField(default=settings.EXPIRE_TIMEDATE)

    def __str__(self):
        return str(self.original_url)
