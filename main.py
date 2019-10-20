import os

from lib.config import Config
from lib.project import Project

from flask import Flask, request
from docker_registry_client import (
    # DockerRegistryClient,
    BaseClient as DockerRegistryBaseClient,
    Repository as DockerRegistryRepository
)


config_path = os.environ.get('DRC_CONFIG_PATH', './config.yml')
config = Config(config_path)

verify_ssl = os.environ.get('DRC_VERIFY_SSL', '').lower() in ('', 'true', 'yes')

app = Flask(__name__)


@app.route('/event', methods=['POST'])
def event_accept():
    webhook_token = request.headers.get('X-Gitlab-Token')
    webhook_name = request.json.get('project', {}).get('name')

    if webhook_name not in (p.get('name') for p in config.projects):
        return 'Project not found', 404

    [project] = [
        Project(**p)
        for p
        in config.projects
        if p.get('name') == webhook_name
    ]

    if (
        project.gitlab.secret_token and
        project.gitlab.secret_token != webhook_token
    ):
        return 'Must provide correct token for this project', 401

    registry_client = DockerRegistryBaseClient(
        project.registry.address,
        verify_ssl=verify_ssl
    )
    repository = DockerRegistryRepository(registry_client, project.registry.repository)

    project.registry.tags_list = repository.tags()

    return project.registry.tags_list


if __name__ == '__main__':
    app.run(
        host='0.0.0.0'
    )
