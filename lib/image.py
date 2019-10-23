import json

from multiprocessing.dummy import Pool as ThreadPool

from lib.rule import CleanupRuleSet


class Image(object):
    """Image object."""

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger')

        self.logger.debug('initializing image "{repository}"'.format(**kwargs))

        self.repository = kwargs.get('repository', '')
        self.registry_client = kwargs.get('registry_client')
        self.rules = CleanupRuleSet(kwargs.get('rules', []))

        if not self.repository or not self.registry_client or not self.rules:
            raise Exception

        self.client = self.registry_client.repository(self.repository)

        self.tags = []
        tags_list = self.client.tags()
        self.logger.debug('found {} tags'.format(len(tags_list)))

        pool = ThreadPool(32)

        self.tags = list(filter(
            None,
            pool.map(self._tag_get, tags_list)
        ))

        self.tags_save = []
        self.tags_remove = []
        self.tags_after = []

    def _tag_get(self, tag):
        try:
            self.logger.debug('fetching manifest for tag "{}"'.format(tag))

            manifest_v1 = self.client.manifest(tag)
            manifest_v2 = self.client.manifest_v2(tag)

            tag_object = ImageTag(
                name=tag,
                manifest=manifest_v1,
                manifest_v2=manifest_v2,
                client=self.client
            )
        except Exception as e:
            self.logger.error(e)
            tag_object = None

        return tag_object

    def _tag_remove(self, tag):
        if tag in self.tags_save:
            self.logger.warning("not removing {}:{} image since it's explicitly set to be saved".format(self.repository, tag.name, tag.sha))
            return False

        try:
            self.logger.warning('removing {}:{} image by digest {}'.format(self.repository, tag.name, tag.sha))
            self.client.delete_manifest(tag.sha)
        except Exception as e:
            self.logger.error(e)

        return True

    def cleanup_plan(self):
        (
            self.tags_save,
            self.tags_remove,
            self.tags_after,
        ) = self.rules.plan(self.tags)

        return {
            '_policy': self.rules.default.action,
            'after': sorted([t.name for t in self.tags_after]),
            'before': sorted([t.name for t in self.tags]),
            'explicit_save': sorted([t.name for t in self.tags_save]),
            'explicit_remove': sorted([t.name for t in self.tags_remove]),
        }

    def cleanup(self):
        plan = self.cleanup_plan()

        tags_to_remove_by_policy = {
            'save': [t for t in self.tags_remove if t not in self.tags_save],
            'remove': [t for t in self.tags if t not in self.tags_save],
        }
        tags_to_remove = tags_to_remove_by_policy.get(self.rules.default.action, [])

        pool = ThreadPool(8)

        pool.map(self._tag_remove, tags_to_remove)

        return plan


class ImageTag(object):
    """RepositoryTag object."""

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.manifest, _ = kwargs.get('manifest')
        _, self.sha = kwargs.get('manifest_v2')

        if not self.name or not self.manifest:
            raise Exception

        self.created = self.__extract_created()

    def __extract_created(self):
        # https://github.com/docker/distribution/blob/master/docs/spec/manifest-v2-1.md#example-manifest
        history = self.manifest.get('history', [])
        newest_layer = history[0]
        layer_info = json.loads(newest_layer.get('v1Compatibility', '{}'))
        created = layer_info.get('created')

        return created
