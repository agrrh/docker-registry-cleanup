class GitlabConfig(object):
    """GitlabConfig object.

    Related config part:

    ```
    gitlab:
      secret_token: 'something'
    ```
    """
    def __init__(self, **kwargs):
        self.secret_token = kwargs.get('secret_token')
