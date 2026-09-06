<div align="center">

<h1>🛡️ SOC Brute-Force Login Investigation Report</h1>

<h3>SSH Authentication Monitoring & Investigation</h3>

<p>
<strong>Incident Type:</strong> Potential SSH Brute-Force Activity
<br>
<strong>Severity:</strong> Medium
<br>
<strong>Status:</strong> Investigated
</p>

</div>

<hr>

<h2>1. Executive Summary</h2>

<p>
A controlled SSH authentication investigation was conducted in an isolated
cybersecurity laboratory environment.
</p>

<p>
The objective was to identify and analyze repeated failed SSH authentication
attempts against an Ubuntu Linux server.
</p>

<p>
During the investigation, three failed authentication attempts were
identified from the Kali Linux system at
<code>192.168.56.103</code> against the
<code>snowden</code> account on the Ubuntu server at
<code>192.168.56.102</code>.
</p>

<p>
The events were recorded in the Ubuntu authentication log:
</p>

<pre><code>/var/log/auth.log</code></pre>

<p>
The repeated failures from the same source against the same account were
classified as <strong>Potential SSH Brute-Force Activity</strong>.
</p>

<p>
No successful authentication was observed immediately following the
controlled failed-login sequence.
</p>

<hr>

<h2>2. Investigation Objective</h2>

<p>
The investigation was designed to demonstrate a basic SOC authentication
monitoring workflow.
</p>

<ul>
<li>Identify failed SSH authentication events.</li>
<li>Identify the source IP address.</li>
<li>Identify the targeted account.</li>
<li>Determine the number of failed attempts.</li>
<li>Analyze the event timestamps.</li>
<li>Check for successful authentication following the failures.</li>
<li>Determine whether the activity represents a potential brute-force pattern.</li>
<li>Develop detection logic.</li>
<li>Document the investigation.</li>
</ul>

<hr>

<h2>3. Investigation Environment</h2>

<table>

<tr>
<th>Component</th>
<th>Details</th>
</tr>

<tr>
<td>Test / Analyst Machine</td>
<td>Kali Linux</td>
</tr>

<tr>
<td>Target Machine</td>
<td>Ubuntu Linux</td>
</tr>

<tr>
<td>Source IP</td>
<td><code>192.168.56.103</code></td>
</tr>

<tr>
<td>Destination IP</td>
<td><code>192.168.56.102</code></td>
</tr>

<tr>
<td>Protocol</td>
<td>SSH</td>
</tr>

<tr>
<td>Service</td>
<td>OpenSSH</td>
</tr>

<tr>
<td>Target Account</td>
<td><code>snowden</code></td>
</tr>

<tr>
<td>Authentication Log</td>
<td><code>/var/log/auth.log</code></td>
</tr>

</table>

<hr>

<h2>4. Lab Preparation</h2>

<p>
The Ubuntu system was configured as the SSH target.
The OpenSSH service was verified to be running.
</p>

<p>
The Kali Linux machine communicated with Ubuntu over the isolated
Host-Only laboratory network.
</p>

<p>
The connectivity path was:
</p>

<pre><code>
Kali Linux
192.168.56.103
      |
      | SSH
      ↓
Ubuntu Linux
192.168.56.102
      |
      ↓
OpenSSH
</code></pre>

<hr>

<h2>5. Controlled Authentication Testing</h2>

<p>
Controlled failed SSH authentication attempts were generated from Kali
Linux against the Ubuntu SSH service.
</p>

<p>
An incorrect password was intentionally entered during the test.
</p>

<p>
The resulting authentication failures were recorded by Ubuntu in:
</p>

<pre><code>/var/log/auth.log</code></pre>

<p>
Three failed authentication events were identified for the controlled
investigation sequence.
</p>

<hr>

<h2>6. Authentication Log Analysis</h2>

<p>
The authentication log was searched for failed password events associated
with the target username and source IP.
</p>

<p>The relevant event pattern was:</p>

<pre><code>
Failed password for snowden from 192.168.56.103
</code></pre>

<p>
The investigation confirmed that the same source IP repeatedly attempted
authentication against the same account.
</p>

<hr>

<h2>7. Observed Evidence</h2>

<table>

<tr>
<th>Field</th>
<th>Finding</th>
</tr>

<tr>
<td>Source IP</td>
<td><code>192.168.56.103</code></td>
</tr>

<tr>
<td>Destination IP</td>
<td><code>192.168.56.102</code></td>
</tr>

<tr>
<td>Target Account</td>
<td><code>snowden</code></td>
</tr>

<tr>
<td>Service</td>
<td>SSH</td>
</tr>

<tr>
<td>Failed Authentication Events</td>
<td><strong>3</strong></td>
</tr>

<tr>
<td>Authentication Result</td>
<td>Failed</td>
</tr>

<tr>
<td>Classification</td>
<td>Potential SSH Brute-Force Activity</td>
</tr>

<tr>
<td>Severity</td>
<td><strong>Medium</strong></td>
</tr>

</table>

<hr>

<h2>8. Incident Timeline</h2>

<p>
The controlled failed-login events occurred within a short period.
</p>

<table>

<tr>
<th>Event</th>
<th>Source IP</th>
<th>Target Account</th>
<th>Result</th>
</tr>

<tr>
<td>SSH Authentication Attempt</td>
<td><code>192.168.56.103</code></td>
<td><code>snowden</code></td>
<td>Failed</td>
</tr>

<tr>
<td>SSH Authentication Attempt</td>
<td><code>192.168.56.103</code></td>
<td><code>snowden</code></td>
<td>Failed</td>
</tr>

<tr>
<td>SSH Authentication Attempt</td>
<td><code>192.168.56.103</code></td>
<td><code>snowden</code></td>
<td>Failed</td>
</tr>

</table>

<p>
The repeated failures from the same source against the same account
formed the basis for the potential brute-force classification.
</p>

<hr>

<h2>9. Successful Authentication Correlation</h2>

<p>
During the investigation, an earlier successful SSH authentication from
<code>192.168.56.103</code> was identified in the authentication logs.
</p>

<p>
However, this successful authentication occurred <strong>before</strong>
the controlled failed-login sequence.
</p>

<p>
Therefore, it was not interpreted as a successful brute-force login.
</p>

<p>
No successful authentication was observed immediately following the
controlled failed-login sequence.
</p>

<div align="center">

<h3>Authentication Assessment</h3>

<p>
<strong>
No evidence of successful authentication following the controlled
failed-login sequence was observed.
</strong>
</p>

</div>

<hr>

<h2>10. Detection Criteria</h2>

<p>
For this laboratory investigation, the detection threshold was defined as:
</p>

<pre><code>
3 or more failed SSH authentication attempts
from the same source IP
against the same username
within a short time period
</code></pre>

<p>
The observed activity met this controlled threshold.
</p>

<hr>

<h2>11. SOC Analyst Reasoning</h2>

<p>
A single failed authentication attempt is not necessarily malicious.
It can occur because of an incorrect password or user error.
</p>

<p>
However, repeated failed authentication attempts from the same source
against the same account can indicate:
</p>

<ul>
<li>Password guessing</li>
<li>Brute-force authentication</li>
<li>Automated authentication attempts</li>
<li>Unauthorized access attempts</li>
</ul>

<p>
A SOC Analyst should correlate failed authentication events with successful
authentication, account activity, source reputation and other available
security telemetry before determining whether an account has actually
been compromised.
</p>

<hr>

<h2>12. IOC Identification</h2>

<table>

<tr>
<th>IOC / Indicator</th>
<th>Value</th>
</tr>

<tr>
<td>Source IP</td>
<td><code>192.168.56.103</code></td>
</tr>

<tr>
<td>Destination IP</td>
<td><code>192.168.56.102</code></td>
</tr>

<tr>
<td>Target Account</td>
<td><code>snowden</code></td>
</tr>

<tr>
<td>Service</td>
<td>SSH</td>
</tr>

<tr>
<td>Event Type</td>
<td>Failed Authentication</td>
</tr>

</table>

<hr>

<h2>13. Impact Assessment</h2>

<p>
The observed activity represents repeated failed authentication attempts
against an SSH account.
</p>

<p>
The activity could represent password guessing or automated brute-force
behavior in a real environment.
</p>

<p>
However, this laboratory investigation did not identify a successful
authentication immediately following the controlled failed-login sequence.
</p>

<p>
Therefore, there is no evidence from this test alone that the target
account was successfully compromised.
</p>

<hr>

<h2>14. Recommended SOC Actions</h2>

<ol>

<li>
Validate whether the source IP is authorized to access the SSH server.
</li>

<li>
Review authentication logs for additional failed-login activity.
</li>

<li>
Search for successful logins from the same source IP.
</li>

<li>
Determine whether other usernames were targeted.
</li>

<li>
Review account activity following suspicious authentication attempts.
</li>

<li>
Investigate the source host if the activity is unauthorized.
</li>

<li>
Consider additional authentication protections such as rate limiting,
account lockout policies or stronger authentication controls where
appropriate.
</li>

<li>
Escalate the incident if evidence of successful compromise is discovered.
</li>

</ol>

<hr>

<h2>15. Detection Improvement</h2>

<p>
A production SOC should avoid relying only on a total count across an
entire log file.
</p>

<p>
A more realistic detection would correlate:
</p>

<pre><code>
Source IP
+
Target Username
+
Failed Authentication Count
+
Time Window
+
Successful Authentication
</code></pre>

<p>
For example:
</p>

<pre><code>
3+ failed SSH logins
from the same source
against the same account
within 60 seconds
</code></pre>

<p>
This reduces false positives and makes the detection more useful for
real-time security monitoring.
</p>

<hr>

<h2>16. Investigation Outcome</h2>

<div align="center">

<table>

<tr>
<th>Category</th>
<th>Result</th>
</tr>

<tr>
<td>Incident Type</td>
<td>Potential SSH Brute-Force Activity</td>
</tr>

<tr>
<td>Source IP</td>
<td><code>192.168.56.103</code></td>
</tr>

<tr>
<td>Target IP</td>
<td><code>192.168.56.102</code></td>
</tr>

<tr>
<td>Target Account</td>
<td><code>snowden</code></td>
</tr>

<tr>
<td>Failed Attempts</td>
<td>3</td>
</tr>

<tr>
<td>Successful Login After Failures</td>
<td>Not observed</td>
</tr>

<tr>
<td>Severity</td>
<td>Medium</td>
</tr>

<tr>
<td>Status</td>
<td>Investigated</td>
</tr>

</table>

</div>

<hr>

<h2>17. Skills Demonstrated</h2>

<ul>

<li>SSH authentication monitoring</li>

<li>Linux log analysis</li>

<li>Authentication event investigation</li>

<li>Source IP identification</li>

<li>User/account identification</li>

<li>Event correlation</li>

<li>Timeline reconstruction</li>

<li>Brute-force detection logic</li>

<li>IOC identification</li>

<li>SOC incident documentation</li>

<li>Incident severity assessment</li>

</ul>

<hr>

<h2>18. Evidence</h2>

<ul>

<li><code>/var/log/auth.log</code></li>

<li>Failed SSH authentication events</li>

<li>Authentication timestamps</li>

<li>Source IP information</li>

<li>Target username information</li>

<li>Successful authentication correlation</li>

</ul>

<hr>

<h2>19. Analyst Conclusion</h2>

<p>
The investigation successfully identified three failed SSH authentication
attempts originating from <code>192.168.56.103</code> and targeting the
<code>snowden</code> account on <code>192.168.56.102</code>.
</p>

<p>
The repeated failures from the same source against the same account met
the controlled threshold for potential brute-force activity.
</p>

<p>
An earlier successful authentication from the same source was identified,
but it occurred before the controlled failed-login sequence and therefore
was not considered evidence of successful brute-force compromise.
</p>

<p>
No successful authentication was observed immediately following the
controlled failed-login sequence.
</p>

<p>
The event was therefore classified as:
</p>

<div align="center">

<h2>⚠️ Potential SSH Brute-Force Activity</h2>

<p>
<strong>Severity: Medium</strong>
</p>

</div>

<hr>

<div align="center">

<h3>🛡️ SOC Investigation Workflow</h3>

<pre><code>
Authentication Activity
        ↓
Log Collection
        ↓
Event Filtering
        ↓
Source Identification
        ↓
Target Account Identification
        ↓
Failed Login Analysis
        ↓
Successful Login Correlation
        ↓
Detection Criteria
        ↓
IOC Extraction
        ↓
Incident Classification
        ↓
SOC Reporting
</code></pre>

<br>

<strong>Shaik Jaffer Sadeq</strong>

<br>

<small>
SOC Analyst Portfolio • Defensive Cybersecurity
</small>

</div>
