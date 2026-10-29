# Phase 2: Cowrie deployment

This procedure installs Cowrie inside the already isolated VM. Keep the VM on the host-only network and use Cowrie's default SSH port `2222` for local validation. Do not expose the VM publicly or redirect port 22 during this phase.

The commands follow the official Cowrie pip installation path. Cowrie currently requires Python 3.11 or newer for the current stable documentation.

## 1. Install system prerequisites

Run in the Kali or Debian-based guest:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential libssl-dev libffi-dev libpython3-dev
python3 --version
```

If the VM has no temporary package access, enable restricted NAT only for this installation, then disable NAT and return to host-only networking before validation.

## 2. Create a dedicated account and state directory

```bash
sudo adduser --disabled-password --gecos "" cowrie
sudo -iu cowrie
mkdir -p ~/my-honeypot
cd ~/my-honeypot
```

Do not run Cowrie as root. Keep the state directory inside the VM and do not copy raw logs into this repository.

## 3. Install and initialize Cowrie

```bash
python3 -m venv cowrie-env
source cowrie-env/bin/activate
python -m pip install --upgrade pip
python -m pip install cowrie
cowrie init
```

`cowrie init` creates the operator-owned configuration at `etc/cowrie.cfg`. Cowrie's default SSH listener is port `2222`, which avoids interfering with the VM's administrative SSH service on port `22`.

Ensure the JSON output plugin is enabled in `etc/cowrie.cfg`:

```ini
[output_jsonlog]
enabled = true
```

Leave the SSH listener on its default port for this phase. Do not add port forwarding, public bind rules, proxy mode, backend pools, or Telnet unless a later phase explicitly requires them.

## 4. Start and validate locally

From the Cowrie state directory, with the virtual environment active:

```bash
cowrie start
tail -f var/log/cowrie/cowrie.log
```

From the authorized Windows host, connect through the host-only IP and Cowrie port:

```powershell
ssh -p 2222 root@<vm-host-only-ip>
```

Use a synthetic test login. The goal is only to create controlled telemetry; do not use real credentials.

Stop the session and inspect the JSON log in the VM:

```bash
tail -n 5 var/log/cowrie/cowrie.json
```

Confirm that records contain fields such as `eventid`, `timestamp`, `session`, and `src_ip`. Do not paste raw credentials or session content into GitHub, this repository, or chat.

## 5. Phase 2 acceptance checks

- [ ] Cowrie runs as the dedicated non-root `cowrie` user.
- [ ] The VM remains host-only and has no port-forwarding rules.
- [ ] Cowrie listens only on the restricted VM interface and port `2222`.
- [ ] A controlled SSH connection to port `2222` succeeds.
- [ ] `var/log/cowrie/cowrie.json` is created and contains a synthetic test event.
- [ ] The Cowrie process can be stopped cleanly with `cowrie stop`.
- [ ] Raw logs remain inside the isolated VM and are not committed.

Do not proceed to production-like exposure or public collection. Phase 3 will consume sanitized JSONL records using this project's parser.
