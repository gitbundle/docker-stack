# GitBundle

This is a template repository for GitBundle Premium Edition.

For production environment, user should configure the ssl cert. Like using `acme.sh` for auto configure ssl.

For local environment, use `mkcert` to generate the ssl cert, and then run `hack.sh` before starting container.

## Notes

The required database may need to create first

# Use your own env
```bash
cp env-example .env
```

# Generate your own secret key
```bash
openssl rand -hex 16
```

# Init required folder
```bash
mkdir -p data/{gitbundle,nsq,postgres}
```

# Troubleshoot

## nsq , redis-server & ssh port
```console
gitbundle  | Received signal 15; terminating.
gitbundle  | Server listening on :: port 22.
gitbundle  | Server listening on 0.0.0.0 port 22.
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Starting gitbundle on PID: 18
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Global init
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Git Version: 2.36.6, Wire Protocol Version 2 Enabled (home: /data/gitbundle/home)
gitbundle  | 2023/10/10 07:50:12 :0: [👉] AppPath: /usr/local/bin/gitbundle
gitbundle  | 2023/10/10 07:50:12 :0: [👉] AppWorkPath: /app/gitbundle
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Custom path: /data/gitbundle
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Plugin path: /data/gitbundle/plugins
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Log path: /data/gitbundle/log
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Configuration file: /data/gitbundle/conf/app.ini
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Run Mode: Prod
gitbundle  | 2023/10/10 07:50:12 :0: [👉] GitBundle vv1.0.3 built with GNU Make 4.3, go1.21.1 : bindata, timetzdata, private_edition
gitbundle  | 2023/10/10 07:50:12 :0: [👉] GitBundle Log Mode: Console(Console:info)
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Router Log: Console(console:info)
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Cache Service Enabled
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Last Commit Cache Service Enabled
gitbundle  | 2023/10/10 07:50:12 :0: [👉] Session Service Enabled
gitbundle  | 2023/10/10 07:50:12 :0: [💣] Empty ClusterTcpAddr for nsq setting
```

> solution, add the following configuration to `data/gitbundle/gitbundle/conf/app.ini`
```ini
[nsq]
CLUSTER_TCP_ADDR = nsq:4150

[redis]
CONNECTION = redis://redis-server:6379
```

## database not exists
```console
gitbundle  | 2023/10/10 07:52:19 :0: [👉] ORM engine initialization attempt #1/10...
gitbundle  | 2023/10/10 07:52:19 :0: [👉] PING DATABASE postgres
gitbundle  | 2023/10/10 07:52:19 :0: [🔴] ORM engine initialization attempt #1/10 failed. Error: pq: database "gitbundle" does not exist
gitbundle  | 2023/10/10 07:52:19 :0: [👉] Backing off for 3 seconds
gitbundle  | 2023/10/10 07:52:22 :0: [👉] ORM engine initialization attempt #2/10...
gitbundle  | 2023/10/10 07:52:22 :0: [👉] PING DATABASE postgres
gitbundle  | 2023/10/10 07:52:22 :0: [🔴] ORM engine initialization attempt #2/10 failed. Error: pq: database "gitbundle" does not exist
gitbundle  | 2023/10/10 07:52:22 :0: [👉] Backing off for 3 seconds
gitbundle  | 2023/10/10 07:52:25 :0: [👉] ORM engine initialization attempt #3/10...
gitbundle  | 2023/10/10 07:52:25 :0: [👉] PING DATABASE postgres
gitbundle  | 2023/10/10 07:52:25 :0: [🔴] ORM engine initialization attempt #3/10 failed. Error: pq: database "gitbundle" does not exist
gitbundle  | 2023/10/10 07:52:25 :0: [👉] Backing off for 3 seconds
gitbundle  | 2023/10/10 07:52:28 :0: [👉] ORM engine initialization attempt #4/10...
gitbundle  | 2023/10/10 07:52:28 :0: [👉] PING DATABASE postgres
gitbundle  | 2023/10/10 07:52:28 :0: [🔴] ORM engine initialization attempt #4/10 failed. Error: pq: database "gitbundle" does not exist
gitbundle  | 2023/10/10 07:52:28 :0: [👉] Backing off for 3 seconds
gitbundle  | 2023/10/10 07:52:31 :0: [👉] ORM engine initialization attempt #5/10...
gitbundle  | 2023/10/10 07:52:31 :0: [👉] PING DATABASE postgres
gitbundle  | 2023/10/10 07:52:31 :0: [🔴] ORM engine initialization attempt #5/10 failed. Error: pq: database "gitbundle" does not exist
gitbundle  | 2023/10/10 07:52:31 :0: [👉] Backing off for 3 seconds
```

> solution, create the database, using the following script to create `docker-compose.yml` configured database
```bash
# create gitbundle database
docker compose exec -u postgres db createdb --encoding=UTF8 gitbundle
# create bundle-builds database
docker compose exec -u postgres db createdb --encoding=UTF8 bundle-builds
# create bundle-deployments database
docker compose exec -u postgres db createdb --encoding=UTF8 bundle-deployments
```

## repository with a bad url
```console
http://example.gitbundle.com:4000/bundle/hello
```

> solution, update the following configuration to `data/gitbundle/gitbundle/conf/app.ini`, then restart the docker stack.
```ini
[server]
APP_DATA_PATH    = /data/gitbundle
DOMAIN           = example.gitbundle.com
SSH_DOMAIN       = example.gitbundle.com
HTTP_PORT        = 4000
ROOT_URL         = http://example.gitbundle.com # add this line to the server section in app.ini
DISABLE_SSH      = false
SSH_PORT         = 22
SSH_LISTEN_PORT  = 22
LFS_START_SERVER = true
LFS_JWT_SECRET   = lfs-jwt-secret
```

## Next
Try to install the plugins, and generate the token for every plugin service. Configure the token for every plugin service. Some plugin may not need a token. This is depending on the plugin features.