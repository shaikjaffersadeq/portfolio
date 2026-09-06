<h1 align="center">SOC Incident Investigation Report</h1>

<p align="center">
  <strong>Suspicious Web Reconnaissance Detection & Investigation</strong>
</p>

<hr>

<h2>1. Executive Summary</h2>

<p>
This investigation was conducted in a controlled SOC laboratory environment
to identify and analyze suspicious web reconnaissance activity against an
internal HTTP server.
</p>

<p>
During the investigation, network traffic between a Kali Linux analyst
machine and an Ubuntu web server was captured and analyzed using Wireshark
and tcpdump.
</p>

<p>
A suspicious HTTP request targeting <code>/admin</code> was identified.
The request contained the User-Agent:
</p>

<p align="center">
  <strong><code>sqlmap</code></strong>
</p>

<p>
The server responded with <code>HTTP 404 File Not Found</code>, indicating
that the requested resource was not available.
</p>

<p>
The activity was classified as <strong>Suspicious Web Reconnaissance</strong>
with a <strong>Medium</strong> severity rating.
</p>

<hr>

<h2>2. Investigation Environment</h2>

<table>
<tr>
<th>Component</th>
<th>Details</th>
</tr>

<tr>
<td>Analyst Machine</td>
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
<td>Destination Port</td>
<td><code>8000</code></td>
</tr>

<tr>
<td>Protocol</td>
<td>HTTP over TCP</td>
</tr>

<tr>
<td>Network Interface</td>
<td><code>eth1</code></td>
</tr>

<tr>
<td>Web Server</td>
<td>Python SimpleHTTPServer</td>
</tr>

</table>

<hr>

<h2>3. Tools Used</h2>

<ul>
<li><strong>Wireshark</strong> — Network packet analysis</li>
<li><strong>tcpdump</strong> — Network traffic capture</li>
<li><strong>Nmap</strong> — Network and service discovery</li>
<li><strong>curl</strong> — HTTP request generation</li>
<li><strong>Kali Linux</strong> — SOC investigation environment</li>
<li><strong>Ubuntu Linux</strong> — Target web server</li>
</ul>

<hr>

<h2>4. Investigation Scenario</h2>

<p>
A simulated internal web reconnaissance event was generated within an
isolated laboratory network.
</p>

<p>
The objective was to determine whether suspicious HTTP activity could be
identified from captured network traffic and converted into a SOC-style
security investigation.
</p>

<p>The investigation focused on:</p>

<ul>
<li>Identifying the source and destination systems</li>
<li>Analyzing TCP connection behavior</li>
<li>Inspecting HTTP requests and responses</li>
<li>Identifying suspicious User-Agent values</li>
<li>Determining whether unauthorized access was successful</li>
<li>Creating a detection rule</li>
<li>Documenting the incident and indicators</li>
</ul>

<hr>

<h2>5. Network Discovery</h2>

<p>
Nmap was used from the Kali Linux machine to identify services exposed by
the Ubuntu target.
</p>

<p>
The investigation identified TCP port <code>8000</code> as an open HTTP
service.
</p>

<p>
Service detection identified the application as:
</p>

<p align="center">
<strong>SimpleHTTPServer 0.6 (Python)</strong>
</p>

<hr>

<h2>6. TCP Traffic Analysis</h2>

<p>
The captured traffic was analyzed in Wireshark to understand the TCP
connection behavior.
</p>

<h3>Normal TCP Connection</h3>

<p>
A normal TCP connection to the web server followed the standard three-way
handshake:
</p>

<ol>
<li>SYN</li>
<li>SYN/ACK</li>
<li>ACK</li>
</ol>

<p>
This established a valid TCP connection between the client and the web
server.
</p>

<h3>Nmap SYN Scan</h3>

<p>
During the simulated reconnaissance activity, SYN scanning behavior was
observed.
</p>

<p>
For an open port, the sequence was:
</p>

<pre>
SYN → SYN/ACK → RST
</pre>

<p>
The RST packet indicated that the scanning host did not complete a normal
TCP connection.
</p>

<p>
A closed port responded with:
</p>

<pre>
SYN → RST/ACK
</pre>

<p>
This behavior is consistent with TCP port discovery.
</p>

<hr>

<h2>7. HTTP Traffic Analysis</h2>

<p>
The HTTP traffic was inspected using Wireshark.
</p>

<p>
A normal request to the web server was observed:
</p>

<pre>
GET / HTTP/1.1
</pre>

<p>
The server responded:
</p>

<pre>
HTTP/1.0 200 OK
</pre>

<p>
This confirmed that the web server was reachable and responding to HTTP
requests.
</p>

<hr>

<h2>8. Suspicious Activity Identified</h2>

<p>
During the investigation, a suspicious HTTP request was identified.
</p>

<h3>Observed Request</h3>

<pre>
GET /admin HTTP/1.1
User-Agent: sqlmap
</pre>

<p>
The request attempted to access the following resource:
</p>

<p align="center">
<strong><code>/admin</code></strong>
</p>

<p>
The HTTP User-Agent contained:
</p>

<p align="center">
<strong><code>sqlmap</code></strong>
</p>

<p>
This value was considered suspicious because SQLMap is commonly associated
with automated SQL injection testing and web application reconnaissance.
</p>

<hr>

<h2>9. Server Response</h2>

<p>
The server returned:
</p>

<pre>
HTTP/1.0 404 File Not Found
</pre>

<p>
This indicates that the requested <code>/admin</code> resource was not
available on the test web server.
</p>

<p>
No evidence was observed during this investigation indicating successful
access to the requested administrative resource.
</p>

<hr>

<h2>10. Detection Logic</h2>

<p>
A detection rule was created to identify HTTP requests containing a
SQLMap User-Agent.
</p>

<p>
The detection logic searches HTTP User-Agent fields for the string:
</p>

<pre>
sqlmap
</pre>

<p>
The corresponding Sigma-style detection rule is stored in:
</p>

<pre>
detections/suspicious-web-user-agent.yml
</pre>

<hr>

<h2>11. Indicators of Compromise</h2>

<table>
<tr>
<th>Indicator</th>
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
<td>Destination Port</td>
<td><code>8000</code></td>
</tr>

<tr>
<td>User-Agent</td>
<td><code>sqlmap</code></td>
</tr>

<tr>
<td>Requested URI</td>
<td><code>/admin</code></td>
</tr>

<tr>
<td>HTTP Response</td>
<td><code>404 File Not Found</code></td>
</tr>

<tr>
<td>Classification</td>
<td>Suspicious Web Reconnaissance</td>
</tr>

<tr>
<td>Severity</td>
<td>Medium</td>
</tr>

</table>

<hr>

<h2>12. Evidence Collected</h2>

<ul>
<li><code>soc-lab.pcapng</code> — Network packet capture</li>
<li>Wireshark HTTP analysis</li>
<li>Wireshark TCP stream analysis</li>
<li>Suspicious HTTP User-Agent observation</li>
<li>Incident timeline</li>
<li>IOC documentation</li>
<li>Detection rule</li>
<li>Incident notes</li>
</ul>

<hr>

<h2>13. Impact Assessment</h2>

<p>
The observed activity represents reconnaissance against the simulated web
server.
</p>

<p>
The investigation did not identify successful exploitation or successful
access to the <code>/admin</code> resource.
</p>

<p>
However, the presence of an automated security-testing User-Agent indicates
that additional investigation would be appropriate in a real SOC
environment.
</p>

<hr>

<h2>14. Recommended SOC Actions</h2>

<ol>
<li>Validate the source host responsible for the activity.</li>

<li>Review web-server logs for additional requests from the source IP.</li>

<li>Search for repeated requests targeting administrative or sensitive
resources.</li>

<li>Look for additional automated scanning User-Agents.</li>

<li>Review authentication logs for related suspicious activity.</li>

<li>Investigate any evidence of successful exploitation.</li>

<li>Escalate the incident if successful compromise or credential access is
identified.</li>
</ol>

<hr>

<h2>15. Analyst Assessment</h2>

<table>
<tr>
<th>Category</th>
<th>Assessment</th>
</tr>

<tr>
<td>Incident Type</td>
<td>Web Reconnaissance</td>
</tr>

<tr>
<td>Detection</td>
<td>Suspicious HTTP User-Agent</td>
</tr>

<tr>
<td>Suspicious Indicator</td>
<td><code>sqlmap</code></td>
</tr>

<tr>
<td>Target</td>
<td><code>/admin</code></td>
</tr>

<tr>
<td>Successful Access</td>
<td>No evidence observed</td>
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

<hr>

<h2>16. Conclusion</h2>

<p>
The investigation successfully identified simulated suspicious web
reconnaissance activity within the SOC laboratory environment.
</p>

<p>
Network traffic analysis revealed TCP scanning behavior followed by HTTP
requests against the test web server. A request targeting
<code>/admin</code> contained the suspicious User-Agent
<code>sqlmap</code>.
</p>

<p>
The server returned a <code>404 File Not Found</code> response, and no
successful access to the administrative resource was observed.
</p>

<p>
The activity was documented as a medium-severity reconnaissance event and
a detection rule was created to identify similar HTTP User-Agent activity.
</p>

<p>
This project demonstrates a complete SOC investigation workflow:
</p>

<p align="center">
<strong>
Traffic Capture → Detection → Investigation → IOC Extraction → Assessment → Reporting
</strong>
</p>

<hr>

<h2>17. Skills Demonstrated</h2>

<ul>
<li>Network traffic analysis</li>
<li>Packet analysis with Wireshark</li>
<li>Network capture with tcpdump</li>
<li>Network scanning analysis</li>
<li>HTTP protocol analysis</li>
<li>TCP/IP analysis</li>
<li>IOC identification</li>
<li>Security event investigation</li>
<li>Detection engineering</li>
<li>Sigma-style rule creation</li>
<li>Incident documentation</li>
<li>SOC analyst reporting</li>
</ul>

<hr>

<p align="center">
<strong>SOC Network Investigation Lab</strong><br>
Simulated environment for cybersecurity learning and portfolio development.
</p>
