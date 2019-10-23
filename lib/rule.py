import re
import logging


class CleanupRuleSet(object):
    """CleanupRuleSet object.

    Related config part:

    ```
    - action: remove
    - action: save
      regexp: '^master\.[0-9]+$'
      order: created
      limit: 10
    - action: save
      regexp: '^(?!master).*$'
      order: created
      limit: 40
    ```
    """

    def __init__(self, rules_config_list):
        if not rules_config_list:
            raise Exception

        self.default = CleanupRule(**rules_config_list[0])
        self.rules = [
            CleanupRule(**rule)
            for rule
            in rules_config_list[1:]
        ]

    def plan(self, tags):
        tags_save = tags[:] if self.default.action == 'save' else []
        tags_remove = []

        # Get latest tag if it exists
        tag_latest = next(
            filter(lambda t: t.name == 'latest', tags),
            None
        )

        for rule in self.rules:
            tags_match = rule.apply(tags, self.default)

            tags_save += tags_match if rule.action == 'save' else []
            tags_remove += tags_match if rule.action == 'remove' else []

        tags_save = list(set(tags_save))
        tags_remove = list(set(tags_remove))

        tags_remove = list(filter(lambda t: t.name != 'latest', tags_remove))

        if self.default.action == 'remove':
            tags_after = [t for t in tags_save if t not in tags_remove]
            if tag_latest:
                tags_save += [tag_latest]
                tags_after += [tag_latest]
        if self.default.action == 'save':
            tags_after = [t for t in tags if t not in tags_remove]

        return (tags_save, tags_remove, tags_after)


class CleanupRule(object):
    """CleanupRule object.

    Related config part:

    ```
    action: save
    regexp: '^.*$'
    order: created
    limit: 10
    ```
    """
    ORDER_POSSIBLE_VALUES_LIST = ('created',)

    def __init__(self, **kwargs):
        self.action = kwargs.get('action')

        if not self.action:
            raise Exception

        self.regexp = kwargs.get('regexp', r'^.*$')
        self.order = kwargs.get('order', 'created')

        if self.order not in self.ORDER_POSSIBLE_VALUES_LIST:
            raise Exception

        self.limit = kwargs.get('limit', 10)

    def apply(self, tags, default_rule):
        logging.debug('applying rule {} "{}" with limit of "{}"'.format(self.action, self.regexp, self.limit))

        tags = tags[:]

        tags_match = []
        for t in tags:
            if t.name == 'latest':
                continue
            elif re.match(self.regexp, t.name):
                logging.debug('+ tag "{}" matched'.format(t.name))
                tags_match.append(t)
            else:
                logging.debug('- tag "{}" not matched'.format(t.name))

        tags_match.sort(
            key=lambda t: getattr(t, self.order),
            reverse=True  # latest first
        )

        return tags_match[:self.limit]
