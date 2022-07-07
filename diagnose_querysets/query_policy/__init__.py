from .interface import policy_manager
from .table_auth_group import _AuthGroupQureyPolicy
from .table_triboo_analytics_reportlog import _TribooAnalyticsReportLogQureyPolicy


# Register policies to Policy Manager Cls.
_supported_policies = [
    _AuthGroupQureyPolicy(),
    _TribooAnalyticsReportLogQureyPolicy()
]
