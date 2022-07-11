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
        self._since_date = None

    def mysql_response_validator(self, resp_of_my_sql):
        if 'modified' not in resp_of_my_sql or 'learner_visit' not in resp_of_my_sql or 'learner_course' not in resp_of_my_sql:
            exc_msg = r'[Query Exception] {} : {}'.format(self.QUERY_SQL, resp_of_my_sql)
            print(exc_msg)
            return exc_msg

    def on_prepare(self):
        self._since_date = raw_input(
            r'Please Enter Datetime for SQL "{}" <--- [YYYY-MM-dd] :'.format(self.QUERY_SQL)
        )
        if not self._since_date:
            raise ValueError(r'[Exception] Empty date, pls input a valid datetime')

        print(r'[Query SQL] ==> {}'.format(self.as_sql()))

    def as_sql(self):
        return self.QUERY_SQL.format(self._since_date)
