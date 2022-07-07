from .interface import _QueryPolicyInterface


class _AuthGroupQureyPolicy(_QueryPolicyInterface):
    """Query Sql ==> select `name` from auth_group;
    """
    QUERY_SQL = r'select `name` from auth_group;'

    def __init__(self):
        super(_AuthGroupQureyPolicy, self).__init__(
            policy_name='auth_group',
            policy_obj=self
        )

    def as_sql(self):
        return self.QUERY_SQL
