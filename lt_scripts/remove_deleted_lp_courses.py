
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
