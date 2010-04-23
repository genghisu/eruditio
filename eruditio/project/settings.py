from os.path import join,  dirname,  normpath

PROJECT_ROOT = join(dirname(normpath(__file__)), '..')
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('hanbox', 'han.mdarien@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"



# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
STATIC_ROOT = join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
MEDIA_ROOT = join(PROJECT_ROOT,  'media')
MEDIA_URL = STATIC_URL + 'media/'
STATIC_LOCAL_ROOT = join(PROJECT_ROOT, 'static_local')
STATIC_LOCAL_URL = '/static_local/'



# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '34#wzfbj^rcz+s_s7g95j9f#6ykrnxbxp^4dp!i)1!ajnt5%o!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openidconsumer.middleware.OpenIDMiddleware',
    'django_community.middleware.CommunityMiddleware',
    'django_reputation.middleware.ReputationMiddleware',
)

ROOT_URLCONF = 'project.urls'

TEMPLATE_DIRS = (
    join(PROJECT_ROOT,  'templates/'), 
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth', 
    'django.core.context_processors.debug', 
    'django.core.context_processors.i18n', 
    'django_community.context_processors.community',
    'django_defaultcontext.context_processors.defaults',
    'django_defaultcontext.context_processors.site_sections',
    'django_reputation.context_processors.reputation',
    'django_comments.context_processors.comments_config',
)

INSTALLED_APPS = (
    'django.contrib.admin', 
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.markup', 
    'south',
    'tutorials',
    'projects',
    'applications',
    'code',
    'info',
    'search',
    'django_qa',
    'django_extensions',
    'django_community',
    'django_defaultcontext',
    'django_comments',
    'django_moderation',
    'django_relatedcontent',
    'django_metatagging',
    'django_utils',
    'django_multivoting',
    'django_gravatar',
    'django_openidconsumer',
    'django_reputation',
    'django_tracking',
    'django_contenthistory',
    'django_badges',
    'django_userhistory',
    'django_community_wiki',
    'haystack',
    'tagging',
    'django_wizard',
    'django_nose',
    'core',
)


CONFIGURED_APPS = (
    'core',
    'tutorials',
    'projects',
    'applications',
    'code',
    'info',
    'django_qa',
    'django_extensions',
    'django_community',
    'django_defaultcontext',
    'django_comments',
    'django_moderation',
    'django_relatedcontent',
    'django_metatagging',
    'django_utils',
    'django_multivoting',
    'django_gravatar',
    'django_openidconsumer',
    'django_reputation',
    'django_tracking',
    'django_contenthistory',
    'django_badges',
    'django_userhistory',
    'django_community_wiki',
)


AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

RECAPTCHA_PUBLIC_KEY = '6LdvGwYAAAAAAJsiMR4IkFJgMXIH-jtT1Rdu9A4G'
RECAPTCHA_PRIVATE_KEY = '6LdvGwYAAAAAAKJ8TJD1WnUk7cbWZDH4fjysrCKJ'

OPENID_ENABLED = True

REPUTATION_ENABLED = True

SETUP = False

HISTORY_TRACKING = True

HAYSTACK_SITECONF = 'project.haystack_site_confs'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8180/solr'

MAX_POSTS_PER_DAY = 3