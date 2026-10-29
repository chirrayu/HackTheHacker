# Safe lab setup

Phase 1 requires a disposable virtual machine or equivalent isolated lab environment before any honeypot deployment.

## Required controls

- Use a dedicated, least-privilege VM account with no personal data, production credentials, private keys, or cloud tokens.
- Start with host-only or otherwise restricted networking. Do not use bridged networking or public port forwarding during initial validation.
- Restrict outbound access to explicitly required package and update sources. Keep inbound SSH access limited to the administrator's lab network.
- Establish a tested snapshot or clean recovery image before installing Cowrie.
- Record the VM image version, OS version, network mode, exposed ports, and recovery procedure in the lab run notes.

## Readiness gate

Do not proceed to Phase 2 until the operator has verified isolation, SSH access from the authorized management host, restrictive firewall rules, and successful recovery from a snapshot. This repository does not automatically create or expose a VM.

Complete `docs/lab-readiness.md` during the environment review. Keep hostnames, addresses, and credentials out of version control if the record contains sensitive deployment details.

## Local Python checks

From the repository root, create a virtual environment and install dependencies using the commands documented in `README.md`. Use synthetic fixtures until the isolated lab is approved.

## Windows host note

The repository workspace does not provision a hypervisor. Install and configure an approved virtualization tool outside this project, then use a disposable Linux guest with host-only or otherwise restricted networking. Do not expose SSH or Cowrie ports publicly during this phase.
