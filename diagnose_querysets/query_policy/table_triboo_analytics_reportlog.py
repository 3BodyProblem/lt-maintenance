from .interface import _QueryPolicyInterface


class _TribooAnalyticsReportLogQureyPolicy(_QueryPolicyInterface):
    """For maintenance script.
    """
    QUERY_SQL = r'SELECT * FROM triboo_analytics_reportlog WHERE date(created)>="{}";'

    def __init__(self):
        super(_TribooAnalyticsReportLogQureyPolicy, self).__init__(
            policy_name='triboo_analytics_reportlog',
            policy_obj=self
        )

    def mysql_response_validator(self, resp_of_my_sql):
        if 'modified' not in resp_of_my_sql or 'learner_visit' not in resp_of_my_sql or 'learner_course' not in resp_of_my_sql:
            exc_msg = r'[Query Exception] {} : {}'.format(self._query_sql, resp_of_my_sql)
            print(exc_msg)
            return exc_msg

    def as_sql(self):
        since_date = raw_input(
            r'Please Enter Datetime for SQL "{}" : '.format(self.QUERY_SQL)
        )
        return self.QUERY_SQL.format(since_date)
