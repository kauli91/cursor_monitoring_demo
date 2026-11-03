# Demo Monitoring Infrastructure — Product Requirements

**Status:** Draft  
**Product:** Demo monitoring for Linux servers  
**Audience:** L1, L2, and L3 infrastructure teams, and application development teams  
**Stack:** Python, Flask  

This document is the software specification for a classroom-style demo. It describes what the product must do so that an implementer can build it without inventing scope.

## 1. Problem

Internal teams currently sign in to individual Linux servers to see whether a host is healthy. That check is slow, easy to do inconsistently, and requires shell access for people who only need to look.

This demo gives those teams one read-only place to see the current CPU, memory, disk, load average, and uptime of the Linux servers they care about. The numbers are simulated. The demo does not connect to real hosts.

## 2. Goals

- Show current server health on one screen, without a shell login.
- Refresh those values automatically so the page feels live.
- Let every signed-in user view servers, and let only the admin account add, edit, or remove servers.
- Ship a clear, attractive Flask UI that L1 can use without training.
- Keep the server list and accounts in a local config file.

## 3. Users and roles

| Role | Who | What they can do |
| --- | --- | --- |
| Viewer | L1, L2, L3, and application developers | Sign in and view the server list and current metrics |
| Admin | A designated operator of the demo | Everything a viewer can do, plus add, edit, and remove servers |

Accounts are not created in the UI. They are entries in the config file.

Two accounts are seeded so both roles can be demonstrated:

| Username | Role | Initial password |
| --- | --- | --- |
| `admin` | admin | `MonitorDemo#1` |
| `viewer` | viewer | `MonitorDemo#1` |

The config file stores only a password hash. The plaintext passwords above are the demo secrets used to generate that hash. They are acceptable only because this application is a demo.

## 4. Decisions that bound this version

These choices define the demo. They are requirements, not suggestions.

| Topic | Requirement |
| --- | --- |
| Data source | Simulated samples. The app never opens SSH, installs an agent, or calls a real host. |
| History | Current values only. Samples are not stored. |
| Refresh | The open page fetches new values every 5 seconds. |
| Inventory storage | One local JSON config file. No database. |
| Screens | A sign-in page, then one monitoring page. |
| Metrics | CPU, memory (including swap), disk per mount, load average, and uptime. |
| Warnings | Color and a text label when a metric crosses a threshold. No alert list, email, or paging. |
| Server type | Linux only. |

Network throughput and port usage motivated the original problem and are deferred. See section 12.

## 5. Experience

### 5.1 Sign-in

The sign-in page asks for username and password. A failed attempt shows one message: “Invalid username or password.” The message does not say which field was wrong. A successful sign-in opens the monitoring page. A signed-in user can sign out, which ends the session and returns to the sign-in page.

Visiting the monitoring page without a session redirects to sign-in.

### 5.2 Monitoring page

After sign-in, the user works on a single page:

- A server list shows every configured server: display name, hostname, environment, owning team, and an overall status.
- Selecting a server shows that server’s current metrics beside or below the list.
- The selected server stays selected across refreshes.
- A “Last updated” time shows when the latest sample arrived.
- If a refresh fails, the page keeps the last sample and shows that the update failed.

Empty inventory: the page states that no servers are configured. The admin sees the add-server form. A viewer sees the empty message and no form.

### 5.3 Read-only viewing

Metrics are never editable. Viewers do not see add, edit, or remove controls. Direct calls to the mutating endpoints by a viewer receive HTTP 403.

The admin uses the same page. Add, edit, and remove are part of that page, not a separate screen. Remove asks for confirmation.

### 5.4 Presentation

The UI is a Flask-rendered page with its own CSS. It should be readable at a glance on a laptop:

- Status is shown with a label (Healthy, Warning, Critical) as well as color, so color is not the only signal.
- Healthy is green, Warning is amber, Critical is red.
- Percentages use one decimal place. Memory and disk sizes use GiB. Uptime is shown in days, hours, and minutes. Load average shows the 1-, 5-, and 15-minute values.
- The layout has a clear header, a scannable server list, and metric cards for the selected host. Spacing and type size favor quick scanning over dense tables.
- The page is usable from 1024 pixels wide upward.

## 6. Functional requirements

### Authentication

- **FR-1.** The app provides username and password sign-in.
- **FR-2.** The seeded admin username is `admin`.
- **FR-3.** Passwords are stored as hashes produced by Werkzeug (`pbkdf2:sha256`). The app never writes plaintext passwords to the config file, logs, or pages.
- **FR-4.** Sign-in compares the submitted password with `check_password_hash`.
- **FR-5.** A session lasts until the user signs out or the session expires after 8 hours of inactivity.
- **FR-6.** Unauthenticated requests to the monitoring page and the JSON endpoints redirect to sign-in or return HTTP 401.

### Server inventory

- **FR-7.** A server record has: unique id, display name, hostname or IP, environment, owning team, and a simulation profile (`steady`, `busy`, or `stressed`). Display name, hostname, and profile are required. Environment and team may be blank.
- **FR-8.** Every server is recorded as Linux. The admin cannot choose another operating system.
- **FR-9.** The admin can add a server. The new server appears in the list and can be selected immediately.
- **FR-10.** The admin can edit a server’s display name, hostname, environment, team, and simulation profile.
- **FR-11.** The admin can remove a server after confirmation. If the removed server was selected, the page selects another server, or shows the empty state when none remain.
- **FR-12.** Display names must be unique. The form explains the validation error and keeps the entered values.
- **FR-13.** Create, update, and delete write the servers section of the config file. Users and thresholds in that file are left unchanged. The write is atomic (write a temporary file, then replace the config).

### Metrics

- **FR-14.** Selecting a server shows a current sample with:
  - CPU: overall percent and one value per core
  - Memory: total, used, free, and used percent
  - Swap: total, used, and used percent
  - Disk: for each mount, mount point, total, used, free, and used percent
  - Load average: 1, 5, and 15 minutes
  - Uptime
- **FR-15.** The monitoring page requests a new sample every 5 seconds without a full page reload.
- **FR-16.** Samples are not written to disk or to a database.
- **FR-17.** Successive samples for one server move smoothly around that server’s profile. They do not jump from idle to critical at random.
- **FR-18.** Each server uses fixed simulated hardware so the numbers stay believable across refreshes:
  - CPU count stays constant per server (4 cores for `steady`, 8 for `busy` and `stressed`)
  - Memory total stays constant (16 GiB)
  - Swap total stays constant (4 GiB)
  - Disk totals stay constant. At least two mounts are shown (`/` and `/var`)
  - Uptime increases with wall-clock time from a fixed boot timestamp stored with the server
- **FR-19.** Profiles produce values in these bands often enough that the color rules in FR-20 are visible during a short demo:

  | Profile | CPU | Memory used | A disk mount | 1-minute load |
  | --- | --- | --- | --- | --- |
  | steady | 15–35% | 40–55% | about 45% | below the CPU count |
  | busy | 60–80% | 70–85% | 75–88% | around the CPU count |
  | stressed | 88–98% | 90–97% | 92–98% | above twice the CPU count |

  Per-core CPU values vary around the overall percentage. The 5- and 15-minute load values move with the 1-minute value and are less volatile.

### Status colors

- **FR-20.** Each metric below is classified with these default thresholds. A value at or above the critical mark is Critical. A value at or above the warning mark and below the critical mark is Warning. Otherwise it is Healthy.

  | Metric | Warning | Critical |
  | --- | --- | --- |
  | CPU overall | 70% | 90% |
  | Memory used | 75% | 90% |
  | Swap used | 50% | 80% |
  | Any disk mount | 80% | 95% |
  | Load average, 1 minute | greater than or equal to the CPU count | greater than or equal to twice the CPU count |

- **FR-21.** The server’s overall status is the worst status among CPU, memory, swap, disk mounts, and 1-minute load. Critical outranks Warning, which outranks Healthy.
- **FR-22.** Thresholds are read from the config file so they can be changed without a code edit. The values in FR-20 are the defaults shipped with the demo.

## 7. Config file

Path: `config/monitoring.json`.

```json
{
  "thresholds": {
    "cpu_warning": 70,
    "cpu_critical": 90,
    "memory_warning": 75,
    "memory_critical": 90,
    "swap_warning": 50,
    "swap_critical": 80,
    "disk_warning": 80,
    "disk_critical": 95
  },
  "users": [
    {
      "username": "admin",
      "role": "admin",
      "password_hash": "<werkzeug pbkdf2:sha256 hash>"
    },
    {
      "username": "viewer",
      "role": "viewer",
      "password_hash": "<werkzeug pbkdf2:sha256 hash>"
    }
  ],
  "servers": [
    {
      "id": "web-01",
      "name": "Web 01",
      "hostname": "web-01.internal",
      "environment": "demo",
      "team": "Application",
      "os": "linux",
      "profile": "steady",
      "booted_at": "2026-11-01T00:00:00Z"
    }
  ]
}
```

The shipped file includes three servers, one of each profile, so Healthy, Warning, and Critical can be shown before anyone adds a host.

Load thresholds are not separate numbers. They are defined from the simulated CPU count in FR-20.

## 8. Interfaces

The browser UI is server-rendered. Live numbers come from JSON endpoints.

| Method | Path | Who | Behavior |
| --- | --- | --- | --- |
| GET | `/login` | public | Sign-in page |
| POST | `/login` | public | Start a session or redisplay the error |
| POST | `/logout` | signed in | End the session |
| GET | `/` | signed in | Monitoring page |
| GET | `/api/servers` | signed in | Server list and overall status |
| GET | `/api/servers/<id>` | signed in | One new simulated sample |
| POST | `/api/servers` | admin | Add a server |
| PUT | `/api/servers/<id>` | admin | Edit a server |
| DELETE | `/api/servers/<id>` | admin | Remove a server |

Viewer calls to `POST`, `PUT`, and `DELETE` return HTTP 403. Unknown server ids return HTTP 404.

## 9. Technical requirements

- **TR-1.** The application is Python 3 and Flask. Flask renders the HTML. CSS shipped with the app styles the pages. A small script on the monitoring page polls the JSON endpoints.
- **TR-2.** No database, message queue, or external monitoring stack is required.
- **TR-3.** The app runs as one local process and reads `config/monitoring.json` from the project directory.
- **TR-4.** Session cookies are signed with Flask’s secret key, read from the environment variable `FLASK_SECRET_KEY`. The repo documents a demo value and does not commit a production secret.
- **TR-5.** Dependencies stay small: Flask and its normal dependency set (including Werkzeug). The standard library handles JSON.

## 10. Non-functional requirements

- **NFR-1.** A sample response for one server is generated and returned in under 100 ms on a developer laptop. The demo inventory is expected to stay under 50 servers.
- **NFR-2.** With the monitoring page open, the visible numbers change within one refresh interval after the clock ticks, under a normal local load.
- **NFR-3.** The sign-in form and the server form can be completed with the keyboard. Status text is present in the markup, not only in color.
- **NFR-4.** Failed sign-in attempts and failed config writes are logged without passwords or password hashes.

## 11. Security notes for the demo

This is a demo, and the following limits are part of the specification:

- Simulated hosts only. There are no server credentials to steal.
- The default passwords are public in this document. Do not reuse them anywhere real.
- Authorization is enforced on the server for every mutating request, not only by hiding buttons.
- The config file is the source of truth for who is an admin.

The app is not intended for exposure beyond the demo environment.

## 12. Out of scope

This version does not include:

- Live collection from real Linux hosts (SSH, agents, SNMP, or cloud APIs)
- Network throughput, interface counters, listening ports, or established connections
- Stored history, charts over time, or a retention policy
- An alert inbox, email, chat, or paging
- User-registration screens, password change, or password reset
- Roles finer than admin and viewer
- Windows or other operating systems
- High availability, multiple app instances, or concurrent writers of the config file

A later version can add network and port details, then replace the simulator with a real collector, without changing the monitoring page’s overall layout.

## 13. Acceptance criteria

The demo is complete when all of the following are true.

1. Opening the app while signed out shows the sign-in page.
2. `viewer` / `MonitorDemo#1` reaches the monitoring page. The seeded servers are listed. Selecting each profile shows CPU, per-core CPU, memory, swap, at least two disk mounts, load average, and uptime.
3. Waiting longer than 5 seconds updates the numbers without a full reload. Leaving and coming back does not require the app to have stored the earlier samples.
4. `steady` is Healthy, `busy` reaches Warning, and `stressed` reaches Critical under the default thresholds. Each status includes a text label.
5. The viewer page has no add, edit, or remove controls. A viewer request to add a server is rejected with HTTP 403.
6. `admin` / `MonitorDemo#1` can add a Linux server with the `stressed` profile, see it in the list, edit its name, and remove it after confirmation. The config file matches those changes, and the user hashes in that file are still hashes.
7. A wrong password shows “Invalid username or password” and does not start a session.
8. Signing out blocks access to the monitoring page until the next successful sign-in.
9. `config/monitoring.json` is the only store for users, thresholds, and servers. No database is required to run the demo.
