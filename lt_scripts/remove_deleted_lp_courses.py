"""
    - Steps:
     1. Get all LP records missing new field `course_metadata_program.visibility`
     2. Add field `visibility` and assign with value `0`(Public LP)
     3. Save all LPs.

    - Usage : `python manage.py lms shell --settings=aws < remove_deleted_lp_courses.py`
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
from django.core.exceptions import ValidationError
from lms.djangoapps.program_enrollments.persistance.connection import MongoDbConnectionsManager


mongo_db = MongoDbConnectionsManager.get_manager().get_connection_by_dbname('programs')
programs = mongo_db['program_set']
draft_programs = mongo_db['draft_program_set'] 

ps  = [p for p in programs.find({'partner': {'$nin': [u'never_exis_abc']}, 'visibility': {'$exists': False} })]  


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
