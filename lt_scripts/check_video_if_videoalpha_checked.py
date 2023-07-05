"""
    Command : `python manage.py cms shell < check_video_if_videoalpha_checked.py`

"""

from django.contrib.auth.models import User

from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore


print('1) ### Load a user from Mysql...')
try:
    _user = User.objects.get(username='LT-developer')
except Exception:
    _user = User.objects.get(username='edx')
print('... user loaded: {}'.format(_user))


INCORRECT_NAME = 'videoalpha'
CORRECT_NAME = 'video'
#INCORRECT_NAME = 'video'
#CORRECT_NAME = 'videoalpha'


print('2) ### Replacing `videoalpha` with `video`...')
for course in CourseOverview.objects.all():
    course_key = course.id
    try:
        course_description = modulestore().get_course(course_key)
    except Exception:
        print("... WARNING: coruse ({}) doesn't exist in MongoDB...".format(course_key))
        continue

    if not course_description.advanced_modules:
        continue

    for index, module in enumerate(course_description.advanced_modules):
        if module == INCORRECT_NAME:
            course_description.advanced_modules[index] = CORRECT_NAME
            try:
                modulestore().update_item(course_description, _user.id)
            except Exception as e:
                print(e)
            print('... Replaced Course ({})`videoalpha` with `video` ==> {}'.format(
                course_key, ','.join(course_description.advanced_modules))
            )

    #course_description._dirty_fields


print('3) ### Checking `videoalpha` related courses, again...')
for course in CourseOverview.objects.all():
    course_key = course.id
    try:
        course_description = modulestore().get_course(course_key)
    except Exception:
        print("... WARNING: coruse ({}) doesn't exist in MongoDB...".format(course_key))
        continue

    if not course_description.advanced_modules:
        continue

    for module in course_description.advanced_modules:
        if module == INCORRECT_NAME:
            print('... `videoalpha` still exists in Course ({}) ==> {}'.format(course_key))
