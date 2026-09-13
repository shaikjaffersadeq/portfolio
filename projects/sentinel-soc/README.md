SENTINEL SOC
Security Operations Center & Incident Response Platform
Project 03
About the Project
SENTINEL SOC is a web-based Security Operations Center and Incident Response application that I built to practice security monitoring, alert investigation and incident handling.
The application brings authentication monitoring, attack simulation, defensive controls, security alerts, a SOC dashboard and incident response into one platform.
The main goal was to create a simple SOC-style workflow where security activity can be generated, detected, investigated and documented.
---
Technologies Used
Python
Flask
SQLite
HTML
CSS
JavaScript
REST APIs
---
Application Modules
1. Password Analyzer
A password analysis module that checks password characteristics and provides feedback about password strength.
2. Authentication Lab
The Authentication Lab is used to generate and monitor login activity.
It records authentication events such as:
Successful login attempts
Failed login attempts
Repeated authentication failures
These events can then be used for detection and investigation.
3. Attack Simulator
A controlled module for generating simulated security activity.
It is used to create test activity so that the detection and defensive parts of the application can be observed.
4. Defense Center
The Defense Center contains defensive controls for handling suspicious authentication activity.
The application includes:
Rate limiting
Account protection
Brute-force protection
These controls demonstrate how repeated suspicious login activity can be handled.
5. SOC Dashboard
The SOC Dashboard provides a central view of security activity in the application.
It displays information including:
Total security events
Failed login attempts
Security alerts
Open incidents
Recent activity
This provides an analyst-style overview of the current security state.
6. Incident Response Center
The Incident Response Center is the main investigation section of the application.
Security alerts can be converted into incidents and investigated through the incident management interface.
The incident lifecycle is:
```text
OPEN
  ↓
INVESTIGATING
  ↓
RESOLVED
  ↓
CLOSED
```
The application allows the analyst to:
View incident details
Investigate incidents
Add analyst notes
Record response actions
View the incident timeline
Add a resolution summary
Add a closure reason
Review resolved and closed incidents
---
Security Alert Detection
One of the detection scenarios implemented in the application is repeated failed authentication activity.
When the activity matches the detection condition, the application can generate a security alert such as:
```text
BRUTE_FORCE_PATTERN
```
The alert can then be reviewed and converted into an incident for further investigation.
---
Incident Investigation Workflow
The workflow used in the application is:
```text
Security Event
      ↓
Detection
      ↓
Security Alert
      ↓
Incident Creation
      ↓
Investigation
      ↓
Response
      ↓
Resolution
      ↓
Closure
```
This helped me practice how a security alert can be handled through an incident-response process rather than simply being recorded as a log.
---
Incident Timeline
Each incident keeps a record of important investigation actions.
For example:
```text
Incident Created
       ↓
Investigation Started
       ↓
Analyst Note Added
       ↓
Response Action Recorded
       ↓
Incident Resolved
       ↓
Incident Closed
```
This provides an audit history of the investigation.
---
Database
SQLite is used to store the application's security and incident data.
The database contains information related to:
Authentication events
Security events
Security alerts
Incidents
Analyst notes
Response actions
Incident timelines
Resolution information
Closure information
---
API
The Flask backend provides API endpoints used by the frontend.
Examples include:
```text
/api/health
/api/incidents
/api/incidents/<incident_id>
/api/incidents/closed
/api/incidents/resolved
```
The application also provides an endpoint for retrieving an incident's timeline.
---
What I Worked On
While building SENTINEL SOC, I worked on:
Flask backend development
SQLite database design
REST API development
Frontend development
Authentication event handling
Brute-force detection logic
Rate limiting
Security alert generation
Incident management
Investigation notes
Response actions
Incident status management
Resolution and closure tracking
Timeline and audit history
---
What I Learned
This project helped me understand how different parts of a SOC workflow connect together.
Instead of only looking at individual security events, I practiced moving from an event to an alert, then to an incident, investigation, response, resolution and closure.
I also gained practical experience connecting a Flask backend, database, APIs and frontend into one security-focused application.
---
Future Improvements
Possible future improvements include:
More detection rules
Threat intelligence integration
IOC enrichment
MITRE ATT&CK mapping
Role-based analyst accounts
Email notifications
Automated incident creation
Automated incident reports
More advanced SOC dashboards
---
Project Status
Completed
---
Author
Shaik Jaffer Sadeq
Cybersecurity-focused BCA student interested in Security Operations, threat detection, incident response, network security and blue-team security.
