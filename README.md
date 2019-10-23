# Info

Private Docker registry cleanup tool.

Supposed to be triggered with GitLab webhook on push event.

Note that as for docker registry `v2.4.x`, this tools itself does not actually remove blobs, it just mark them as unused. Run garbage [collection process](https://docs.docker.com/registry/garbage-collection/) to truly remove data from disk.

# Usage

## Running

```sh
docker run -d --name docker-registry-cleanup \
  -p 80:5000 \
  agrrh/docker-registry-cleanup
```

#### Environment variables

- `DRC_CONFIG_PATH` - config file to use, defaults to `./config.yml`
- `DRC_LISTEN_HOST` - address to bind to, defaults to `0.0.0.0`
- `DRC_LISTEN_PORT` - address to bind to, defaults to `5000`
- `DRC_DEBUG` - set to `yes` or `true` to run in debug mode

## Testing

Using [httpie](https://httpie.org/):

```sh
http POST :8080/event @./res/sample_payload/gitlab/push.json
```

## Configuration

Tool is configured via `config.yml`:

##### `<config>`

```yaml
projects:
  - <project>
  - <project>
```

##### `<project>`

```yaml
- name: myproject
  gitlab:
    secret_token: ''  # Use if specified in GitLab > Settings > Integrations
  registry:
    verify_ssl: false
  images:
    - repository: my/project
      rules:
        - <rule>
        - <rule>
        - <rule>
```

Recommended ruleset scheme is:

```yaml
rules:
  - action: remove
  - action: save
    regexp: '^.*$'
    order: created
    limit: 20
```


##### `<rule>`

First rule is default policy and *must* contain single `action` directive:

```yaml
- action: remove
```

If default rules is `remove`, it will never remove `:latest` tag if it exists.

Let's say, we are pushing tags in `branch_name.pipeline_id` format. Then other rules would define saving actions to preserve sane amount of images, e.g. save 10 newest tags matching `master.[0-9]+` regular expression:

```yaml
- action: save
  regexp: '^master\.[0-9]+$'
  order: created
  limit: 10
```

Also we would like to save some newest images across rest of tags. Consider 40 as reasonable amount and add following rule:

```yaml
- action: save
  regexp: '^(?!master).*$'
  order: created
  limit: 40
```

It's also possible to add more `remove` rules. In case some images matches both `remove` and `save` rules, default action would take precedence.
