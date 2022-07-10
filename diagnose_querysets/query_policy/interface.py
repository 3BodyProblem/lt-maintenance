from abc import ABCMeta, abstractmethod


class _PolicyManager(object):
    """Manage all policies (Singleton)"""
    _supported_policy_list = {}     # for checking duplicated policy name
    _instance_of_singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance_of_singleton:
            cls._instance_of_singleton = super(_PolicyManager, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance_of_singleton

    def new(self, policy_name, policy_obj):
        """Add new query policy class to classes manager"""
        if policy_name in _PolicyManager._supported_policy_list:
            raise ValueError(r'[Error] Duplicate policy name : {}'.format(policy_name))

        _PolicyManager._supported_policy_list[policy_name] = policy_obj

    @property
    def supported_policies(self):
        """Return supported policies string seperated by comma

            @return     list of supported policy names
            @rtype:     list
        """
        return [policy_name for policy_name in _PolicyManager._supported_policy_list.keys()]

    def get_policy_obj_by_name(self, policy_name):
        """Return policy class by name

            @return     class of query policy
            @rtype:     subclass of class `_QueryPolicyInterface`
        """
        policy_obj = _PolicyManager._supported_policy_list.get(policy_name)
        if not policy_obj:
            raise KeyError(r'[Error] Invalid policy name : {}'.format(policy_name))

        return policy_obj


policy_manager = _PolicyManager()


class _QueryPolicyInterface(object):
    """Base class for all mongodb record object."""
    __metaclass__ = ABCMeta

    def __init__(self, policy_name, policy_obj):
        """Construct a query policy obj.
            &
            Register Kinds of Subclass of it to policy manager.

            @param policy_name:     supported query policy name ( passed from Derived class )
            @type policy_name:      string
            @param policy_obj:      instance of subclass
            @type policy_obj:       subclass
            @return:                Instance of Derived class from `QueryPolicyInterface`
            @rtype:                 Subclass of `QueryPolicyInterface`
        """
        if not policy_name:
            raise ValueError(r'Policy name cannot be empty')

        if not isinstance(policy_obj, _QueryPolicyInterface):
            raise ValueError(r'[Error] Class {} is not subclass of class `_QueryPolicyInterface`'.format(policy_obj))

        policy_manager.new(policy_name, policy_obj)
        self._policy_name = policy_name

    @property
    def policy_name(self):
        """Return policy name"""
        return self._policy_name

    @abstractmethod
    def on_prepare(self):
        """event before execute query policy"""
        raise NotImplementedError

    @abstractmethod
    def as_sql(self):
        """Return Query Sql

            @return:        SQL
            @rtype:         string
        """
        raise NotImplementedError

    @abstractmethod
    def mysql_response_validator(self):
        """Validate mysql response, raise Exception `ValueError` while got invalid response from Mysql Sql

            @return:        None, if no exception occured
            @rtupe          string or None
        """
        raise NotImplementedError
