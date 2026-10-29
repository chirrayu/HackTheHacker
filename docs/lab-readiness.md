# Phase 1 lab readiness record

This checklist is completed by the operator before Cowrie is installed. It is intentionally a template and contains no real host details.

## Environment

- [ ] Disposable Linux VM or equivalent isolated environment created.
- [ ] VM image and OS version recorded in a private operator log.
- [ ] No personal data, production credentials, private keys, or cloud tokens are present.
- [ ] A least-privilege administration account is available.
- [ ] A clean snapshot or recovery image exists.

## Network isolation

- [ ] Network mode is host-only, internal, or otherwise restricted.
- [ ] Bridged networking is disabled for initial testing.
- [ ] Public port forwarding is disabled.
- [ ] Inbound access is limited to the authorized management host.
- [ ] Outbound access is restricted to explicitly required package/update sources.
- [ ] Host and guest firewall defaults are restrictive and have been verified.

## SSH validation

- [ ] SSH is enabled only on the intended management interface.
- [ ] SSH login from the authorized management host succeeds.
- [ ] Password or key policy is documented without storing secrets here.
- [ ] Unauthorized network paths to SSH have been tested and rejected.

## Recovery validation

- [ ] The VM was stopped and restored from the clean snapshot.
- [ ] The restored guest boots successfully.
- [ ] SSH access still works after restoration.
- [ ] The operator knows how to discard and recreate the guest.

## Phase 1 decision

- Status: `NOT READY` until every applicable checkbox above is verified.
- Reviewer:
- Date:
- Notes:

Do not begin Phase 2 while this record is `NOT READY`. Do not commit a completed record if it contains sensitive infrastructure details.
