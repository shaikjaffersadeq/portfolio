<h1 align="center">SOC Incident Investigation – Suspicious Web Reconnaissance</h1>

<p align="center">
  <strong>Security Operations Center (SOC) Investigation Project</strong>
</p>

<hr>

<h2>📌 Project Overview</h2>

<p>
This project demonstrates a practical SOC investigation of suspicious automated
web reconnaissance activity detected against a laboratory web server.
</p>

<p>
The investigation was performed in an isolated cybersecurity laboratory
environment using network packet capture analysis, Wireshark, HTTP traffic
inspection, TCP analysis, IOC identification, and a custom detection rule.
</p>

<h2>🚨 Incident Summary</h2>

<table>
  <tr>
    <td><strong>Incident Type</strong></td>
    <td>Suspicious Web Reconnaissance</td>
  </tr>
  <tr>
    <td><strong>Severity</strong></td>
    <td>Medium</td>
  </tr>
  <tr>
    <td><strong>Source IP</strong></td>
    <td>192.168.56.103</td>
  </tr>
  <tr>
    <td><strong>Destination IP</strong></td>
    <td>192.168.56.102</td>
  </tr>
  <tr>
    <td><strong>Destination Port</strong></td>
    <td>8000</td>
  </tr>
  <tr>
    <td><strong>Protocol</strong></td>
    <td>HTTP / TCP</td>
  </tr>
  <tr>
    <td><strong>Detection Indicator</strong></td>
    <td>SQLMap User-Agent</td>
  </tr>
  <tr>
    <td><strong>Administrative Access</strong></td>
    <td>Not Successful</td>
  </tr>
  <tr>
    <td><strong>Final Classification</strong></td>
    <td>SUSPICIOUS WEB RECONNAISSANCE</td>
  </tr>
</table>

<h2>🔍 Investigation Findings</h2>

<p>
Network traffic from <strong>192.168.56.103</strong> was observed communicating
with the laboratory web server at <strong>192.168.56.102:8000</strong>.
</p>

<p>
The HTTP traffic contained a suspicious automated scanning indicator:
</p>

<pre>
User-Agent: sqlmap
</pre>

<p>
The source system also requested the following administrative-looking endpoint:
</p>

<pre>
GET /admin HTTP/1.1
Host: 192.168.56.102:8000
User-Agent: sqlmap
</pre>

<p>
The server responded with:
</p>

<pre>
HTTP/1.0 404 File not found
</pre>

<p>
This indicates that the requested <code>/admin</code> resource was not available.
No evidence of successful administrative access was identified during the
investigation.
</p>

<h2>🧪 Investigation Process</h2>

<ol>
  <li>
    <strong>Packet Capture Analysis</strong><br>
    Reviewed the supplied PCAP file using Wireshark.
  </li>

  <li>
    <strong>TCP Analysis</strong><br>
    Examined TCP connection establishment, SYN packets, acknowledgements,
    and connection termination/reset behaviour.
  </li>

  <li>
    <strong>HTTP Analysis</strong><br>
    Inspected HTTP requests and server responses to identify suspicious web
    activity.
  </li>

  <li>
    <strong>User-Agent Analysis</strong><br>
    Identified the <code>sqlmap</code> User-Agent as a strong indicator of
    automated web security testing/reconnaissance activity.
  </li>

  <li>
    <strong>Endpoint Analysis</strong><br>
    Investigated the <code>/admin</code> request and confirmed the server
    returned HTTP 404.
  </li>

  <li>
    <strong>IOC Identification</strong><br>
    Documented relevant IP addresses, ports, HTTP indicators, and other
    investigation artifacts.
  </li>

  <li>
    <strong>Detection Rule Creation</strong><br>
    Created a detection rule to identify HTTP requests containing the
    SQLMap User-Agent.
  </li>

  <li>
    <strong>Incident Documentation</strong><br>
    Created an incident timeline, investigation notes, and a final SOC
    investigation report.
  </li>
</ol>

<h2>🛡️ Detection Logic</h2>

<p>
The investigation includes a custom detection rule designed to identify
HTTP traffic containing the SQLMap User-Agent.
</p>

<pre>
title: Suspicious SQLMap User-Agent
id: soc-lab-sqlmap-001
status: experimental

description:
  Detects HTTP requests containing a SQLMap User-Agent.

logsource:
  category: webserver

detection:
  selection:
    http_user_agent|contains: 'sqlmap'
  condition: selection

level: medium
</pre>

<h2>📊 Key Evidence</h2>

<ul>
  <li>Network packet capture (<code>soc-lab.pcapng</code>)</li>
  <li>Wireshark packet analysis</li>
  <li>TCP connection analysis</li>
  <li>HTTP request/response analysis</li>
  <li>SQLMap User-Agent indicator</li>
  <li>GET request to <code>/admin</code></li>
  <li>HTTP 404 server response</li>
  <li>Incident timeline</li>
  <li>Investigation notes</li>
  <li>Custom detection rule</li>
</ul>

<h2>📁 Project Structure</h2>

<pre>
SOC-Lab/
│
├── soc-lab.pcapng
│
├── SOC-Investigation-Report.md
│
├── incident-timeline.md
│
├── README.md
│
├── iocs/
│   └── iocs.txt
│
├── evidence/
│   └── incident-notes.txt
│
└── detections/
    └── suspicious-web-user-agent.yml
</pre>

<h2>🧰 Tools Used</h2>

<ul>
  <li><strong>Wireshark</strong> – Network traffic and packet analysis</li>
  <li><strong>Linux / Kali Linux</strong> – Investigation environment</li>
  <li><strong>curl</strong> – HTTP request testing</li>
  <li><strong>TCP/IP</strong> – Network communication analysis</li>
  <li><strong>HTTP</strong> – Web traffic analysis</li>
  <li><strong>YAML</strong> – Detection rule creation</li>
  <li><strong>GitHub</strong> – Project documentation and portfolio</li>
</ul>

<h2>🎯 Skills Demonstrated</h2>

<ul>
  <li>Network reconnaissance analysis</li>
  <li>Packet capture analysis</li>
  <li>TCP analysis</li>
  <li>HTTP analysis</li>
  <li>Threat detection</li>
  <li>IOC identification</li>
  <li>Security alert creation</li>
  <li>Detection rule development</li>
  <li>Incident documentation</li>
  <li>SOC investigation methodology</li>
  <li>Evidence-based security analysis</li>
</ul>

<h2>📋 Analyst Conclusion</h2>

<p>
The investigation identified suspicious automated web reconnaissance
originating from <strong>192.168.56.103</strong> against the laboratory web
server at <strong>192.168.56.102:8000</strong>.
</p>

<p>
The <strong>SQLMap User-Agent</strong> provided a useful detection indicator
for identifying the automated nature of the HTTP activity.
</p>

<p>
The <code>/admin</code> request resulted in an
<strong>HTTP 404</strong> response. Therefore, the investigation found
<strong>no evidence of successful administrative access</strong>.
</p>

<h2>⚠️ Final Classification</h2>

<table>
  <tr>
    <td><strong>Classification</strong></td>
    <td>SUSPICIOUS WEB RECONNAISSANCE</td>
  </tr>
  <tr>
    <td><strong>Severity</strong></td>
    <td>MEDIUM</td>
  </tr>
  <tr>
    <td><strong>Status</strong></td>
    <td>INVESTIGATED</td>
  </tr>
</table>

<h2>🎓 Learning Outcome</h2>

<p>
This project demonstrates how a SOC analyst can move from raw network traffic
to a documented security finding by correlating TCP behaviour, HTTP requests,
User-Agent indicators, server responses, and detection logic.
</p>

<p>
The project also demonstrates the importance of distinguishing between
<strong>suspicious activity</strong> and <strong>confirmed compromise</strong>.
In this investigation, reconnaissance activity was identified, but successful
administrative access was not observed.
</p>

<h2>⚖️ Disclaimer</h2>

<p>
This project was performed in an isolated laboratory environment for
educational and defensive cybersecurity purposes only. All systems,
addresses, traffic, and testing activities were part of a controlled
laboratory environment.
</p>

<hr>

<p align="center">
  <strong>SOC Incident Investigation Project</strong><br>
  Cybersecurity Portfolio
</p>
