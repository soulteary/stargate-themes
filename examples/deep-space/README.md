# Deep Space with Docker Compose

This example runs Stargate v1.8.0 with Deep Space 1.0.0, Traefik and a protected
Hello service. It uses local HTTP, a shared password and in-memory sessions.
Restarting Stargate clears those sessions. It does not require Warden or Herald.

For an existing deployment, keep its authentication, TLS and session-storage
settings. Add `THEME_DIR=/app/themes/deep-space` and the read-only theme mount
from [compose.yml](compose.yml).

## Requirements

- Docker with Docker Compose v2 or later.
- `curl`, `unzip` and `openssl`.
- `sha256sum` on Linux, or `shasum` on macOS.
- Host port 80 and the `172.30.0.0/24` subnet available.

From the repository root, enter the example directory:

```sh
cd examples/deep-space
mkdir -p downloads themes
```

## Download and verify

Download the ZIP, index and checksum manifest from the
[v1.0.0 theme release](https://github.com/soulteary/stargate-themes/releases/tag/v1.0.0):

```sh
(
  set -e
  THEME_RELEASE=https://github.com/soulteary/stargate-themes/releases/download/v1.0.0

  for FILE in deep-space-1.0.0.zip index.json checksums.txt; do
    curl --fail --location --retry 3 \
      --output "downloads/${FILE}" \
      "${THEME_RELEASE}/${FILE}"
  done
)
```

On Linux, verify both the ZIP and index:

```sh
(cd downloads && sha256sum --check checksums.txt)
```

On macOS:

```sh
(cd downloads && shasum -a 256 --check checksums.txt)
```

Both files must report `OK` before installation. The ZIP's SHA-256 for this
release is also pinned below:

```text
6c4b861e0243fe3e83e57e6f8657eace3c29962804c2e75135679daef1524403
```

Compare it with:

```sh
openssl dgst -sha256 downloads/deep-space-1.0.0.zip
```

## Install the theme

For a fresh installation:

```sh
mkdir -p themes/deep-space
unzip downloads/deep-space-1.0.0.zip -d themes/deep-space

chmod 755 themes themes/deep-space themes/deep-space/assets
chmod 644 \
  themes/deep-space/theme.yml \
  themes/deep-space/LICENSE.txt \
  themes/deep-space/assets/deep-space.jpg
```

The resulting directory contains:

```text
themes/deep-space/
  theme.yml
  LICENSE.txt
  assets/
    deep-space.jpg
```

The archive has no enclosing `deep-space/` directory. `THEME_DIR` must point
to the directory containing `theme.yml`. Stargate reads extracted files, not
ZIP archives. UID 10001 must be able to read the files and traverse directories.
The Compose mount is read-only and refuses to create a missing source directory.

## Configure and start

Generate a local `.env` file with a random login password and session-exchange
secret. This command refuses to overwrite an existing `.env`:

```sh
(
  umask 077
  set -C
  {
    echo 'AUTH_HOSTNAME=auth.test.localhost'
    echo 'APP_HOSTNAME=hello.test.localhost'
    printf 'STARGATE_PASSWORD=%s\n' "$(openssl rand -hex 16)"
    printf 'SESSION_EXCHANGE_SECRET=%s\n' "$(openssl rand -hex 32)"
    echo 'THEME_SAFE_MODE=false'
  } > .env
)
```

Alternatively, copy [.env.example](.env.example) to `.env`, restrict it to mode
`600`, and set both secrets. Compose rejects empty values for either secret.
To display the generated login password locally:

```sh
sed -n 's/^STARGATE_PASSWORD=//p' .env
```

If the hostnames do not resolve to loopback, add this entry to your hosts file:

```text
127.0.0.1 auth.test.localhost hello.test.localhost
```

If the subnet is already in use, change both `networks.traefik.ipam.config.subnet`
and `TRUSTED_PROXIES` in `compose.yml`. The latter must match Traefik's network.

Validate and start:

```sh
docker compose config --quiet
docker compose pull
docker compose up -d

docker compose ps
docker compose logs --tail=100 stargate
```

Open <http://hello.test.localhost> and log in with `STARGATE_PASSWORD` from
`.env`. Confirm that login uses the Deep Space background and returns to Hello.
The login page is also available at <http://auth.test.localhost/_login>; after
login, open <http://auth.test.localhost/_account> to check the account page.

`/healthz` checks service health; it does not establish that login or the theme
works. Check the page, image loading and login redirect in the browser.

## Change or disable the theme

Edit `themes/deep-space/theme.yml`, then reload the theme by restarting Stargate:

```sh
docker compose restart stargate
```

A theme is validated and loaded at startup. Invalid theme data prevents startup.
To recover, set this value in `.env`:

```dotenv
THEME_SAFE_MODE=true
```

Apply the changed environment by recreating the container:

```sh
docker compose up -d --force-recreate stargate
```

Safe mode uses the bundled interface and skips native themes and legacy UI
overrides. Fix the theme, set `THEME_SAFE_MODE=false`, and recreate Stargate
again to enable it. Environment changes require recreation; a restart alone
does not apply them.

To stop selecting the theme permanently, remove `THEME_DIR` and leave safe mode
false. This restores normal UI override precedence. To replace a package,
extract it into a clean directory, verify it, then update the mount and recreate
Stargate. Do not mix files from different theme versions. Use the same package
on every replica. Reload open browser pages after a theme change.

## Deployment scope

The example uses `COOKIE_SECURE=false` and a plaintext password for local HTTP.
For production, configure HTTPS, use `COOKIE_SECURE=true`, and store passwords
with bcrypt. Preserve existing Redis and authentication configuration when
adding a theme. See Stargate's [deployment guide](https://github.com/soulteary/stargate/blob/v1.8.0/docs/enUS/DEPLOYMENT.md)
and [theme guide](https://github.com/soulteary/stargate/blob/v1.8.0/docs/enUS/THEMES.md).

Stop the local example with:

```sh
docker compose down
```
