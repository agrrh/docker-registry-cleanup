class Project(object):
    """Project object."""

    """
    name: project-from-other-registry
    gitlab:
      secret_token: 'something'
    registry:
      address: https://registry.example.org
      credentials: 'admin:pass'
      repository: foo
      rules:
        # default action
        - action: save
        # remove images leaving LIMIT newest
        - action: remove
          order: age
          limit: 20
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.gitlab = GitlabConfig(kwargs.get('gitlab'))
        self.registry = RegistryConfig(kwargs.get('gitlab'))