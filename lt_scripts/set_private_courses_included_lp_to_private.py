"""
    A script to check full public LPs using private courses, then set these LPs as private

"""
from lms.djangoapps.program_enrollments.persistance.programs import PartialProgram, DraftPartialProgram


DEF_VISIBILITY_FULL_PUBLIC = 0
DEF_VISIBILITY_ACCESSIBLE = 1
DEF_VISIBILITY_PRIVATE = 2


print('### [1] Querying non-private LPs............')
ps = [p for p in PartialProgram.query({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$nin': [DEF_VISIBILITY_PRIVATE]} })]
print('****** [1.1] Count of LPs : {}'.format(len(ps)))
for p in ps:
    print('****** Program {} : {}'.format(p['title'], p['uuid']))

print('### [2] Querying non-private Draft LPs............')
dps = [p for p in DraftPartialProgram.query({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$nin': [DEF_VISIBILITY_PRIVATE]} })]
print('****** [1.2] Count of Draft LPs : {}'.format(len(ps)))
for p in dps:
    print('****** Draft Program {} : {}'.format(p['title'], p['uuid']))

print('### [3] Done.')
