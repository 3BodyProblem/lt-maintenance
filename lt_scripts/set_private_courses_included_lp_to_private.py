"""
    A script to check ( "Public" + "Accessible by URL" ) LPs using private courses, then set these LPs as private

    Usage: `python manage.py lms shell --settings=aws < set_private_courses_included_lp_to_private.py`
    Sample ===> : ```
        edxapp@learning-tribes:~/edx-platform$ python manage.py lms shell --settings=aws < set_private_courses_included_lp_to_private.py
        ### [1] Querying non-private LPs............
        ****** [1.1] Count of LPs : 4
        ******   =========>>>  Private Course course-v1:demo+123+123 is used by LP
        ******   =========>>>  Private Course course-v1:demo+2022+12 is used by LP
        ****** Private Course included in Program TEST QUENTIN 2 : 1ebf036b-1789-4ae5-a558-2009e04df238
        ******   =========>>>  Private Course course-v1:demo+T12+2021_Q4 is used by LP
        ****** Private Course included in Program Learning Path Demo : 45a1d853-947c-4566-bf1a-ae6560cbc579
        ### [2] Querying non-private Draft LPs............
        ****** [1.2] Count of Draft LPs : 4
        ******   =========>>>  Private Course course-v1:demo+123+123 is used by LP
        ******   =========>>>  Private Course course-v1:demo+2022+12 is used by LP
        ****** Private Course included in Draft Program TEST QUENTIN 2 : 1ebf036b-1789-4ae5-a558-2009e04df238
        ******   =========>>>  Private Course course-v1:demo+T12+2021_Q4 is used by LP
        ****** Private Course included in Draft Program Learning Path Demo : 45a1d853-947c-4566-bf1a-ae6560cbc579
        ### [3] Using Mysql Db Name : learning-demo_discovery
        ****** [Done] Program (1ebf036b-1789-4ae5-a558-2009e04df238) in Mysql.
        ****** [Done] Program (45a1d853-947c-4566-bf1a-ae6560cbc579) in Mysql.
        ### [4] Done.

        Then we saw that
            the LP( https://studio-demo.triboolearning.com/program_detail/?program_uuid=1ebf036b-1789-4ae5-a558-2009e04df238 ) has been set as "Private" from "Public".
    ```

"""
from django.db import connection
from lms.djangoapps.program_enrollments.persistance.programs import PartialProgram, DraftPartialProgram
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore


DEF_VISIBILITY_FULL_PUBLIC = 0
DEF_VISIBILITY_ACCESSIBLE = 1
DEF_VISIBILITY_PRIVATE = 2


def is_private_course(course_id):
    course_descriptor = modulestore().get_course(CourseKey.from_string(course_id))
    if 'none' == course_descriptor.catalog_visibility:
        return True

    return False


def is_private_course_in_LP(program):
    private_course_ids = []
    for course in program['courses']:
        for run in course['course_runs']:
            if is_private_course(run['key']):
                private_course_ids.append(run['key'])

    for i in private_course_ids:
        print('******   =========>>>  Private Course {} is used by LP'.format(i))

    return True if private_course_ids else False


discovery_mysql_db_name = None
with connection.cursor() as cursor:
    cursor.execute('show databases;')
    for r in cursor.fetchall():
        if r[0].endswith('_discovery') == True:
            discovery_mysql_db_name = r[0]

if not discovery_mysql_db_name:
    raise Exception('Error: Mysql Db Name is empty!')

program_uuids = set()

print('### [1] Querying non-private LPs............')
ps = [p for p in PartialProgram.query({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$nin': [DEF_VISIBILITY_PRIVATE]} })]
print('****** [1.1] Count of LPs : {}'.format(len(ps)))
for p in ps:
    if is_private_course_in_LP(p):
        print('****** Private Course included in Program {} : {}'.format(p['title'].encode('utf-8'), p['uuid']))
        program_uuids.add(p['uuid'])
        p['visibility'] = DEF_VISIBILITY_PRIVATE
        p.save()

print('### [2] Querying non-private Draft LPs............')
dps = [p for p in DraftPartialProgram.query({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$nin': [DEF_VISIBILITY_PRIVATE]} })]
print('****** [1.2] Count of Draft LPs : {}'.format(len(ps)))
for p in dps:
    if is_private_course_in_LP(p):
        print('****** Private Course included in Draft Program {} : {}'.format(p['title'].encode('utf-8'), p['uuid']))
        program_uuids.add(p['uuid'])
        p['visibility'] = DEF_VISIBILITY_PRIVATE
        p.save()


print('### [3] Using Mysql Db Name : {}'.format(discovery_mysql_db_name))
with connection.cursor() as cursor:
    cursor.execute('use `{}`;'.format(discovery_mysql_db_name))
    for uuid in program_uuids:
        cursor.execute(
            "update course_metadata_program set visibility=2 where uuid='{}' and visibility<>2".format(
                uuid.replace('-', '')
            )
        )
        cursor.execute(
            "select count(1) from course_metadata_program where uuid='{}' and visibility=2".format(
                uuid.replace('-', '')
            )
        )
        affected_num = cursor.fetchone()[0]
        if 1 == affected_num:
            print('****** [Done] Program ({}) in Mysql.'.format(uuid))
        else:
            raise Exception('Failed to update Mysql table course_metadata_program : {}  ({})'.format(uuid, affected_num))


print('### [4] Done.')
