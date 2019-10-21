import os

from lib.config import Config
from lib.project import Project

from flask import Flask, request

config_path = os.environ.get('DRC_CONFIG_PATH', './config.yml')
config = Config(config_path)

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

    project.registry.process()

    return {
        'tags': {
            'all': project.registry.tags_list,
            'remove': project.registry.tags_delete_list,
            'save': project.registry.tags_save_list,
        },
    }, 202


if __name__ == '__main__':
    host = os.environ.get('DRC_LISTEN_HOST', '0.0.0.0')
    port = os.environ.get('DRC_LISTEN_PORT', '5000')
    debug = os.environ.get('DRC_DEBUG', '').lower() in ('', 'true', 'yes')

    app.run(
        host=host,
        port=port,
        debug=debug
    )
