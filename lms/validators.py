from rest_framework import serializers
from urllib.parse import urlparse


def validate_youtube_only(value):
    """
    Проверяет, что ссылка ведет только на youtube.com
    Разрешает: youtube.com, www.youtube.com, youtu.be, m.youtube.com
    """
    if not value:
        return  # Если поле пустое, пропускаем (для необязательных полей)
    
    # Парсим URL
    parsed_url = urlparse(value)
    domain = parsed_url.netloc.lower()
    
    # Разрешенные домены YouTube
    allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com']
    
    # Проверяем, что домен точно совпадает или заканчивается на разрешенный домен
    is_youtube = any(
        domain == allowed_domain or domain.endswith('.' + allowed_domain)
        for allowed_domain in allowed_domains
    )
    
    if not is_youtube:
        raise serializers.ValidationError(
            'Разрешены только ссылки на youtube.com. '
            f'Получена ссылка: {value}'
        )