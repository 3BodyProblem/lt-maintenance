

class Verification(object):
    """Verification of analytics"""
    def __init__(self, nodes_settings):
        """Constrctor

            @param nodes_settings:      nodes settings of Mysql / SSL of each AWS Node Instances.
            @type nodes_settings:       iterable object.
        """
        self._nodes_settings = nodes_settings

    def execute(self):
        for node in self._nodes_settings:
            print(node)
