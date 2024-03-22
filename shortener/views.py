from rest_framework import (
    viewsets,
    mixins,
    status,
    exceptions
)
from rest_framework.response import Response
import pyshorteners
import re
from .serializers import (
    URLShortenerSerializer
)
from core.models import URLShortener
from django.db.models import Q
import datetime
import threading

class HandleThreading(threading.Thread):
    def __init__(self, queryset):
        self.queryset = queryset
        threading.Thread.__init__(self)

    def run(self):
        queryset = self.queryset.filter(
            expired_at__lt=datetime.datetime.now(tz=datetime.timezone.utc)
        )
        for queryset in queryset:
            self.queryset.filter(
                original_url=queryset,
                short_url=queryset.short_url,
                expired_at__lt=datetime.datetime.now(tz=datetime.timezone.utc),
            ).delete()

class UrlShortenerViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = URLShortenerSerializer
    queryset = URLShortener.objects.all()

    def create(self, request):
        try:
            data = request.data

            path = data.get('url', None)

            if path is None:
                raise exceptions.APIException('URL field is required')

            regex = re.compile(
                r'^(?:http|ftp)s?://'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$',
                re.IGNORECASE
            )

            matching = re.match(regex, path)

            if matching is None:
                raise exceptions.APIException('Given URL is invalid, enter the valid url (http should be in the url)')

            shortener = pyshorteners.Shortener()
            shorturl = shortener.tinyurl.short(path)

            old_data = self.queryset.filter(
                expired_at__lt=datetime.datetime.now(tz=datetime.timezone.utc)
            ).exists()

            if old_data:
                HandleThreading(self.queryset).start()

            instance = self.queryset.filter(
                original_url=path,
                short_url=shorturl,
                expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)).exists()

            if instance:
                queryset = self.queryset.get(Q(original_url=path) & Q(short_url=shorturl))
                serializer = self.get_serializer(queryset, many=False)

                response = {
                    'data': serializer.data,
                    'status': status.HTTP_200_OK
                }

                return Response(response)

            payload = {
                'original_url': path,
                'short_url': shorturl
            }
            serializer = self.get_serializer(data=payload)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            queryset = self.queryset.get(Q(original_url=path) & Q(short_url=shorturl))
            serializer = self.get_serializer(queryset, many=False)

            response = {
                'data': serializer.data,
                'status': status.HTTP_200_OK
            }
            return Response(response)
        except Exception as e:
            response = {
                'message': e.args,
                'status': status.HTTP_404_NOT_FOUND
            }
            return Response(response)