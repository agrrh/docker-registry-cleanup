from lib.cleanup import CleanupRuleSet


class RegistryConfig(object):
    """RegistryConfig object.

    Related config part:

    ```
    address: http://127.0.0.1:5000/
    credentials: ''
    rules:
      # default action
      - action: remove
      # save LIMIT newest "master.[0-9]+" tags
      - action: save
        regexp: '^master\.[0-9]+$'
        order: age
        limit: 10
      # save LIMIT newest across non-master tags
      - action: save
        regexp: '^(?!master).*$'
        order: age
        limit: 40
    ```
    """

    def __init__(self, **kwargs):
        self.address = kwargs.get('address', 'http://127.0.0.1:5000/')
        self.credentials = kwargs.get('credentials', '')
        self.repository = kwargs.get('repository', '')
        self.rules = CleanupRuleSet(kwargs.get('rules', []))

        if not self.repository:
            raise Exception
