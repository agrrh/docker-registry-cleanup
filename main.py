import os
import logging

from lib.config import Config
from lib.project import Project

from flask import Flask, request


host = os.environ.get('DRC_LISTEN_HOST', '0.0.0.0')
port = os.environ.get('DRC_LISTEN_PORT', '5000')
debug = os.environ.get('DRC_DEBUG', '').lower() in ('', 'true', 'yes')


def logger_init():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if debug else logging.WARNING)

    handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s | %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = logger_init()

config_path = os.environ.get('DRC_CONFIG_PATH', './config.yml')
config = Config(config_path)

app = Flask(__name__)


@app.route('/event', methods=['POST'])
def event_accept():
    webhook_token = request.headers.get('X-Gitlab-Token')
    webhook_name = request.json.get('project', {}).get('path_with_namespace')

    if webhook_name not in (p.get('name') for p in config.projects):
        return 'Project not found', 404

    [project] = [
        Project(**p, logger=logger)
        for p
        in config.projects
        if p.get('name') == webhook_name
    ]

    if (
        project.gitlab.secret_token and
        project.gitlab.secret_token != webhook_token
    ):
        return 'Must provide correct token for this project', 401

    return {
        image.repository: (
            image.cleanup_plan() if request.args.get('fake') else image.cleanup()
        )
        for image
        in project.images
    }, 202


if __name__ == '__main__':
    app.run(
        host=host,
        port=port,
        debug=debug
    )
