from lib.config import Config

from flask import Flask, request
from docker_registry_client import DockerRegistryClient


config = Config('./config.yml')

app = Flask(__name__)


@app.route('/event', methods=['POST'])
def event_accept():
    webhook_token = request.headers.get('X-Gitlab-Token')
    webhook_name = request.json.get('project', {}).get('name')

    if webhook_name not in (p.get('name') for p in config.projects):
        return 'Project not found', 404

    [project_config] = [p for p in config.projects if p.get('name') == webhook_name]

    print(project_config)

    if (
        project_config.get('gitlab').get('secret_token') and
        project_config.get('gitlab').get('secret_token') != webhook_token
    ):
        return 'Must provide correct token for this project', 401

    return 'Hello, World!'


if __name__ == '__main__':
    app.run(
        host='0.0.0.0'
    )
