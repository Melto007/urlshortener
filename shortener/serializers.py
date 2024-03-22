from rest_framework import (
    serializers
)
from core.models import URLShortener

class URLShortenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLShortener
        fields = ['id', 'original_url', 'short_url', 'expired_at']
