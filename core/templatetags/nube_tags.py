from django import template

register = template.Library()

@register.filter(name='url_nube')
def url_nube(value):
    if not value:
        return ''
    url_str = str(value)
    if "http" in url_str:
        posicion_http = url_str.find("http")
        return url_str[posicion_http:]
    try:
        return value.url
    except AttributeError:
        return url_str