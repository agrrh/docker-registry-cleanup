from docker_registry_client import DockerRegistryClient


class RegistryConfig(object):
    """RegistryConfig object.

    Related config part:

    ```
    address: http://127.0.0.1:5000/
    credentials: ''
    ```
    """

    def __init__(self, **kwargs):
        self.address = kwargs.get('address', 'http://127.0.0.1:5000/')
        self.verify_ssl = kwargs.get('verify_ssl', True)
        self.api_version = kwargs.get('api_version', 2)
        self.credentials = kwargs.get('credentials', '')

        self._client = DockerRegistryClient(self.address, verify_ssl=self.verify_ssl, api_version=self.api_version)
