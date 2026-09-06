<div align="center">

<h1>🛡️ SOC Brute-Force Login Detection & Investigation</h1>

<h3>Security Operations Center (SOC) Investigation Project</h3>

<p>
A hands-on cybersecurity lab focused on detecting, investigating,
and documenting repeated failed SSH authentication attempts.
</p>

</div>

<hr>

<h2>📌 Project Overview</h2>

<p>
This project simulates a potential SSH brute-force authentication attack
inside an isolated cybersecurity lab environment.
</p>

<p>
The investigation was performed using:
</p>

<ul>
<li>Kali Linux</li>
<li>Ubuntu Linux</li>
<li>OpenSSH</li>
<li>Linux authentication logs</li>
<li>Linux command-line tools</li>
</ul>

<p>
The objective was to generate controlled failed SSH authentication attempts,
collect authentication evidence, identify the source IP, determine the
targeted account, analyze the attack timeline, and develop detection logic.
</p>

<hr>

<h2>🎯 Project Objective</h2>

<p>The main objective of this project is to demonstrate how a SOC Analyst can:</p>

<ol>
<li>Monitor authentication activity.</li>
<li>Identify repeated failed SSH logins.</li>
<li>Determine the source IP address.</li>
<li>Identify the targeted user account.</li>
<li>Analyze authentication timestamps.</li>
<li>Determine whether a successful login followed the failures.</li>
<li>Identify potential brute-force behavior.</li>
<li>Create detection logic.</li>
<li>Document the incident professionally.</li>
</ol>

<hr>

<h2>🧪 Lab Environment</h2>

<table>
<thead>
<tr>
<th>Component</th>
<th>Details</th>
</tr>
</thead>

<tbody>

<tr>
<td>Attacker / Test Machine</td>
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
<td>Network</td>
<td>Isolated Host-Only Lab</td>
</tr>

</tbody>
</table>

<p>
<strong>Environment:</strong> All activity was performed inside a controlled
lab environment using systems configured for cybersecurity practice.
</p>

<hr>

<h2>🔬 Investigation Scenario</h2>

<p>
A series of failed SSH authentication attempts was simulated from the
Kali Linux machine against the Ubuntu SSH server.
</p>

<p>
The purpose was to reproduce the type of authentication pattern that a
SOC Analyst might investigate when an account is repeatedly targeted.
</p>

<p>
The authentication events were recorded by the Ubuntu system in:
</p>

<pre><code>/var/log/auth.log</code></pre>

<hr>

<h2>🔎 Investigation Process</h2>

<h3>1️⃣ SSH Service Preparation</h3>

<p>
The Ubuntu machine was configured as the SSH target.
The SSH service was verified to be running.
</p>

<p>
Kali Linux was then used to connect to the Ubuntu host over the isolated
Host-Only network.
</p>

<hr>

<h3>2️⃣ Controlled Failed Authentication</h3>

<p>
Multiple SSH login attempts were intentionally made using an incorrect
password.
</p>

<p>The attempts originated from:</p>

<pre><code>192.168.56.103</code></pre>

<p>and targeted:</p>

<pre><code>snowden</code></pre>

<p>on:</p>

<pre><code>192.168.56.102</code></pre>

<p>
The failed authentication activity generated corresponding events in
the Ubuntu authentication logs.
</p>

<hr>

<h3>3️⃣ Authentication Log Analysis</h3>

<p>
The Ubuntu authentication log was searched for failed password events.
</p>

<p>The relevant log pattern was:</p>

<pre><code>Failed password for snowden from 192.168.56.103</code></pre>

<p>
Three matching failed authentication events were identified for the
controlled test sequence.
</p>

<hr>

<h2>📊 Observed Evidence</h2>

<table>
<thead>
<tr>
<th>Indicator</th>
<th>Finding</th>
</tr>
</thead>

<tbody>

<tr>
<td>Source IP</td>
<td><code>192.168.56.103</code></td>
</tr>

<tr>
<td>Destination IP</td>
<td><code>192.168.56.102</code></td>
</tr>

<tr>
<td>Username</td>
<td><code>snowden</code></td>
</tr>

<tr>
<td>Service</td>
<td>SSH</td>
</tr>

<tr>
<td>Failed Attempts</td>
<td><strong>3</strong></td>
</tr>

<tr>
<td>Authentication Result</td>
<td>Failed</td>
</tr>

<tr>
<td>Detection Category</td>
<td>Potential Brute-Force Activity</td>
</tr>

<tr>
<td>Severity</td>
<td><strong>Medium</strong></td>
</tr>

</tbody>
</table>

<hr>

<h2>🕒 Incident Timeline</h2>

<p>
The controlled failed authentication sequence occurred within a short
time period.
</p>

<p>
The events showed repeated authentication failures against the same
account from the same source IP.
</p>

<p>
This repeated pattern is more suspicious than an isolated failed login.
</p>

<table>
<thead>
<tr>
<th>Event</th>
<th>Source</th>
<th>Target</th>
<th>Result</th>
</tr>
</thead>

<tbody>

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

</tbody>
</table>

<hr>

<h2>🔐 Successful Authentication Analysis</h2>

<p>
A successful SSH authentication from:
</p>

<pre><code>192.168.56.103</code></pre>

<p>
was also present in the authentication logs.
</p>

<p>
However, that successful authentication occurred <strong>before</strong>
the controlled failed-login sequence.
</p>

<p>
Therefore, it was not interpreted as a successful brute-force compromise.
</p>

<p>
No successful authentication was observed immediately following the
controlled failed-login sequence.
</p>

<div align="center">

<h3>Investigation Conclusion</h3>

<p>
<strong>
Failed authentication activity was observed, but no subsequent successful
authentication was identified during the controlled test sequence.
</strong>
</p>

</div>

<hr>

<h2>🚨 Detection Logic</h2>

<p>
The investigation uses the following detection concept:
</p>

<div align="center">

<table>
<tr>
<td>

<strong>IF</strong><br>
3 or more failed SSH authentication attempts<br>
<br>

<strong>FROM</strong><br>
the same source IP<br>
<br>

<strong>AGAINST</strong><br>
the same username<br>
<br>

<strong>WITHIN</strong><br>
a short time window<br>
<br>

<strong>THEN</strong><br>
generate a potential SSH brute-force alert.

</td>
</tr>
</table>

</div>

<h3>Example Detection</h3>

<pre><code>Source IP       : 192.168.56.103
Target Username : snowden
Failed Attempts : 3
Threshold       : 3

ALERT: Potential SSH Brute-Force Activity
Severity: Medium</code></pre>

<hr>

<h2>🧠 SOC Analyst Reasoning</h2>

<p>
A single failed SSH login does not necessarily indicate malicious activity.
Users can make typing mistakes or enter an incorrect password.
</p>

<p>
However, repeated failures from the same source against the same account
can indicate:
</p>

<ul>
<li>Password guessing</li>
<li>Brute-force authentication</li>
<li>Automated authentication attempts</li>
<li>Unauthorized access attempts</li>
</ul>

<p>
A SOC Analyst should correlate authentication failures with successful
login events and other available telemetry before declaring an account
compromise.
</p>

<hr>

<h2>📈 Investigation Outcome</h2>

<p>
The investigation identified:
</p>

<blockquote>
<strong>
Three failed SSH authentication attempts from
<code>192.168.56.103</code> targeting the
<code>snowden</code> account on
<code>192.168.56.102</code>.
</strong>
</blockquote>

<p>
The pattern met the controlled detection threshold for potential
brute-force activity.
</p>

<p>
No successful authentication was observed immediately after the
failed-login sequence.
</p>

<p>Therefore, the incident is classified as:</p>

<div align="center">

<h3>⚠️ Potential SSH Brute-Force Activity</h3>

<p><strong>Severity: Medium</strong></p>

</div>

<hr>

<h2>🛠️ Skills Demonstrated</h2>

<h3>Security Operations</h3>

<ul>
<li>Authentication monitoring</li>
<li>Log analysis</li>
<li>Incident investigation</li>
<li>IOC identification</li>
<li>Timeline reconstruction</li>
<li>Detection engineering</li>
<li>Incident documentation</li>
</ul>

<h3>Linux</h3>

<ul>
<li>SSH</li>
<li><code>/var/log/auth.log</code></li>
<li><code>grep</code></li>
<li><code>tail</code></li>
<li>Linux service management</li>
<li>Command-line investigation</li>
</ul>

<h3>SOC Analysis</h3>

<ul>
<li>Source identification</li>
<li>User/account identification</li>
<li>Event correlation</li>
<li>Failed vs successful authentication analysis</li>
<li>Detection threshold creation</li>
<li>Incident documentation</li>
</ul>

<hr>

<h2>📂 Project Structure</h2>

<pre><code>soc-brute-force-investigation/
│
├── README.md
├── SOC-Investigation-Report.md
├── incident-timeline.md
│
├── detections/
│   └── brute-force-login.yml
│
├── evidence/
│   └── incident-notes.txt
│
└── iocs/
    └── iocs.txt</code></pre>

<hr>

<h2>📋 Evidence Collected</h2>

<ul>
<li>Ubuntu SSH authentication logs</li>
<li>Failed authentication events</li>
<li>Source IP information</li>
<li>Target username</li>
<li>Authentication timestamps</li>
<li>Successful authentication correlation</li>
<li>Detection criteria</li>
</ul>

<hr>

<h2>🎓 What This Project Demonstrates</h2>

<p>
This project demonstrates the complete basic workflow of a SOC
authentication investigation:
</p>

<div align="center">

<pre><code>Generate Controlled Activity
          ↓
Collect Authentication Logs
          ↓
Search & Filter Events
          ↓
Identify Source IP
          ↓
Identify Target Account
          ↓
Analyze Failed Attempts
          ↓
Check Successful Authentication
          ↓
Build Detection Logic
          ↓
Classify the Incident
          ↓
Document the Investigation</code></pre>

</div>

<hr>

<h2>⚠️ Lab Disclaimer</h2>

<p>
This project was performed entirely within an isolated cybersecurity
lab using systems controlled by the analyst.
</p>

<p>
No unauthorized systems, networks, or accounts were targeted.
</p>

<hr>

<div align="center">

<h2>👨‍💻 Analyst</h2>

<h3>Shaik Jaffer Sadeq</h3>

<p><strong>Aspiring SOC Analyst</strong></p>

<p>
Security Monitoring • Threat Detection • Incident Response •
Network Security • Defensive Cybersecurity
</p>

</div>
