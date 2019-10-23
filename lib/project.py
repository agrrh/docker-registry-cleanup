from lib.gitlab import GitlabConfig
from lib.registry import RegistryConfig
from lib.image import Image


class Project(object):
    """Project object.

    Related config part:

    ```
    name: project-from-other-registry
    gitlab:
      secret_token: 'something'
    registry:
      address: https://registry.example.org
      credentials: 'admin:pass'
    images:
      - repository: foo
        rules:
          - action: save
          # remove images leaving LIMIT newest
          - action: remove
            order: created
            limit: 20
    ```
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

        self.name = kwargs.get('name')
        if not self.name:
            raise Exception

        self.gitlab = GitlabConfig(**kwargs.get('gitlab', {}))
        self.registry = RegistryConfig(**kwargs.get('registry', {}))
        self.images = [
            Image(**image, registry_client=self.registry._client, logger=self.logger)
            for image
            in kwargs.get('images', [])
        ]
