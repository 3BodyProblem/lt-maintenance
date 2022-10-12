"""
    - Steps:
     1. Get all LP records missing new field `course_metadata_program.visibility`
     2. Add field `visibility` and assign with value `0`(Public LP)
     3. Save all LPs.

    - Usage : `python manage.py lms shell --settings=aws < add_field_visibility.py`
        Sample ===> :
        ```
        edxapp@learning-tribes:~/edx-platform$ python manage.py lms shell --settings=aws < add_field_visibility.py
        ### [1] Querying field visibility missed records............
        ****** [1.1] Count of LPs : 5
        ****** LP : Test Non Started Path saved
        ****** LP : Aaron Test Learning Path saved
        ****** LP : barry_test_1024_abc saved
        ****** LP : test_barry_program_1024 saved
        ****** LP : NEW LP - Change Course After LP Published saved
        ****** [1.2] Count of Draft LPs : 5
        ****** Draft LP : Test Non Started Path saved
        ****** Draft LP : Aaron Test Learning Path saved
        ****** Draft LP : barry_test_1024_abc saved
        ****** Draft LP : test_barry_program_1024 saved
        ****** Draft LP : NEW LP - Change Course After LP Published saved
        ****** Draft LP : BARRY___UMA_Pro_Ambienteculturalypoliticoennegociosinternacionales_barry saved
        ### [2] Done.
        ```

"""
from lms.djangoapps.program_enrollments.persistance.programs import PartialProgram, DraftPartialProgram


print('### [1] Querying field visibility missed records............')
ps = [p for p in PartialProgram.query({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$exists': False} })]

print('****** [1.1] Count of LPs : {}'.format(len(ps)))
for p in ps:
    p['visibility'] = 0
    p.save()
    print('****** LP : {} saved'.format(p['title'].encode('utf-8')))

dps = [p for p in DraftPartialProgram.query({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$exists': False} })]
print('****** [1.2] Count of Draft LPs : {}'.format(len(ps)))
for p in dps:
    p['visibility'] = 0
    p.save()
    print('****** Draft LP : {} saved'.format(p['title'].encode('utf-8')))

print('### [2] Done.')
