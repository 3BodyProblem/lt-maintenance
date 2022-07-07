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

    def as_sql(self):
        since_date = raw_input(
            r'Please Enter Datetime for SQL "{}" : '.format(self.QUERY_SQL)
        )
        return self.QUERY_SQL.format(since_date)
