<h1 align="center">SOC Incident Timeline</h1>

<p align="center">
  <strong>Suspicious Web Reconnaissance Investigation</strong>
</p>

<hr>

<h2>Incident Summary</h2>

<p>
A simulated HTTP reconnaissance activity was observed against an internal
SOC laboratory web server. Network traffic was captured and analyzed to
identify the source, destination, activity, and security impact.
</p>

<hr>

<h2>Network Details</h2>

<table>
<tr>
<th>Field</th>
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
<td>Protocol</td>
<td>HTTP / TCP</td>
</tr>

<tr>
<td>Interface</td>
<td><code>eth1</code></td>
</tr>

</table>

<hr>

<h2>Timeline</h2>

<h3>1. TCP Connection Establishment</h3>

<p>
The client initiated a TCP connection to the web server on port
<code>8000</code>.
</p>

<pre>
SYN
↓
SYN/ACK
↓
ACK
</pre>

<p>
The three-way handshake successfully established the TCP connection.
</p>

<hr>

<h3>2. Normal HTTP Request</h3>

<p>
The client sent a request to the root directory of the web server.
</p>

<pre>
GET / HTTP/1.1
</pre>

<p>
The server responded successfully:
</p>

<pre>
HTTP/1.0 200 OK
</pre>

<p>
This confirmed that the HTTP service was accessible and responding
normally.
</p>

<hr>

<h3>3. Network Reconnaissance</h3>

<p>
Nmap SYN scanning activity was performed against the laboratory web server
to simulate network reconnaissance.
</p>

<p>
For the open HTTP port, the observed TCP behavior was:
</p>

<pre>
SYN → SYN/ACK → RST
</pre>

<p>
This behavior is consistent with a SYN scan where the scanner does not
complete a normal TCP connection.
</p>

<hr>

<h3>4. Suspicious HTTP Request</h3>

<p>
A suspicious HTTP request was generated against an administrative-looking
resource.
</p>

<pre>
GET /admin HTTP/1.1
User-Agent: sqlmap
</pre>

<p>
The requested URI was:
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
This was flagged as suspicious because SQLMap is commonly associated with
automated web application security testing and reconnaissance.
</p>

<hr>

<h3>5. Server Response</h3>

<p>
The web server returned:
</p>

<pre>
HTTP/1.0 404 File Not Found
</pre>

<p>
The requested administrative resource was therefore not available on the
test server.
</p>

<p>
No evidence of successful access to the <code>/admin</code> resource was
observed during the investigation.
</p>

<hr>

<h2>Detection</h2>

<p>
The suspicious activity was identified by inspecting the HTTP User-Agent
field in Wireshark.
</p>

<p>
The following detection condition was used:
</p>

<pre>
HTTP User-Agent contains "sqlmap"
</pre>

<p>
A Sigma-style detection rule was created and stored at:
</p>

<pre>
detections/suspicious-web-user-agent.yml
</pre>

<hr>

<h2>Indicators Identified</h2>

<ul>
<li><strong>Source IP:</strong> <code>192.168.56.103</code></li>
<li><strong>Destination IP:</strong> <code>192.168.56.102</code></li>
<li><strong>Destination Port:</strong> <code>8000</code></li>
<li><strong>User-Agent:</strong> <code>sqlmap</code></li>
<li><strong>Requested URI:</strong> <code>/admin</code></li>
<li><strong>Response:</strong> <code>404 File Not Found</code></li>
</ul>

<hr>

<h2>Assessment</h2>

<table>
<tr>
<th>Category</th>
<th>Assessment</th>
</tr>

<tr>
<td>Activity</td>
<td>Suspicious Web Reconnaissance</td>
</tr>

<tr>
<td>Detection</td>
<td>SQLMap User-Agent</td>
</tr>

<tr>
<td>Successful Exploitation</td>
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

<hr>

<h2>Recommended SOC Actions</h2>

<ol>
<li>Validate the source host.</li>

<li>Review web-server logs for additional requests.</li>

<li>Search for repeated scanning activity.</li>

<li>Identify additional suspicious User-Agent values.</li>

<li>Review authentication and application logs.</li>

<li>Investigate any evidence of successful exploitation.</li>

<li>Escalate the incident if compromise is confirmed.</li>
</ol>

<hr>

<h2>Evidence</h2>

<ul>
<li><code>soc-lab.pcapng</code></li>
<li>Wireshark packet analysis</li>
<li>HTTP request and response analysis</li>
<li>TCP stream analysis</li>
<li>IOC documentation</li>
<li>Detection rule</li>
<li>Incident notes</li>
</ul>

<hr>

<h2>Analyst Conclusion</h2>

<p>
The investigation identified simulated automated web reconnaissance
activity originating from <code>192.168.56.103</code> and targeting the
HTTP service at <code>192.168.56.102:8000</code>.
</p>

<p>
The suspicious <code>GET /admin</code> request contained the
<code>sqlmap</code> User-Agent and resulted in a
<code>404 File Not Found</code> response.
</p>

<p>
No successful access or exploitation was observed. The event was therefore
classified as <strong>Medium Severity Suspicious Web Reconnaissance</strong>.
</p>

<hr>

<p align="center">
<strong>SOC Network Investigation Lab</strong>
</p>
