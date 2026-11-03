# Implementation TODO

Work top to bottom. Each numbered step is one small change for an AI-assisted session. Finish its security and documentation checkboxes before starting the next step.

The product spec is [requirements.md](requirements.md). This demo simulates Linux server health. It does not connect to real hosts.

Suggested layout as the steps introduce files:

```text
app/__init__.py
app/auth.py
app/config_store.py
app/simulator.py
app/status.py
app/templates/
app/static/css/app.css
app/static/js/monitor.js
config/monitoring.json
tests/
.github/workflows/ci.yml
.github/workflows/cd.yml
```

## 1. Project initialization and basic UI

- [x] **1.1 Add the repository hygiene files**
  - [x] Create `.gitignore` for `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, and `.env`.
  - [x] Security: a local `.env` is ignored, so a developer secret key stays off the branch.
  - [x] Docs: create `README.md` with the product name and a link to `docs/requirements.md`.

- [x] **1.2 Pin the runtime dependency**
  - [x] Add `requirements.txt` with a pinned Flask release. Werkzeug arrives with Flask. Add nothing else.
  - [x] Security: pin the version so a later install cannot silently move to an unreviewed Flask.
  - [x] Docs: add an Install section to `README.md` (`python -m venv .venv`, then `pip install -r requirements.txt`).

- [x] **1.3 Add a demo environment example**
  - [x] Add `.env.example` with `FLASK_SECRET_KEY` set to a labeled demo value.
  - [x] Security: the example key is a demo value only. The real local key lives in `.env`, which is gitignored.
  - [x] Docs: tell the reader to copy `.env.example` to `.env` and to avoid reusing the demo key outside this project.

- [x] **1.4 Create the Flask app factory**
  - [x] Add `app/__init__.py` with `create_app()`. Read `FLASK_SECRET_KEY` from the environment and assign it to `app.secret_key`.
  - [x] Security: startup fails with a clear error when `FLASK_SECRET_KEY` is missing. The source tree contains no fallback key.
  - [x] Docs: add a Run section to `README.md` (`FLASK_APP=app:create_app`, `flask run`) and state that the variable is required.

- [x] **1.5 Add the page shell and stylesheet**
  - [x] Add `app/templates/base.html` with a header, “Demo Monitoring”, and a main region. Add `app/static/css/app.css`.
  - [x] Make the layout readable from 1024px wide: header, content spacing, and a type size suited to scanning.
  - [x] Security: the template does not render untrusted text with `|safe`.
  - [x] Docs: describe the shell in `README.md` (header plus an empty main region).

- [x] **1.6 Add the placeholder monitoring page**
  - [x] Serve `GET /` with a server-list region and a detail region. Both are empty and say that data is not wired yet.
  - [x] Security: this route is public only until step 2.8. The page shows no account data, no config contents, and no metrics.
  - [x] Docs: note in `README.md` that `/` is a temporary open page and that sign-in will close it.

- [x] **1.7 Add status presentation to the shell**
  - [x] Show three static examples on the placeholder: Healthy, Warning, and Critical. Healthy is green, Warning is amber, Critical is red.
  - [x] Security: each example includes the word in the HTML. Color is an extra signal, which matches the spec’s accessibility rule.
  - [x] Docs: record the three labels and their colors in `README.md`.

- [x] **1.8 Confirm the app boots**
  - [x] Run the app with the demo key and open `/`. The shell, empty regions, and three status examples are visible.
  - [x] Security: the running process loaded the key from the environment. The key does not appear in the page or the README.
  - [x] Docs: add the local URL (`http://127.0.0.1:5000/`) to the Run section.

## 2. Sign-in functionality and unit tests

- [ ] **2.1 Add the test runner**
  - [ ] Add `requirements-dev.txt` with a pinned pytest. Add `tests/` and a passing smoke test that imports `create_app`.
  - [ ] Security: the test app uses a key set inside the test, and the test does not read or print a developer `.env`.
  - [ ] Docs: add a Test section to `README.md` (`pip install -r requirements-dev.txt`, then `pytest`).

- [ ] **2.2 Hash and check passwords**
  - [ ] Add helpers in `app/auth.py` that hash with Werkzeug `pbkdf2:sha256` and check with `check_password_hash`.
  - [ ] Unit-test that a hash verifies the original password, rejects a different password, and starts with `pbkdf2:sha256`.
  - [ ] Security: tests assert the stored form is a hash. Helpers never log the password or the hash.
  - [ ] Docs: note in `README.md` that demo passwords are public in the spec and must not be reused.

- [ ] **2.3 Load users from a JSON fixture**
  - [ ] Load `users` (username, role, `password_hash`) from a config path passed into the app. Roles are `admin` and `viewer`.
  - [ ] Unit-test a temp JSON file: known user is found, unknown user is absent, and a record with a plaintext `password` field is rejected.
  - [ ] Security: the loader accepts `password_hash` only. It refuses a user record that carries a plaintext password.
  - [ ] Docs: document the user fields in `README.md`. Point at the config shape in `docs/requirements.md`.

- [ ] **2.4 Show the sign-in form**
  - [ ] Add `GET /login` with username and password fields, labels, and a submit button. Autocomplete and label markup let the form be completed from the keyboard.
  - [ ] Add a view test that the form renders and that the password input is `type="password"`.
  - [ ] Security: the form uses `POST`. The password field is a password input. The page does not echo a previous password.
  - [ ] Docs: describe the sign-in page in `README.md`, including the seeded usernames `admin` and `viewer`.

- [ ] **2.5 Accept a correct password**
  - [ ] `POST /login` checks the hash, stores username and role in the session, and redirects to `/`.
  - [ ] Test `admin` and `viewer` against fixture hashes of `MonitorDemo#1`. Each lands on `/` with the matching role in the session.
  - [ ] Security: the session cookie is marked `HttpOnly`. Comparison goes through `check_password_hash`.
  - [ ] Docs: write the happy-path sign-in steps in `README.md`.

- [ ] **2.6 Reject a bad password**
  - [ ] A failed `POST /login` re-renders the form with exactly `Invalid username or password.` The session stays empty.
  - [ ] Test a wrong password, an unknown username, and an empty submit. All three show that same sentence.
  - [ ] Security: the response does not say which field failed. The submitted password is absent from the HTML and the session.
  - [ ] Docs: record the exact error sentence in `README.md`.

- [ ] **2.7 End the session**
  - [ ] Set the session lifetime to 8 hours. Add `POST /logout` to clear the session and redirect to `/login`.
  - [ ] Test that logout removes the session and that a following request to `/` is sent to `/login`.
  - [ ] Security: logout is `POST`, so a page that merely links to a URL cannot sign the user out. The session is cleared on the server.
  - [ ] Docs: add Sign out to the `README.md` usage steps.

- [ ] **2.8 Close the monitoring page**
  - [ ] `GET /` without a session redirects to `/login`. A signed-in user still sees the placeholder shell and a sign-out control.
  - [ ] Test the redirect for an anonymous client, and test that `admin` and `viewer` can both open `/`.
  - [ ] Security: the placeholder from step 1.6 is no longer public. The sign-out control is present only for a signed-in user.
  - [ ] Docs: replace the “temporary open page” note in `README.md` with the redirect behavior.

- [ ] **2.9 Log failed sign-in safely**
  - [ ] Log a failed sign-in with the username and the result. Leave the password and the hash out of the log record.
  - [ ] Test the log record with a handler attached in the test. Assert the password string is absent.
  - [ ] Security: this is the spec rule that failed sign-ins are logged without secrets.
  - [ ] Docs: add one `README.md` sentence on what a failed sign-in log contains.

## 3. CI/CD with GitHub Actions

- [ ] **3.1 Add the CI test workflow**
  - [ ] Add `.github/workflows/ci.yml`. On `push` and `pull_request`, use Ubuntu and Python 3.12, install `requirements.txt` and `requirements-dev.txt`, and run `pytest`.
  - [ ] Security: workflow permissions are `contents: read`. `FLASK_SECRET_KEY` is a job-scoped dummy used only by tests. The workflow does not print the environment.
  - [ ] Docs: add a CI section to `README.md` that names the workflow file and the `pytest` command it runs.

- [ ] **3.2 Add CI checks for secret handling**
  - [ ] In the same workflow, fail the job if `.gitignore` is missing an entry for `.env`. When `config/monitoring.json` exists, fail if any user object contains `password`, or if `password_hash` does not start with `pbkdf2:sha256`.
  - [ ] Security: the check looks at the config file that the app loads. It leaves the public demo password in `docs/requirements.md` alone, because the spec publishes it on purpose.
  - [ ] Docs: describe both checks in the `README.md` CI section.

- [ ] **3.3 Add a manual CD smoke workflow**
  - [ ] Add `.github/workflows/cd.yml` with `workflow_dispatch` only. It installs the app, starts Flask on localhost with a dummy `FLASK_SECRET_KEY`, requests `GET /login`, expects HTTP 200, and stops the process.
  - [ ] Security: the workflow has no deploy step and no cloud credentials. The dummy key is not printed. The job does not publish the demo to a public host.
  - [ ] Docs: explain in `README.md` how to run the CD workflow by hand, and that delivery means “the sign-in page boots,” not a deployment.

- [ ] **3.4 Keep the pipelines green for the rest of this list**
  - [ ] After this step, every later change leaves `pytest` passing locally and the CI workflow as the place those tests run.
  - [ ] Security: new tests that need a secret key keep using a dummy key inside the test or the job. They do not read a real `.env`.
  - [ ] Docs: state that rule in the `README.md` CI section.

## 4. Config file

- [ ] **4.1 Load the full monitoring file**
  - [ ] Extend the loader to read `thresholds`, `users`, and `servers` from `config/monitoring.json`.
  - [ ] Unit-test a temp file that contains all three sections, and a missing file that raises a clear error.
  - [ ] Security: the loader parses JSON only. It does not evaluate file contents. Errors name the path and the field, and omit hash values.
  - [ ] Docs: give the config path and the three top-level keys in `README.md`.

- [ ] **4.2 Validate a server record**
  - [ ] Require `id`, `name`, `hostname`, `profile` (`steady`, `busy`, or `stressed`), `os` equal to `linux`, and `booted_at`. Allow `environment` and `team` to be empty.
  - [ ] Unit-test one valid server and one rejection each for a missing name, a bad profile, and an `os` other than `linux`.
  - [ ] Security: `os` is fixed to `linux` in validation, so a crafted config cannot introduce another platform.
  - [ ] Docs: list required and optional server fields in `README.md`.

- [ ] **4.3 Write server changes atomically**
  - [ ] Add a writer that updates `servers` and leaves `users` and `thresholds` as they were. Write a temporary file in the same directory, then replace the config.
  - [ ] Unit-test that a server edit survives a reload and that every `password_hash` is unchanged.
  - [ ] Security: the replace is atomic so a crash mid-write does not leave a half-written config. The writer never accepts a user or threshold payload.
  - [ ] Docs: describe the temp-file replace in `README.md`.

- [ ] **4.4 Ship the seeded config**
  - [ ] Create `config/monitoring.json` with the default thresholds from the spec, hashed `admin` and `viewer` accounts, and three Linux servers (`steady`, `busy`, `stressed`) with fixed `booted_at` values.
  - [ ] Security: generate the hashes with the step 2.2 helper. The file contains `password_hash` values and no plaintext password. Run the step 3.2 check against this file.
  - [ ] Docs: document the three seeded servers and the two usernames in `README.md`. Repeat that the plaintext demo password lives in the spec, not in the config.

## 5. Simulated metrics

- [ ] **5.1 Fix the hardware for each profile**
  - [ ] `steady` has 4 cores. `busy` and `stressed` have 8. Memory total is 16 GiB. Swap total is 4 GiB. Disk totals are fixed for `/` and `/var`.
  - [ ] Unit-test that two samples of the same server return the same totals and the same core count.
  - [ ] Security: the simulator is a pure function of the server record and the clock. It opens no socket and starts no process.
  - [ ] Docs: record the hardware table in `README.md`.

- [ ] **5.2 Generate one full sample**
  - [ ] Return CPU overall, one value per core, memory used/free/percent, swap used/percent, both disk mounts, load average for 1/5/15 minutes, and uptime from `booted_at`.
  - [ ] Unit-test the keys and that uptime grows when the clock moves forward.
  - [ ] Security: the sample is returned to the caller only. The function does not write a file.
  - [ ] Docs: list the sample fields in `README.md` next to the metric list from the spec.

- [ ] **5.3 Keep successive samples smooth**
  - [ ] Each new sample moves a small step from the previous one inside the profile band. Per-core values stay near the overall CPU. The 5- and 15-minute load values move less than the 1-minute value.
  - [ ] Unit-test that a `steady` server sampled many times stays inside its band and never lands in the `stressed` CPU band.
  - [ ] Security: the step state lives in memory for the life of the process. It is not appended to the config file.
  - [ ] Docs: explain in `README.md` that a restart may start a new walk inside the same band, and that history is not stored.

- [ ] **5.4 Cover the three demo profiles**
  - [ ] Hold `steady` in CPU 15–35%, memory 40–55%, a disk near 45%, and 1-minute load below the core count. Hold `busy` and `stressed` inside the bands in the spec.
  - [ ] Unit-test one server of each profile.
  - [ ] Security: profile names come from the validated server record. An unknown profile fails validation in step 4.2 rather than sampling arbitrary input.
  - [ ] Docs: copy the three profile bands into `README.md`.

## 6. Status colors

- [ ] **6.1 Classify one metric**
  - [ ] Implement Healthy / Warning / Critical for CPU, memory, swap, disk, and 1-minute load using the default thresholds. A value on the line counts as that level.
  - [ ] Unit-test the boundaries: just below warning, exactly warning, just below critical, and exactly critical.
  - [ ] Security: classification reads numbers only. It does not change the sample or the config.
  - [ ] Docs: add the threshold table to `README.md`.

- [ ] **6.2 Compute the server’s overall status**
  - [ ] Overall status is the worst of CPU, memory, swap, every disk mount, and 1-minute load. Critical outranks Warning, which outranks Healthy.
  - [ ] Unit-test a sample that is Healthy except for one Critical disk, and expect Critical.
  - [ ] Security: the result includes the text label that the UI will show, so a later template can render the word and the color together.
  - [ ] Docs: describe the “worst wins” rule in `README.md`.

- [ ] **6.3 Read thresholds from config**
  - [ ] Use the `thresholds` object from `config/monitoring.json`. Load-average limits stay derived from the core count.
  - [ ] Unit-test that raising `cpu_warning` in a temp config changes the classification.
  - [ ] Security: a missing threshold key fails the load with the key name. The app does not silently switch to a looser limit.
  - [ ] Docs: say in `README.md` that editing the threshold numbers is a config change, followed by a process restart.

## 7. Live read-only view

- [ ] **7.1 List servers for a signed-in user**
  - [ ] Add `GET /api/servers`. Return id, name, hostname, environment, team, and overall status. Anonymous callers receive HTTP 401.
  - [ ] Test `viewer`, `admin`, and an anonymous client.
  - [ ] Security: the JSON has no user records and no password hashes. Query text is escaped by JSON encoding.
  - [ ] Docs: add the endpoint to a Routes section in `README.md`.

- [ ] **7.2 Return one sample**
  - [ ] Add `GET /api/servers/<id>` with a fresh sample and the status of each metric. Unknown ids return HTTP 404. Anonymous callers receive HTTP 401.
  - [ ] Test a seeded id, a missing id, and an anonymous client.
  - [ ] Security: the handler reads the inventory and returns a sample. It has no write path.
  - [ ] Docs: document the sample endpoint and the 404 behavior in `README.md`.

- [ ] **7.3 Render the server list**
  - [ ] On `/`, show each server’s name, hostname, environment, team, and overall status label. Selecting a row marks it selected.
  - [ ] Test that the seeded names appear for a signed-in user and that status text is in the HTML.
  - [ ] Security: render server fields with normal template escaping. A name that contains HTML shows as text.
  - [ ] Docs: describe the list columns in `README.md`.

- [ ] **7.4 Render the selected server**
  - [ ] Show CPU overall and per core, memory, swap, both disks, load average, and uptime. Percentages use one decimal. Sizes use GiB. Uptime uses days, hours, and minutes.
  - [ ] Test the formatting helpers with fixed numbers.
  - [ ] Security: metric values are numbers rendered as text. The template does not inject raw JSON into HTML.
  - [ ] Docs: describe the detail cards and the number formats in `README.md`.

- [ ] **7.5 Refresh every 5 seconds**
  - [ ] Add `app/static/js/monitor.js`. Poll the sample endpoint every 5 seconds. Update the open server in place. Show `Last updated`. On a failed poll, keep the previous numbers and show that the update failed.
  - [ ] Test the failure message behavior with a small helper, or a focused test of the “keep last sample” rule if the script is structured so the rule can run without a browser.
  - [ ] Security: build DOM updates with `textContent` or equivalent. The script does not read `innerHTML` from the API payload.
  - [ ] Docs: document the 5-second refresh and the failed-update message in `README.md`.

- [ ] **7.6 Show an empty inventory**
  - [ ] When `servers` is empty, show that no servers are configured. Leave the detail region empty.
  - [ ] Test a temp config with zero servers for a signed-in viewer.
  - [ ] Security: the empty page still requires a session. It does not offer a way to change users or thresholds.
  - [ ] Docs: quote the empty-state sentence in `README.md`.

## 8. Admin server changes

- [ ] **8.1 Add a server from the admin page**
  - [ ] On the same `/` page, an admin gets a form: name, hostname, environment, team, and profile. `os` is Linux and is not a choice. `POST /api/servers` appends the server and returns it.
  - [ ] Test that the new server is in the following `GET /api/servers` result and can be sampled.
  - [ ] Security: the route checks the session role on the server. A hidden form is not the control. `viewer` receives HTTP 403.
  - [ ] Docs: add the admin form fields to `README.md`.

- [ ] **8.2 Validate the add form**
  - [ ] Reject a missing name, hostname, or profile, and reject a duplicate display name. Return the errors and keep the submitted values. Ids are generated by the app.
  - [ ] Test the duplicate-name case and a blank name.
  - [ ] Security: the id is server-generated. The client cannot choose an id that overwrites another record. Input is stored as data, not as markup.
  - [ ] Docs: list the validation messages in `README.md`.

- [ ] **8.3 Edit a server**
  - [ ] `PUT /api/servers/<id>` updates name, hostname, environment, team, and profile. Unknown ids return HTTP 404.
  - [ ] Test a name change and a missing id.
  - [ ] Security: `viewer` receives HTTP 403. The handler uses the atomic writer from step 4.3.
  - [ ] Docs: document edit in `README.md`.

- [ ] **8.4 Remove a server**
  - [ ] The admin UI asks for confirmation, then calls `DELETE /api/servers/<id>`. If the removed server was selected, select another server, or show the empty state.
  - [ ] Test delete, the 404 that follows, and a viewer’s HTTP 403.
  - [ ] Security: deletion is authorized on the server. Confirmation is in the UI so a mis-click is not the only safeguard; the role check still stands.
  - [ ] Docs: describe confirm-and-remove in `README.md`.

- [ ] **8.5 Hide write controls from viewers**
  - [ ] The viewer HTML has no add, edit, or remove controls. The admin HTML has them on this same page. Metrics stay read-only for both roles.
  - [ ] Test the HTML for both roles, and repeat the 403 tests for `POST`, `PUT`, and `DELETE`.
  - [ ] Security: both layers exist. The UI hides the controls, and the endpoints reject the viewer.
  - [ ] Docs: state the role split in `README.md`.

- [ ] **8.6 Prove the config stays intact**
  - [ ] After an add, an edit, and a delete, `users` and `thresholds` match the file from before the changes, and both password hashes still start with `pbkdf2:sha256`.
  - [ ] Automate that assertion in a test that uses a temp copy of the config.
  - [ ] Security: this is the regression test for “inventory edits do not rewrite accounts.”
  - [ ] Docs: mention the guarantee in `README.md`.

## 9. Acceptance pass

- [ ] **9.1 Walk the spec’s acceptance list**
  - [ ] Check each of the nine acceptance items in `docs/requirements.md` against the running app and the tests. Note any gap as a new checkbox under this step rather than expanding scope.
  - [ ] Security: during the walk-through, confirm the viewer cannot mutate inventory, the error sentence stays generic, and the config still holds hashes.
  - [ ] Docs: add a short “Checked against the spec” note to `README.md` with the date of the pass.

- [ ] **9.2 Leave a demo runbook**
  - [ ] `README.md` covers install, the required `FLASK_SECRET_KEY`, both seeded users, the three seeded servers, refresh behavior, admin add/edit/remove, tests, and the two GitHub Actions workflows.
  - [ ] Security: the runbook tells the reader the demo is for a local or private environment and that the published demo password must not be reused.
  - [ ] Docs: this step is the final read of `README.md`. Remove leftover notes about the temporary public placeholder.

- [ ] **9.3 Confirm CI and CD**
  - [ ] `pytest` passes locally. The CI workflow is the test gate. The CD workflow is manual and stops after `GET /login` returns 200.
  - [ ] Security: workflow permissions stay read-only, and neither workflow deploys the app or prints `FLASK_SECRET_KEY`.
  - [ ] Docs: the `README.md` CI section matches the workflow filenames and how to run them.
