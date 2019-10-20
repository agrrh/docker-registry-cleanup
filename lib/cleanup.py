class CleanupRuleSet(object):
    """CleanupRuleSet object.

    Related config part:

    ```
    - action: remove
    - action: save
      regexp: '^master\.[0-9]+$'
      order: age
      limit: 10
    - action: save
      regexp: '^(?!master).*$'
      order: age
      limit: 40
    ```
    """

    def __init__(self, rules_config_list):
        if not rules_config_list:
            raise Exception

        self.default = CleanupRule(**rules_config_list[0])
        self.rules = [
            CleanupRule(**rule)
            for rule
            in rules_config_list[1:]
        ]


class CleanupRule(object):
    """CleanupRule object.

    Related config part:

    ```
    action: save
    regexp: '^(?!master).*$'
    order: age
    limit: 40
    ```
    """
    ORDER_POSSIBLE_VALUES_LIST = ('age',)

    def __init__(self, **kwargs):
        self.action = kwargs.get('action')

        if not self.action:
            raise Exception

        self.regexp = kwargs.get('regexp', r'^.*$')
        self.order = kwargs.get('order', 'age')
        if self.order not in self.ORDER_POSSIBLE_VALUES_LIST:
            raise Exception

        self.limit = kwargs.get('limit', 10)
