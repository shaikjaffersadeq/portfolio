# Incident Timeline — SSH Brute-Force Investigation

## Incident Overview

This timeline documents the controlled SSH authentication testing
performed in the SOC laboratory environment.

The purpose was to identify repeated failed authentication attempts,
correlate them with the source IP and target account, and determine
whether a successful authentication occurred after the failed attempts.

---

## Lab Timeline

| Stage | Activity | Details |
|------|----------|---------|
| 1 | SSH Service Preparation | OpenSSH server configured on Ubuntu |
| 2 | Connectivity Test | Kali connected to Ubuntu over the Host-only network |
| 3 | Authentication Test | Controlled SSH login attempts performed from Kali |
| 4 | Failed Authentication | Multiple incorrect-password attempts generated |
| 5 | Log Collection | `/var/log/auth.log` reviewed on Ubuntu |
| 6 | Source Identification | Source IP identified as `192.168.56.103` |
| 7 | Target Identification | Target IP identified as `192.168.56.102` |
| 8 | Account Identification | Target account identified as `snowden` |
| 9 | Authentication Correlation | Logs checked for successful authentication |
| 10 | Investigation Result | No successful authentication observed immediately after the failed sequence |

---

## Observed Authentication Events

### Event 1 — Failed Authentication

**Source IP:** `192.168.56.103`

**Destination IP:** `192.168.56.102`

**Account:** `snowden`

**Service:** SSH

**Event Type:** Failed password

**Result:** Authentication failed

---

### Event 2 — Failed Authentication

**Source IP:** `192.168.56.103`

**Destination IP:** `192.168.56.102`

**Account:** `snowden`

**Service:** SSH

**Event Type:** Failed password

**Result:** Authentication failed

---

### Event 3 — Failed Authentication

**Source IP:** `192.168.56.103`

**Destination IP:** `192.168.56.102`

**Account:** `snowden`

**Service:** SSH

**Event Type:** Failed password

**Result:** Authentication failed

---

## Failed Attempt Summary

The controlled test produced:

**3 failed SSH authentication attempts**

from:

`192.168.56.103`

against:

`snowden`

on:

`192.168.56.102`

---

## Successful Authentication Correlation

An earlier successful SSH authentication from the same source and
account was observed before the controlled failed-login sequence.

This earlier successful authentication was treated separately from
the simulated failed-login activity.

A subsequent search for:

`Accepted password for snowden from 192.168.56.103`

did not identify a successful authentication immediately following
the controlled failed-login sequence.

Therefore, there is no evidence from this test that the failed-login
sequence resulted in successful authentication.

---

## Detection Point

The investigation identifies the following detection condition:

> IF 3 or more failed SSH authentication attempts occur from the same
> source IP against the same account within a short time window,
> generate a potential SSH brute-force alert.

This is a laboratory detection threshold used to demonstrate SOC
investigation and correlation logic.

---

## SOC Analyst Interpretation

The repeated authentication failures are consistent with potential
SSH brute-force or password-guessing activity.

However, repeated failed authentication alone does not prove that an
attack was successful.

The investigation therefore focused on:

- Source IP identification
- Target IP identification
- Target account identification
- Number of failed attempts
- Authentication timeline
- Successful-login correlation
- Final access outcome

---

## Incident Classification

**Classification:** Potential SSH Brute-Force Activity

**Severity:** Medium

**Status:** Investigated

**Successful Authentication After Test:** Not observed

**Compromise Confirmed:** No

---

## Recommended SOC Actions

If this occurred in a production environment, an analyst should:

1. Review additional SSH authentication logs.
2. Determine whether the source IP generated similar activity against
   other accounts or systems.
3. Check for successful authentication following the failed attempts.
4. Review the authenticated user's activity if a successful login is
   identified.
5. Correlate the source IP with firewall, VPN, endpoint, and SIEM logs.
6. Determine whether the source is authorized security-testing
   infrastructure.
7. Apply appropriate blocking or rate-limiting controls if malicious
   activity is confirmed.

---

## Investigation Conclusion

The controlled investigation successfully demonstrated how a SOC
analyst can identify and investigate repeated SSH authentication
failures.

Three failed authentication attempts were observed from
`192.168.56.103` against the `snowden` account on
`192.168.56.102`.

No successful authentication was observed immediately after the
controlled failed-login sequence.

The activity was therefore classified as **Potential SSH Brute-Force
Activity — Medium Severity**, with no confirmed compromise.

---

**Analyst:** Shaik Jaffer Sadeq  
**Project:** SOC Brute-Force Login Detection & Investigation  
**Environment:** Isolated SOC Laboratory
