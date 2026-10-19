# Publishing this integration to HACS

This guide takes the repository from "working code on disk" to a published HACS
integration. It covers both routes, because they are different things and you
will need the first one long before the second one finishes:

| Route | What it means | How long |
| --- | --- | --- |
| **Custom repository** | Users add your GitHub URL in HACS manually. No approval. | Immediate |
| **Default repository** | Your repo appears in the HACS store for everyone. Requires a pull request to `hacs/default`. | Months of review |

Do the custom-repository route first. It lets real users install and report bugs
while the default-listing PR waits in the queue.

The requirements below are taken from:

- <https://www.hacs.xyz/docs/publish/start/>
- <https://www.hacs.xyz/docs/publish/integration/>
- <https://www.hacs.xyz/docs/publish/action/>
- <https://www.hacs.xyz/docs/publish/include/>
- <https://developers.home-assistant.io/docs/creating_integration_manifest/>

---

## Phase 0 — Decide the repository coordinates

Everything below assumes these values. Change them consistently if you use
different ones.

| Item | Value used here |
| --- | --- |
| GitHub account/org | `ip2location` |
| Repository name | `home-assistant-ip2location` |
| Repository URL | `https://github.com/ip2location/home-assistant-ip2location` |
| Integration domain | `ip2location_io` |
| Integration directory | `custom_components/ip2location_io/` |
| First release tag | `v1.0.0` |

The **domain** is the permanent identity of the integration. It must match the
directory name under `custom_components/` and the `domain` key in
`manifest.json`. It cannot be changed later without breaking every user's config
entry. It is `ip2location_io` rather than `ip2location` because Home Assistant
Core already ships an integration with the domain `ip2location` (its
`geo_location` platform), and a custom integration must not reuse it.

> If the repository will live somewhere else, replace `ip2location` in the
> manifest URLs, `README.md` badges, and the `my.home-assistant.io` links before
> publishing.

---

## Phase 1 — Finish the repository contents

### 1.1 Required file layout

HACS integration repositories have a fixed shape. There must be **exactly one**
directory under `custom_components/`, and every file the integration needs must
live inside it.

```text
home-assistant-ip2location/
├── .github/
│   └── workflows/
│       └── validate.yaml
├── custom_components/
│   └── ip2location_io/
│       ├── __init__.py
│       ├── api.py
│       ├── binary_sensor.py
│       ├── brand/
│       │   ├── icon.png
│       │   └── icon@2x.png
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── device_tracker.py
│       ├── entity.py
│       ├── manifest.json
│       ├── sensor.py
│       ├── strings.json
│       └── translations/
│           └── en.json
├── docs/
│   └── HACS_PUBLISHING.md
├── hacs.json
├── info.md
├── LICENSE
├── README.md
└── .gitignore
```

`hacs.json` **must be at the repository root**, not inside the integration
folder. The same applies to `README.md`.

### 1.2 `manifest.json` keys HACS enforces

HACS rejects a manifest that is missing any of these:

- `domain`
- `documentation`
- `issue_tracker`
- `codeowners`
- `name`
- `version`

Home Assistant additionally requires `version` for **custom** integrations
(core integrations must omit it). Use a valid SemVer or CalVer value, for
example `"1.0.0"`.

### 1.3 Replace the two placeholders

**a) `codeowners`** — set this to the GitHub account or org that will own the
repository:

```json
"codeowners": ["@ip2location"]
```

HACS and hassfest both resolve these names against GitHub, so it must be a real
account or organisation.

**b) Confirm the URLs** in `manifest.json`:

```json
"documentation": "https://github.com/ip2location/home-assistant-ip2location",
"issue_tracker": "https://github.com/ip2location/home-assistant-ip2location/issues"
```

### 1.4 `hacs.json`

```json
{
  "name": "IP2Location.io",
  "render_readme": true,
  "homeassistant": "2025.1.0"
}
```

- `name` is the only required key.
- `homeassistant` is the minimum Home Assistant version HACS will install onto.
  This code uses `entry.runtime_data`, the `config_entry` argument to
  `DataUpdateCoordinator`, and the current `OptionsFlow` API, so `2025.1.0` is a
  safe floor.
- `render_readme: true` makes HACS render `README.md` in the info panel. The
  repository also ships `info.md`, so the information check passes either way.
- Do **not** set `content_in_root` — the code is in `custom_components/`, which
  is the expected layout.

### 1.5 Brand assets

The `brand` directory must contain at least `icon.png`. This repository ships
`icon.png` (512×512) and `icon@2x.png` (1024×1024) inside
`custom_components/ip2location_io/brand/`. HACS checks this directory first and
only falls back to the `home-assistant/brands` repository if it is missing.

### 1.6 Local pre-flight check

Run these before pushing:

```bash
cd home-assistant-ip2location

# Python syntax
for f in custom_components/ip2location_io/*.py; do python -m py_compile "$f"; done

# JSON validity
python -c "import json,glob; [json.load(open(f,encoding='utf-8')) for f in ['hacs.json']+glob.glob('custom_components/ip2location_io/**/*.json', recursive=True)]"

# translations must mirror strings.json
python -c "import json; a=json.load(open('custom_components/ip2location_io/strings.json',encoding='utf-8')); b=json.load(open('custom_components/ip2location_io/translations/en.json',encoding='utf-8')); assert a==b, 'strings.json and translations/en.json differ'"

# one integration, and hacs.json at the root
ls custom_components/
test -f hacs.json && echo "hacs.json present"

rm -rf custom_components/ip2location_io/__pycache__
```

---

## Phase 2 — Create and push the GitHub repository

Create the repository on GitHub as **public**. HACS only works with public
repositories.

```bash
cd home-assistant-ip2location

git init -b main
git add .
git commit -m "Initial commit: IP2Location.io Home Assistant integration"
git remote add origin git@github.com:ip2location/home-assistant-ip2location.git
git push -u origin main
```

Then, in **Settings → General** on GitHub:

1. **Description** — required. HACS shows it in the store. Example:
   `Home Assistant integration that displays IP geolocation data from IP2Location.io`
2. **Topics** — required. Suggested:
   `home-assistant`, `hacs`, `home-assistant-integration`, `ip2location`,
   `geolocation`, `ip-geolocation`, `ip-lookup`
3. **Issues** — required to be enabled. Under *Features*, tick **Issues**.
4. Confirm the default branch is `main`.

All four are hard checks in the HACS validation and in the default-store review.

---

## Phase 3 — Add the validation workflows

The repository already contains `.github/workflows/validate.yaml`:

```yaml
name: Validate

on:
  push:
  pull_request:
  schedule:
    - cron: "0 0 * * *"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate-hacs:
    runs-on: "ubuntu-latest"
    steps:
      - name: HACS validation
        uses: "hacs/action@main"
        with:
          category: "integration"

  validate-hassfest:
    runs-on: "ubuntu-latest"
    steps:
      - uses: actions/checkout@v4
      - uses: home-assistant/actions/hassfest@master
```

### What each action checks

**`hacs/action`** validates the repository against HACS's own rules:

| Check | Looks at |
| --- | --- |
| `archived` | The repository must not be archived. |
| `brands` | `custom_components/ip2location_io/brand/icon.png` exists. |
| `description` | The GitHub repository has a description. |
| `hacsjson` | `hacs.json` exists at the root and contains `name`. |
| `information` | An information file (`README.md` with `render_readme` or `info.md`) exists. |
| `issues` | GitHub issues are enabled. |
| `topics` | The repository has topics. |
| `manifest` | The integration manifest is valid. |

**`hassfest`** validates Home Assistant's own conventions: manifest schema,
directory structure, translations, config flow strings, and more. It is stricter
than the HACS action and is the check most likely to catch a code-level mistake.

### Reading the result

1. Open the **Actions** tab.
2. Select the **Validate** workflow and the latest run.
3. Both `validate-hacs` and `validate-hassfest` must be **green**.
4. The HACS `with:` block must contain **no `ignore:` key**. The default-store
   PR explicitly requires validation "without any errors or ignores".
5. Copy the URL of the successful run — the PR template asks for it.

You can also trigger a run by hand with **Run workflow** (`workflow_dispatch`).

### Common failures and fixes

| Message | Fix |
| --- | --- |
| `No 'version' key in the manifest file` | Add `"version": "1.0.0"` to `manifest.json`. |
| `No brand assets found` | Add `custom_components/ip2location_io/brand/icon.png`. |
| `The repository has no description` | Set a description in the GitHub repository settings. |
| `The repository has no topics` | Add topics in the GitHub repository settings. |
| `Issues are disabled` | Enable Issues under Settings → General → Features. |
| `hacs.json is missing` | Move it to the repository root. |
| `More than one integration` | Keep exactly one directory under `custom_components/`. |
| hassfest: `Invalid manifest` | Compare against the manifest documentation linked at the top. |
| hassfest: translation mismatch | Make `translations/en.json` identical to `strings.json`. |
| hassfest: `the string should not contain URLs` | Translation strings — including `data_description` — must not contain a URL. Move the link to the README or use a description placeholder. |
| HACS: `The repository has no valid topics` | Add topics in the GitHub repository settings (for example `home-assistant`, `hacs`, `home-assistant-integration`). |
| Workflow did not run | Confirm the file is at `.github/workflows/validate.yaml`. |

Do not work around a failing check with `ignore:`. The default-store review
requires an unmodified, passing run.

---

## Phase 4 — Publish a GitHub release

A tag alone is **not** enough: HACS reads GitHub *Releases*. The release must be
created **after** the validation actions have passed, because the default-store
PR asks for a successful action run and a release made after it.

### 4.1 Keep the manifest version and the tag in sync

`manifest.json` already has `"version": "1.0.0"`. Leave it there for this
release.

### 4.2 Tag and release

```bash
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
```

Then on GitHub:

1. Open **Releases → Draft a new release**.
2. Choose the existing tag `v1.0.0`.
3. Release title: `v1.0.0`.
4. Add release notes (features, fixes, breaking changes).
5. **Publish release** — not "Save draft".

HACS uses the release tag as the version users see. Keep the tag and the
manifest version aligned so support requests are unambiguous.

### 4.3 `zip_release`

This repository does **not** use `zip_release`. HACS copies the contents of
`custom_components/ip2location_io/` from the release source tree into the user's
`config/custom_components/ip2location_io/`. There is no build step, so nothing
extra is needed.

---

## Phase 5 — Test it as a custom repository

This is the route that works immediately, and it is the same thing users will do
until the default listing is merged.

1. In Home Assistant, open **HACS**.
2. Click the three dots in the top-right corner → **Custom repositories**.
3. Paste `https://github.com/ip2location/home-assistant-ip2location`.
4. Select category **Integration** and click **Add**.
5. Search for **IP2Location.io** in HACS, open it, and click **Download**.
6. **Restart Home Assistant.**
7. Go to **Settings → Devices & services → Add integration** and search for
   **IP2Location.io**.

### Checks to run before announcing it

- [ ] The config flow opens and the field descriptions render.
- [ ] An empty IP address geolocates the Home Assistant host.
- [ ] An explicit IPv4 address and an explicit IPv6 address both work.
- [ ] An invalid IP string shows the `invalid_ip` error.
- [ ] A wrong API key shows `invalid_auth`.
- [ ] The sensors match the plan (free key → core fields only).
- [ ] `binary_sensor.*_proxy` exists and reflects `is_proxy`.
- [ ] `device_tracker.*_location` appears on a map card.
- [ ] **Configure** changes the polling interval and the entry reloads.
- [ ] Removing the entry removes its entities and leaves no errors in the log.
- [ ] With debug logging on, no tracebacks appear during setup or polling.

Enable debug logging while testing:

```yaml
logger:
  logs:
    custom_components.ip2location_io: debug
```

HACS also keeps its own log under **HACS → (three dots) → Log**.

---

## Phase 6 — Submit for the default store

Only start this once all of the following are true:

- The repository is public and not archived.
- HACS and hassfest both pass with no `ignore`.
- At least one full GitHub release exists.
- You are the repository owner or a major contributor.
- The PR will be opened from **your personal account**, not an organisation
  account. The PR must be editable by the reviewer.

### 6.1 Fork and branch

1. Fork `https://github.com/hacs/default` to your own account.
2. Clone your fork and create a branch off `master`, never commit to `master`
   directly:

```bash
git clone git@github.com:YOUR-USERNAME/default.git
cd default
git checkout -b add-ip2location
```

### 6.2 Edit the `integration` file

`integration` is a JSON array of `"owner/repo"` strings, sorted
**case-insensitively**. Add your entry in the correct alphabetical position —
not at the end.

`ip2location/home-assistant-ip2location` sorts after
`IoTFenster/MySmartWindow` and before `iPeel/HA-Eleven-Energy` (the comparison is
case-insensitive, so `iot…` comes before `ip2…`, and the digit `2` sorts before
the letter `e`):

```diff
   "iosmand/ha-open-meteo-custom",
   "IoTFenster/MySmartWindow",
+  "ip2location/home-assistant-ip2location",
   "iPeel/HA-Eleven-Energy",
   "iprak/sensi",
   "iprak/weatherapi",
```

Keep the two-space indentation and the trailing comma. Then validate the file:

```bash
python -c "import json; d=json.load(open('integration')); print(len(d), 'entries'); assert d == sorted(d, key=str.lower), 'not sorted'"
```

### 6.3 Commit and push

```bash
git add integration
git commit -m "Add ip2location/home-assistant-ip2location"
git push origin add-ip2location
```

### 6.4 Open the pull request

Open the PR against `hacs/default:master`. The repository provides a template at
`.github/PULL_REQUEST_TEMPLATE.md`; fill it in **completely**. A PR that does not
follow it is closed without further notice.

```markdown
## Checklist

- [x] I've read the [publishing documentation](https://hacs.xyz/docs/publish/start).
- [x] I've added the [HACS action](https://hacs.xyz/docs/publish/action) to my repository.
- [x] (For integrations only) I've added the [hassfest action](https://developers.home-assistant.io/blog/2020/04/16/hassfest/) to my repository.
- [x] The actions are passing without any disabled checks in my repository.
- [x] I've added a link to the action run on my repository below in the links section.
- [x] I've created a new release of the repository after the validation actions were run successfully.

## Links

Link to current release: https://github.com/ip2location/home-assistant-ip2location/releases/tag/v1.0.0
Link to successful HACS action (without the `ignore` key): https://github.com/ip2location/home-assistant-ip2location/actions/runs/RUN_ID
Link to successful hassfest action (if integration): https://github.com/ip2location/home-assistant-ip2location/actions/runs/RUN_ID
```

Rules for the PR itself:

- Do **not** request reviews. The template says this will get the PR closed.
- Do **not** misrepresent anything in the template.
- Do not open the PR before the release exists and the actions pass.
- If the PR is marked as a draft, set it to **Ready for review** when it is
  complete.

### 6.5 Automated checks on the PR

The reviewer runs the same HACS checks, plus:

| Check | What it verifies |
| --- | --- |
| brands | Brand assets or a `home-assistant/brands` entry exist. |
| manifest | The integration manifest is valid. |
| hacs-validation | The same validation HACS runs for custom repositories. |
| hacs-manifest | `hacs.json` contains at least `name`. |
| archived | The repository is active. |
| releases | At least one release exists. |
| owner | The submitter owns or contributes to the repository. |
| repository | Description, issues and topics are set. |
| lint jq | The edited JSON files parse. |
| lint sorted | The `integration` array is correctly sorted. |

---

## Phase 7 — After the PR is merged

- The repository is included in the **next scheduled scan** of the HACS store,
  not instantly.
- New additions currently take months to be reviewed. This is normal; the
  custom-repository route keeps you usable in the meantime.
- Once listed, users install it from the HACS store with no manual repository
  entry.

---

## Phase 8 — Releasing updates

For every future version:

1. Bump `"version"` in `custom_components/ip2location_io/manifest.json`.
2. Update `README.md` if user-visible behaviour changed.
3. Commit and push.
4. Confirm both validation actions pass on the push.
5. Create a new tag and a GitHub **Release** from it (for example `v1.1.0`).
6. Do not edit the `hacs/default` list again — it points at the repository, not
   a tag.

HACS offers the five latest releases plus the default branch in its version
picker, so old tags stay available for users who need to roll back.

---

## Appendix A — What HACS actually copies

When a user installs the integration, HACS copies:

```text
custom_components/ip2location_io/  →  <config>/custom_components/ip2location_io/
```

Nothing outside `custom_components/ip2location_io/` is installed. That is why
every runtime file (including `brand/`, `strings.json` and `translations/`) must
live inside that directory. `hacs.json`, `README.md`, `LICENSE`, `docs/` and
`.github/` are repository metadata only.

---

## Appendix B — Requirement checklist

**General**

- [ ] Repository is public on GitHub.
- [ ] Repository has a description.
- [ ] Repository has topics.
- [ ] Repository has a `README.md`.
- [ ] Repository is not archived.
- [ ] Issues are enabled.
- [ ] `hacs.json` exists at the root and contains `name`.

**Integration**

- [ ] Exactly one directory under `custom_components/`.
- [ ] All runtime files are inside `custom_components/ip2location_io/`.
- [ ] `manifest.json` contains `domain`, `documentation`, `issue_tracker`,
      `codeowners`, `name`, `version`.
- [ ] `codeowners` resolves to a real GitHub account or org.
- [ ] `custom_components/ip2location_io/brand/icon.png` exists.
- [ ] The directory name, manifest `domain`, and config entry domain all match.
- [ ] HACS action passes with no `ignore`.
- [ ] hassfest passes.
- [ ] At least one GitHub **Release** exists (not just a tag).
- [ ] The release was created after the validation runs.

**Default-store PR**

- [ ] Forked `hacs/default` and branched from `master`.
- [ ] Entry added alphabetically (case-insensitive), not appended.
- [ ] `integration` still parses as JSON and is sorted.
- [ ] PR opened from a personal account.
- [ ] PR template fully filled in, with all three links.
- [ ] No review requested.

---

## Appendix C — Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| HACS says the repository is not valid | Open the Actions tab and read the failing check name; the table in Phase 3 maps each one to a fix. |
| Integration downloads but does not appear in "Add integration" | Home Assistant was not restarted after install, or the `domain` in `manifest.json` does not match the folder name. |
| Entities are missing after setup | The API plan does not return those fields. The free plan only returns the core location set. |
| `invalid_auth` on setup | The API key is wrong, revoked, or pasted with whitespace. |
| `rate_limit` | The anonymous quota (1,000 per day) or the key's monthly quota is exhausted. |
| `cannot_connect` | Home Assistant cannot reach `api.ip2location.io`; check DNS and outbound HTTPS. |
| HACS offers an old version | HACS shows the latest GitHub **Release**. Create a release, not just a tag. |
| Default-store PR closed | The template was incomplete, a check was ignored, a release was missing, or the account could not edit the PR. |
| `lint sorted` fails | The entry is out of alphabetical order. Re-check case-insensitive placement. |

---

## Appendix D — Reference links

- HACS publisher overview: <https://www.hacs.xyz/docs/publish/>
- General requirements: <https://www.hacs.xyz/docs/publish/start/>
- Integration requirements: <https://www.hacs.xyz/docs/publish/integration/>
- Validation action: <https://www.hacs.xyz/docs/publish/action/>
- Default-store inclusion: <https://www.hacs.xyz/docs/publish/include/>
- HACS default repository list: <https://github.com/hacs/default>
- Home Assistant integration manifest: <https://developers.home-assistant.io/docs/creating_integration_manifest>
- hassfest: <https://developers.home-assistant.io/blog/2020/04/16/hassfest>
- Reference template: <https://github.com/custom-components/blueprint>
