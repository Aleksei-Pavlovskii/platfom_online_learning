from urllib.parse import urlparse
from rest_framework import serializers

ALLOWED_HOSTS = {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be'}


class YouTubeUrlValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        value = value.get(self.field)
        if not value:
            return

        parsed = urlparse(value)
        host = parsed.netloc.split(':')[0].lower() if parsed.netloc else ''

        if host not in ALLOWED_HOSTS:
            raise serializers.ValidationError({
                self.field: (
                    'Ссылка должна вести на youtube.com (или youtu.be). '
                    'Ссылки на сторонние ресурсы запрещены.'
                )
            })
