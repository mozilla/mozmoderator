from django.core.urlresolvers import reverse

from jingo import register


@register.function
def get_next_url(request):
    """Return next_url stored in session or Dashboard."""
    if 'next_url' in request.session:
        return request.session.pop('next_url')
    elif request.get_full_path() == '/':
        return reverse('event')

    return request.get_full_path()
