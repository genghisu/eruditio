# -*- coding: utf-8 -*-

import random

from django.contrib.auth.models import User
from django_community.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist
from django_qa.models import Question, Answer
from core.models import Django, Python
from applications.models import App
from code.models import Code, CodeMode
from tutorials.models import Tutorial

USERS = ['simon', 'carla', 'randy', 'genghis']
TAGS = ['django', 'python', 'riot', 'logo', 'c++', 'c#', 'template-tags', 'filters', 'forms', 'django-extensions']

APPS = ['django-tagging', 'django-extensions', 'soclone', 'django_moderation', 'django_relatedcontent']

TITLES = \
['Why can’t I get my Azure, WCF, REST, SSL project working? What am I doing wrong?',
'Custom preview for open dailog using Delphi',
'Why am I getting an error about my class defining __slots__ when trying to pickle an object?',
'Assigning icons to a ComboBox’s List using dynamically-loaded external images.',
'Rule of Thumb: when to use SQL DB vs. Key-Value store (i.e. Redis)',
'LONG TITLE------Assigning icons to a ComboBox’s List using dynamically-loaded external images.Why can’t I get my Azure, WCF, REST, SSL project working? What am I doing wrong?']

CONTENTS = \
["""<p>With the introduction of <a href="http://framework.zend.com/manual/en/zend.controller.router.html#zend.controller.router.routes.rest" rel="nofollow"><strong>Zend_Rest_Route</strong></a> in Zend Framework 1.9 (and its <a href="http://zendframeworkcookbook.blogspot.com/2009/08/re-fw-mvc-zendrestroute.html" rel="nofollow">update</a> in 1.9.2) we now have a standardized RESTful solution for routing requests. As of August 2009 there are no examples of its usage, only the basic documentation found in the reference guide.</p>

<p>While it is perhaps far more simple than I assume, I was hoping those more competent than I might provide some examples illustrating the use of the <a href="http://framework.zend.com/manual/en/zend.controller.router.html#zend.rest.controller" rel="nofollow"><strong>Zend_Rest_Controller</strong></a> in a scenario where:</p>

<ul>
<li>Some controllers (such as indexController.php) operate normally</li>
<li>Others operate as rest-based services (returning json)</li>
</ul>

<p>It appears the <a href="http://framework.zend.com/manual/en/zend.controller.actionhelpers.html#zend.controller.actionhelpers.json" rel="nofollow"><strong>JSON Action Helper</strong></a> now fully automates and optimizes the json response to a request, making its use along with Zend_Rest_Route an ideal combination.</p>
""",
"""
<p>I'm working on a homework problem and I'm having some difficulties creating a O(n*logn) solution.  I need to write a function that takes a pre-sorted array and a value to search for.  I then need to find if any two elements of the array sum to equal that value. </p>

<p>I need to create both O(n) and O(n*logn) algorithms for this.  </p>

<p>The O(n) was easy to create; however, I am having difficulties creating the O(n*logn) algorithm without adding in some gratuitous code that doesn't actually help in solving the problem.  If anyone could give me some pointers on what I might be missing it would be appreciated.</p>
""",
"""
<p>I have a Crystal Report in Visual Studio 2008 (C#).  Its datasource is set programmatically at run-time to a .NET list, defined as follows:</p>

<pre><code>List&lt;visit_volume&gt; Visits

</code></pre>

<p>a <code>visit_volume</code> looks like this:</p>

<pre><code>public class visit_template
{
    private int _numberOfVisits;
    public int numberOfVisits
    {
        get { return this._numberOfVisits; }
        set { this._numberOfVisits = value; }
    }

    // other ints and doubles declared here
    // ..
    // ..

    private List&lt;mEvent&gt; _events;
    public List&lt;mEvent&gt; events
    {
        get { return this._events; }
        set
        {
            // updates _numberOfVisits here
            // ..
            // build-up a debugging string of each mEvent
            // ..
        }
    }
}
</code></pre>

<p>So, being fed into the Crystal Report is a <code>List&lt;&gt;</code> of <code>visit_volume</code> objects, which themselves contain a <code>List&lt;&gt;</code> of <code>mEvent</code> objects.</p>

<p>In Crystal Reports, I can see the contents of the <code>Visits</code> list, but I can't access and report on the contents of the <code>events</code> member - it just doesn't show.  Is this because Crystal can't handle nested <code>List&lt;&gt;</code> structures, or am I doing something wrong?</p>

<p>Thanks in advance.</p>
"""]

ANSWERS = \
["""
<p>I think that although Crystal understands the 'outer' list as a datatable of rows, the data types of the fields inside that row must be standard database types. For example, if you were creating a SqlServer table and tried to add a field, it would not allow you to select a 'list' as the data type of that field.</p>

<p>I think that you may need to place all of the values from your nested list into a separate object/table, and then get Crystal to form a relationship between those two tables.</p>

<p>I'm not sure how you would supply both objects as the datasource - you may need to declare a dataset in Visual Studio, get Crystal to base its report on that structure, and then pass both objects through as separate tables in a .NET DataSet object.</p>
""",
"""
<p>Lazy programming!</p>

<pre><code>public bool MyProp
{
    get { return (myProp = myProp ?? GetPropValue()).Value; }
}
private bool? myProp;
</code></pre>
""",
"""
<p>You cannot change the signature of an overridden method.  (Except for covarient return types)</p>

<p>In your code, what would you expect to happen if I run the following:</p>

<pre><code>BaseFile file = new Picture();
file.GetFileInformation();  //Look ma, no parameters!

</code></pre>

<p>What would the <code>filePath</code> parameter be?</p>

<p>You should change the parameters of the base and derived methods to be identical.</p>
"""]

CODE = \
"""
import django.http as http
import django.shortcuts as shortcuts
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

import django_community.utils as community_utils
import django_utils.pagination as pagination
import django_utils.request_helpers as request_helpers
import django_community.decorators as community_decorators
from django_reputation.decorators import reputation_required
import applications.forms as forms
import applications.models as models
from core.models import DjangoCompatibility, PythonCompatibility
from django_metatagging.views import RetagAction
from django_moderation.views import FlagAction
from django_reputation.models import Reputation

def apps_list(request, option = 'most_recent'):
    page = request_helpers.get_page(request)
    apps = models.App.objects.get_sorted_objects(option)
    apps = models.App.objects.moderated_content(apps)
    
    current_page, page_range = pagination.paginate_queryset(apps, 20, 5, page)
    
    return shortcuts.render_to_response(
                'applications/list.html', 
                {'current_page':current_page,  
                 'page_range':page_range,  
                 'sort':option}, 
                context_instance = RequestContext(request),
    )

@community_decorators.user_required
def contribute_app(request):
    from tagging.models import Tag
    from django_metatagging.utils import parse_tag_input_local
    
    AppForm = forms.build_app_form()
    
    if request.POST:
        form = AppForm(request.POST,  request.FILES)
        print form.data
        if form.is_valid():
            print form.cleaned_data
            app = models.App.objects.add_app(name = form.cleaned_data.get('name', None), 
                                             description = form.cleaned_data.get('description', None),
                                             version = form.cleaned_data.get('version', None), 
                                             sources = form.cleaned_data.get('sources', None),
                                             dependencies = form.cleaned_data.get('dependencies', []),
                                             python_versions = form.cleaned_data.get('python', []),
                                             django_versions = form.cleaned_data.get('django', []),
                                             usage = 'dependency',
                                             user = request.user)
            tags = parse_tag_input_local(form.cleaned_data['tags'])
            for tag in tags:
                Tag.objects.add_tag(app, tag)
            return http.HttpResponseRedirect(reverse('applications-view-app',  args=[app.id]))
    else:
        form = AppForm()
    return shortcuts.render_to_response(
                'applications/contribute.html', 
                {'form':form}, 
                context_instance = RequestContext(request),
    )
"""

def random_user():
    user_id = random.randint(0, 3)
    user_name = USERS[user_id]
    return User.objects.get(username = user_name)

def random_title():
    title_id = random.randint(0, len(TITLES)-1)
    return TITLES[title_id].strip()

def random_content():
    content_id = random.randint(0, 2)
    return CONTENTS[content_id].strip()

def random_answer():
    id = random.randint(0, 2)
    return ANSWERS[id].strip()

def random_app():
    id = random.randint(0, len(APPS) - 1)
    return APPS[id]

def random_code_mode():
    modes = CodeMode.objects.all()
    mode_id = random.randint(0, modes.count() - 1)
    return modes[mode_id]

def init_users():
    for name in USERS:
        try:
            user = User.objects.get(username = name)
        except ObjectDoesNotExist:
            user = User(username = name)
            user.save()
            user.linked_profile = UserProfile.objects.get_user_profile(user)

def init_questions():
    for i in range(1, 50):
        title = random_title()
        try:
            question = Question.objects.get(name = title + str(i))
        except ObjectDoesNotExist:
            user = random_user()
            body = random_content()
            question = Question.objects.add(user = user, data = {'title':title, 'question':body})
            init_answers(question)
            init_tags(question)

def init_answers(question):
    for i in range(1, 5):
        content = random_answer()
        user = random_user()
        if not user == question.user:
            answer = Answer.objects.answer_question(question = question, user = user, answer = content)

def init_apps():
    for i in range(1, 50):
        name = random_app()
        version = '1.0'
        try:
            app = App.objects.get(name = name + str(i), version = version)
        except ObjectDoesNotExist:
            user = random_user()
            description = random_content()
            
            django_versions = ["%s_%s" % ("Django", x.version) for x in Django.objects.all()]
            python_versions = ["%s_%s" % ("Python", x.version) for x in Python.objects.all()]
            
            data = {'name':name + str(i),
                    'description':description,
                    'version':version,
                    'url':'http://www.google.com',
                    'django_versions':django_versions,
                    'python_versions':python_versions,
                    'sources':'http://www.google.com',
                    'dependencies':'',
                    'usage':'dependency'}
            
            app = App.objects.add(data = data, user=user)
            init_tags(app)

def init_codes():
    for i in range(1, 50):
        name = random_title()
        mode = random_code_mode()
        description = random_answer()
        user = random_user()
        try:
            code = Code.objects.get(name = name[0:70] + str(i), mode = mode)
        except ObjectDoesNotExist:
             data = {'title':name[0:70] + str(i),
                     'description':description,
                     'code':CODE.strip(),
                     'mode':mode.name}
             
             code = Code.objects.add(user = user , data = data)
             init_tags(code)

def init_tutorials():
    for i in range(1, 50):
        name = random_title()
        description = random_content()
        user = random_user()
        url = "http://www.frontend360.com"
        try:
            tutorial = Tutorial.objects.get(name = name[0:70] + str(i), url = url)
        except ObjectDoesNotExist:
            data = {'name':name[0:70] + str(i),
                    'description':description,
                    'url':url}
            
            tutorial = Tutorial.objects.add(data = data, user = user)
            init_tags(tutorial)

def init_tags(object):
    from tagging.models import Tag
    from django_metatagging.utils import parse_tag_input_local
    
    tags = parse_tag_input_local(",".join(TAGS))
    for tag in tags:
        Tag.objects.add_tag(object, tag)
                
def init_database():
    from django.contrib.auth.models import User
    
    init_users()
    init_questions()
    init_apps()
    init_codes()
    init_tutorials()