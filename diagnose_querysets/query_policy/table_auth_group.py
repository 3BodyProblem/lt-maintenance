from .interface import _QueryPolicyInterface


class _AuthGroupQureyPolicy(_QueryPolicyInterface):
    """Query Sql ==> select `name` from auth_group;
    """
    QUERY_SQL = r'SELECT `name` FROM auth_group;'

    def __init__(self):
        super(_AuthGroupQureyPolicy, self).__init__(
            policy_name='auth_group',
            policy_obj=self
        )

    def mysql_response_validator(self, resp_of_my_sql):
        if 'rows in set' not in resp_of_my_sql:
            exc_msg = r'[Query Exception] {} : {}'.format(self._query_sql, resp_of_my_sql)
            print(exc_msg)
            return exc_msg

    def as_sql(self):
        return self.QUERY_SQL
