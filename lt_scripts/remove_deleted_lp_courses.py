"""
    - Steps:
     1. Get all LP records missing new field `course_metadata_program.visibility`
     2. Get all deleted(invalid) courses from LPs and remove them from LPs
     3. Save all LPs.

    - Usage : `python manage.py lms shell --settings=aws < remove_deleted_lp_courses.py`
        Sample ===> :
        ```
        edxapp@learning-tribes:~/edx-platform$ python manage.py lms shell --settings=aws < remove_deleted_lp_courses.py
        ### [1] Querying field visibility missed records of Programs............
        ****** [1.1] Count of LPs : 1
        ****** Course [Teste Scorm] / [course-v1:marelli+1000+20211119] would be removed from LP [Minha Primeira Trilha]
        ****** Course [Teste Scorm 2] / [course-v1:marelli+1000+20220111] would be removed from LP [Minha Primeira Trilha]
        ****** LP : Minha Primeira Trilha saved
        ### [2] Querying field visibility missed records of Draft Programs............
        ****** [2.1] Count of Draft LPs : 1
        ****** Course [Teste Scorm] / [course-v1:marelli+1000+20211119] would be removed from LP [Minha Primeira Trilha]
        ****** Course [Teste Scorm 2] / [course-v1:marelli+1000+20220111] would be removed from LP [Minha Primeira Trilha]
        ****** Draft LP : Minha Primeira Trilha saved
        ### [3] Done.
        ```

"""
from django.core.exceptions import ValidationError
from lms.djangoapps.program_enrollments.persistance.connection import MongoDbConnectionsManager
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey


mongo_db = MongoDbConnectionsManager.get_manager().get_connection_by_dbname('programs')
programs = mongo_db['program_set']
draft_programs = mongo_db['draft_program_set'] 


def save(collection, p_object_data, ignored_fields=None):
    """Save data into a MongoDB collection

        @param collection:          MongoDb collection
        @type collection:           PyMongo Collection Object
        @param p_object_data:       program dict
        @type p_object_data:        dict
        @param ignored_fields:      ignored fields names set (the data of these fields would not be saved)
        @type ignored_fields:       set
    """
    if not p_object_data['_id']:
        raise ValidationError('MongoDB record primary key (`_id`) cannot be empty.')

    DEF_FIELD_NULL_VALUE = 'is_null'    # Defined in file `program_enrollments/persistance/persistent_object.py`
    ignored_fields = set() \
        if not ignored_fields else ignored_fields

    return collection.update(
        {r'_id': p_object_data[r'_id']},
        {
            '$set': {
                fd: None if DEF_FIELD_NULL_VALUE == val else val
                for fd, val in p_object_data.items()
                if val is not None and fd not in ignored_fields     # Ignore `None` Value while updating.
            }
        },
        upsert=True
    )


def remove_invalid_lp_courses(program_dict):
    def _course_exists(course_id, p_title, c_title):
        c_exist = CourseOverview.objects.filter(
            pk=CourseKey.from_string(course_id)
        ).exists()

        if not c_exist:
            print('****** Course [{}] / [{}] would be removed from LP [{}]'.format(c_title, course_id, p_title))

        return c_exist

    program_dict['courses'] = [course for course in program_dict['courses'] for run in course['course_runs'] if _course_exists(run['key'], program_dict['title'].encode('utf-8'), course['title'].encode('utf-8'))]


ps  = [p for p in programs.find({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$exists': False} })]
dps  = [p for p in draft_programs.find({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$exists': False} })]

print('### [1] Querying field visibility missed records of Programs............')
print('****** [1.1] Count of LPs : {}'.format(len(ps)))
for p in ps:
    remove_invalid_lp_courses(p)
    save(programs, p)
    print('****** LP : {} saved'.format(p['title']))

print('### [2] Querying field visibility missed records of Draft Programs............')
print('****** [2.1] Count of Draft LPs : {}'.format(len(dps)))
for p in dps:
    remove_invalid_lp_courses(p)
    save(draft_programs, p)
    print('****** Draft LP : {} saved'.format(p['title']))

print('### [3] Done.')
