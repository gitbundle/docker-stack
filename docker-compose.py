# NOTE: install yaml module first
import yaml

bundleBuildsServerDependsOn = [
    "db",
    "redis-server",
    "gitbundle",
    "nsq",
]

gitbundleDependsOn = [
    # {
    #     "db": {
    #         "condition": "service_healthy",
    #     }
    # },
    "db",
    "nsq",
    "redis-server",
]


def haproxyDependsOn():
    return [
        "gitbundle",
    ]


def commonVolumes():
    return [
        "/etc/localtime:/etc/localtime:ro",  # sync localtime to container, worked for linux
        "/etc/hosts:/etc/hosts:ro",  # this maybe no need, when you have real-network domains
    ]


def containerVolumes(vs):
    return vs + commonVolumes()


def main():
    return {
        "version": "3.8",
        "services": {
            "gitbundle": gitbundle(gitbundleDependsOn, "gitbundle", "gitbundle/gitbundle"),
            "bundle-deployments": bundlePluginServer("BUNDLE_DEPLOYMENTS", ["db", "gitbundle", "redis-server", "nsq"]),
            "bundle-pods": bundlePluginServer("BUNDLE_PODS", ["db", "gitbundle", "redis-server", "nsq"]),
            "bundle-metrics": bundlePluginServer("BUNDLE_METRICS", ["db", "gitbundle", "redis-server", "nsq"]),
            "bundle-builds": bundleBuildsServer(bundleBuildsServerDependsOn),
            "bundle-runner-amd64": bundleRunnerServer("amd64", ["bundle-builds"]),
            # "bundle-runner-arm64": bundleRunnerServer("arm64", ["bundle-builds"]),
            "haproxy": haproxy(haproxyDependsOn()),
            "redis-server": redisServer(),
            "nsq": nsq(),
            "db": db(),
        },
        "volumes": {
            "gitbundle-data": volume("$PWD/data/gitbundle"),
            "nsq-data": volume("$PWD/data/nsq"),
            "db-data": volume("$PWD/data/postgres"),
        },
        "networks": {
            "gitbundle-private": {
                "driver": "bridge",
            },
        },
    }


def gitbundle(dependsOn, containerName, image):
    return {
        "container_name": containerName,
        "image": image,
        "volumes": containerVolumes(
            [
                "gitbundle-data:/data",
            ]
        ),
        "environment": [
            'APP_NAME=${APP_NAME:-"GitBundle"}',
            "RUN_USER=${RUN_USER:-git}",
            "DOMAIN=${DOMAIN:-example.gitbundle.com}",
            "SSH_DOMAIN=${SSH_DOMAIN:-example.gitbundle.com}",
            "HTTP_PORT=${HTTP_PORT:-4000}",
            "ROOT_URL=${ROOT_URL:-}",
            "DISABLE_SSH=${DISABLE_SSH:-false}",
            "SSH_PORT=${SSH_PORT:-22}",
            "LFS_START_SERVER=${LFS_START_SERVER:-true}",
            "DB_TYPE=${DB_TYPE:-postgres}",
            "DB_HOST=${DB_HOST:-db:5432}",
            "DB_NAME=${DB_NAME:-gitbundle}",
            "DB_USER=${DB_USER:-postgres}",
            "DB_PASSWD=${DB_PASSWD:-postgres}",
            "DB_SCHEMA=${DB_SCHEMA:-public}",
            "SSL_MODE=${SSL_MODE:-disable}",
            "LOG_SQL=${LOG_SQL:-false}",
            "INSTALL_LOCK=${INSTALL_LOCK:-true}",
            "DISABLE_REGISTRATION=${DISABLE_REGISTRATION:-false}",
            "REQUIRE_SIGNIN_VIEW=${REQUIRE_SIGNIN_VIEW:-false}",
            "SECRET_KEY=${SECRET_KEY:-}",
            "NSQD_CLUSTER_TCP_ADDR=${NSQD_CLUSTER_TCP_ADDR:-}",
            "REDIS_CONNECTION=${REDIS_CONNECTION:-}",
        ],
        "depends_on": dependsOn,
        "restart": "always",
        "networks": networks(),
    }


# NOTE: some plugins may not have some environment variables, just ignore
def bundlePluginServer(pluginName, dependsOn):
    return {
        "container_name": "%s" % pluginName.replace("_", "-").lower(),
        "image": "gitbundle/%s" % pluginName.replace("_", "-").lower(),
        "volumes": containerVolumes([]),
        "environment": [
            # gitbundle
            "%s_GITBUNDLE_SERVER=${%s_GITBUNDLE_SERVER:-}" % (pluginName, pluginName),
            "%s_GITBUNDLE_SKIP_VERIFY=${%s_GITBUNDLE_SKIP_VERIFY:-false}" % (pluginName, pluginName),
            # database
            "%s_DATABASE_DRIVER=${%s_DATABASE_DRIVER:-}" % (pluginName, pluginName),
            "%s_DATABASE_HOST=${%s_DATABASE_HOST:-}" % (pluginName, pluginName),
            "%s_DATABASE_NAME=${%s_DATABASE_NAME:-}" % (pluginName, pluginName),
            "%s_DATABASE_USER=${%s_DATABASE_USER:-}" % (pluginName, pluginName),
            "%s_DATABASE_PASSWD=${%s_DATABASE_PASSWD:-}" % (pluginName, pluginName),
            # log
            "%s_LOGS_LEVEL=trace" % (pluginName),
            "%s_LOGS_COLOR=true" % (pluginName),
            "%s_LOGS_TEXT=true" % (pluginName),
            "%s_LOGS_CALLER=true" % (pluginName),
            # redis
            "%s_REDIS_CONNECTION=${%s_REDIS_CONNECTION:-}" % (pluginName, pluginName),
            # nsq
            "%s_NSQ_CLUSTER_TCP_ADDR=${%s_NSQ_CLUSTER_TCP_ADDR:-}" % (pluginName, pluginName),
            "%s_NSQ_AUTH_SECRET=${%s_NSQ_AUTH_SECRET:-}" % (pluginName, pluginName),
            "%s_PLUGIN_NAME=${%s_PLUGIN_NAME:-}" % (pluginName, pluginName),
            "%s_PLUGIN_TOKEN=${%s_PLUGIN_TOKEN:-}" % (pluginName, pluginName),
        ],
        "depends_on": dependsOn,
        "restart": "always",
        "networks": networks(),
    }


def bundleBuildsServer(dependsOn):
    return {
        "container_name": "bundle-builds",
        "image": "gitbundle/bundle-builds",
        "ports": [
            "8080:8080",
        ],
        "environment": [
            "BUNDLE_BUILDS_SERVER_HOST=${BUNDLE_BUILDS_SERVER_HOST:-localhost:8080}",
            "BUNDLE_BUILDS_SERVER_PORT=${BUNDLE_BUILDS_SERVER_PORT:-:8080}",
            "BUNDLE_BUILDS_SERVER_PROTO=${BUNDLE_BUILDS_SERVER_PROTO:-http}",
            "BUNDLE_BUILDS_SERVER_PROXY_HOST=${BUNDLE_BUILDS_SERVER_PROXY_HOST:-bundle-builds:8080}",  # maybe needed by gitbundle webhook
            "BUNDLE_BUILDS_SERVER_PROXY_PROTO=${BUNDLE_BUILDS_SERVER_PROXY_PROTO:-http}",
            "BUNDLE_BUILDS_RPC_SECRET=${BUNDLE_BUILDS_RPC_SECRET:-}",
            "BUNDLE_BUILDS_COOKIE_SECRET=${BUNDLE_BUILDS_COOKIE_SECRET:-}",
            "BUNDLE_BUILDS_COOKIE_TIMEOUT=${BUNDLE_BUILDS_COOKIE_TIMEOUT:-720h}",
            "BUNDLE_BUILDS_GITBUNDLE_SERVER=${BUNDLE_BUILDS_GITBUNDLE_SERVER:-https://example.gitbundle.com}",
            "BUNDLE_BUILDS_GITBUNDLE_DEBUG=${BUNDLE_BUILDS_GITBUNDLE_DEBUG:-false}",
            "BUNDLE_BUILDS_GITBUNDLE_SKIP_VERIFY=${BUNDLE_BUILDS_GITBUNDLE_SKIP_VERIFY:-true}",
            "BUNDLE_BUILDS_DATABASE_DRIVER=${BUNDLE_BUILDS_DATABASE_DRIVER:-postgres}",
            "BUNDLE_BUILDS_DATABASE_DATASOURCE=${BUNDLE_BUILDS_DATABASE_DATASOURCE:-postgres://postgres:postgres@db:5432/bundle-builds?sslmode=disable}",
            "BUNDLE_BUILDS_DATABASE_SECRET=${BUNDLE_BUILDS_DATABASE_SECRET:-}",
            "BUNDLE_BUILDS_REDIS_CONNECTION=${BUNDLE_BUILDS_REDIS_CONNECTION:-redis://redis-server:6379}",
            "BUNDLE_BUILDS_WEBHOOK_ENDPOINT=${BUNDLE_BUILDS_WEBHOOK_ENDPOINT:-}",
            "BUNDLE_BUILDS_LOGS_TRACE=${BUNDLE_BUILDS_LOGS_TRACE:-true}",
            "BUNDLE_BUILDS_LOGS_COLOR=${BUNDLE_BUILDS_LOGS_COLOR:-true}",
            "BUNDLE_BUILDS_LOGS_TEXT=${BUNDLE_BUILDS_LOGS_TEXT:-true}",
            "BUNDLE_BUILDS_ARTEFACT_DOCKER_BASE_IMAGE=${BUNDLE_BUILDS_ARTEFACT_DOCKER_BASE_IMAGE:-gitbundle/bundle-docker}",
            "BUNDLE_BUILDS_ARTEFACT_DOCKER_REGISTRY_HOST=${BUNDLE_BUILDS_ARTEFACT_DOCKER_REGISTRY_HOST:-}",
            "BUNDLE_BUILDS_ARTEFACT_DEBUG_BUILD=${BUNDLE_BUILDS_ARTEFACT_DEBUG_BUILD:-false}",
            "BUNDLE_BUILDS_ARTEFACT_DUMP_BUILD=${BUNDLE_BUILDS_ARTEFACT_DUMP_BUILD:-false}",
            "BUNDLE_BUILDS_NSQ_CLUSTER_TCP_ADDR=${BUNDLE_BUILDS_NSQ_CLUSTER_TCP_ADDR:-}",
            "BUNDLE_BUILDS_NSQ_AUTH_SECRET=${BUNDLE_BUILDS_NSQ_AUTH_SECRET:-}",
            "BUNDLE_BUILDS_PLUGIN_TOKEN=${BUNDLE_BUILDS_PLUGIN_TOKEN:-}",
        ],
        "depends_on": dependsOn,
        "restart": "always",
        "networks": networks(),
    }


def bundleRunnerServer(arch, dependsOn):
    return {
        "container_name": "bundle-runner-%s" % arch,
        "image": "gitbundle/bundle-builds-runner-docker",
        "platform": "linux/%s" % arch,
        "volumes": containerVolumes(
            [
                "/var/run/docker.sock:/var/run/docker.sock",
            ]
        ),
        "environment": [
            "BUNDLE_BUILDS_TRACE=${BUNDLE_BUILDS_TRACE:-true}",
            "BUNDLE_BUILDS_RPC_HOST=${BUNDLE_BUILDS_RPC_HOST:-bundle-builds:8080}",
            "BUNDLE_BUILDS_RPC_PROTO=${BUNDLE_BUILDS_RPC_PROTO:-http}",
            "BUNDLE_BUILDS_RPC_SECRET=${BUNDLE_BUILDS_RPC_SECRET:-}",
            "BUNDLE_BUILDS_RPC_DUMP_HTTP=${BUNDLE_BUILDS_RPC_DUMP_HTTP:-false}",
            "BUNDLE_BUILDS_RPC_DUMP_HTTP_BODY=${BUNDLE_BUILDS_RPC_DUMP_HTTP_BODY:-false}",
            "BUNDLE_BUILDS_TMATE_ENABLED=${BUNDLE_BUILDS_TMATE_ENABLED:-true}",
            "BUNDLE_BUILDS_RUNNER_CLONE_IMAGE=${BUNDLE_BUILDS_RUNNER_CLONE_IMAGE:-gitbundle/bundle-git}",  # need user release server with https, you can build your own clone image
            "BUNDLE_BUILDS_RUNNER_CAPACITY=${BUNDLE_BUILDS_RUNNER_CAPACITY:-2}",
            "BUNDLE_BUILDS_DOCKER_STREAM_PULL=${BUNDLE_BUILDS_DOCKER_STREAM_PULL:-true}",
            "BUNDLE_BUILDS_PRIVILEGED_IMAGES=${BUNDLE_BUILDS_PRIVILEGED_IMAGES:-}",
        ],
        "depends_on": dependsOn,
        "restart": "always",
        "networks": networks(),
    }


# The best way maybe is to install haproxy in your host machine
# As the docker container permission limitation with host files,
# your certs in your host machine maybe need to set 0644 perm for the haproxy container to run.
def haproxy(dependsOn):
    return {
        "container_name": "haproxy",
        "image": "haproxy:lts-alpine",
        "ports": [
            "22:22",
            "80:80",
            "443:443",
        ],
        "volumes": containerVolumes(
            [
                "./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro",
                "./certs:/certs:ro",
            ]
        ),
        "depends_on": dependsOn,
        "restart": "always",
        "networks": networks(),
    }


def redisServer():
    return {
        "container_name": "redis-server",
        "image": "redis:alpine",
        "ports": [
            "6379:6379",
        ],
        "volumes": containerVolumes([]),
        "restart": "always",
        "networks": networks(),
    }


def nsq():
    return {
        "container_name": "nsq",
        "image": "nsqio/nsq",
        "ports": [
            "4160:4160",  # nsqlookupd-tcp
            "4161:4161",  # nsqlookupd-http
            "4150:4150",  # nsqd-tcp
            "4151:4151",  # nsqd-http
            "4152:4152",  # nsqd-https
            "4171:4171",  # nsqadmin
        ],
        "volumes": containerVolumes(
            [
                "nsq-data:/data",
                "./nsq.sh:/workspace/nsq.sh",
            ]
        ),
        "command": "/workspace/nsq.sh",
        "networks": networks(),
    }


def db():
    return {
        "container_name": "db",
        "image": "postgres:alpine",
        "ports": [
            "5432:5432",
        ],
        "volumes": containerVolumes(
            [
                "db-data:/var/lib/postgresql/data:rw",
            ]
        ),
        "environment": [
            "POSTGRES_USER=postgres",
            "POSTGRES_PASSWORD=postgres",
        ],
        "healthcheck": {
            "test": ["CMD-SHELL", "pg_isready -U postgres"],
            "interval": "5s",
            "timeout": "5s",
            "retries": 5,
        },
        "networks": networks(),
    }


def volume(device):
    return {
        "driver": "local",
        "driver_opts": {
            "type": "none",
            "device": device,
            "o": "bind",
        },
    }


def networks():
    return ["gitbundle-private"]


data = main()
with open("docker-compose.yml", "w") as outfile:
    outfile.write("# this file is automatically generated. DO NOT EDIT")
    outfile.write("\n")
    yaml.Dumper.ignore_aliases = lambda *args: True
    yaml.dump(data, outfile, default_flow_style=False, sort_keys=False)
