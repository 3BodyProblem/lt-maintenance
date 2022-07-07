from .interface import policy_manager
from .table_auth_group import _AuthGroupQureyPolicy


# Register policies to Policy Manager Cls.
_supported_policies = [
    _AuthGroupQureyPolicy(),
]
