import os

try:
    from __revision__ import __revision__
except:
    __revision__ = 'develop'

metadata = {
    'name': "django360",
    'version': "1.0",
    'release': __revision__,
    'url': 'http://www.django360.com',
    'author': 'hanbox',
    'author_email': 'han.mdarien@gmail.com',
    'admin': 'han.mdarien@gmail.com',
    'dependencies': (
        'BeautifulSoup',
        'recaptcha-client==1.0.5',
        'Markdown==2.0.3',
        'python-openid==2.2.4',
        'python-yadis==1.1.0',
        'Pygments>=1.1.1',
        'simplejson',
        'django-haystack',
        'django-debug-toolbar',
        'South',
        'django-extensions',
        'html5lib',
        'pysolr',
        'django-nose',
    ),
    'description': 'Django360',
    'license': 'Private',
}
