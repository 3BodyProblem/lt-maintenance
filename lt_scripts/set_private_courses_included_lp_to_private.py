"""
    A script to check full public LPs using private courses, then set these LPs as private

"""
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


print('### [1] Querying non-private LPs............')
ps = [p for p in PartialProgram.query({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$nin': [DEF_VISIBILITY_PRIVATE]} })]
print('****** [1.1] Count of LPs : {}'.format(len(ps)))
for p in ps:
    if is_private_course_in_LP(p):
        print('****** Private Course included in Program {} : {}'.format(p['title'], p['uuid']))
        p['visibility'] = DEF_VISIBILITY_PRIVATE
        p.save()

print('### [2] Querying non-private Draft LPs............')
dps = [p for p in DraftPartialProgram.query({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$nin': [DEF_VISIBILITY_PRIVATE]} })]
print('****** [1.2] Count of Draft LPs : {}'.format(len(ps)))
for p in dps:
    if is_private_course_in_LP(p):
        print('****** Private Course included in Draft Program {} : {}'.format(p['title'], p['uuid']))
        p['visibility'] = DEF_VISIBILITY_PRIVATE
        p.save()

print('### [3] Done.')
