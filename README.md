🛡️ CloudQuarantine

🚀 Event-driven Kubernetes security control plane for automatic threat detection, decision-making, response, and forensic analysis

🎯 Problem

Modern Kubernetes environments lack automated runtime security response.

Threats are detected… but not contained ❌
Security tools are reactive, not proactive ❌
No behavior awareness (repeated attacks go unnoticed) ❌
No clear forensic trace of incidents ❌

👉 Result: delayed response, lateral movement, and lack of visibility.

💡 Solution

CloudQuarantine is an event-driven DevSecOps platform that:

Detects runtime threats using Falco
Evaluates risk through a scoring decision engine
Enhances detection with behavior analysis (AI layer)
Supports manual approval workflows
Automatically quarantines compromised workloads
Enforces network isolation using Kubernetes policies
Scales deployments to zero in critical scenarios
Generates forensic timelines for incident analysis
Sends real-time alerts via Telegram
🧠 Architecture
Falco (Runtime Detection)
        ↓
Falcosidekick (Event Routing)
        ↓
FastAPI Controller (Control Plane)
        ↓
Decision Engine (Risk Scoring)
        ↓
AI Behavior Layer (Repetition + Context)
        ↓
Response Engine (Playbooks)
        ↓
Kubernetes API
        ↓
NetworkPolicy + Deployment Control
        ↓
Forensics (Incidents + Timeline)
        ↓
Dashboard UI (React)
⚡ Features
🔍 Detection
Runtime syscall monitoring (Falco)
Detection of shell, exec, root activity
🧠 Decision Engine
Risk-based scoring system
Policy-driven thresholds
Context-aware evaluation (namespace, workload)
🤖 AI Behavior Layer
Detects repeated suspicious activity per pod
Tracks anomalies at namespace level
Detects activity after quarantine
Adjusts risk dynamically

👉 Example:

1 shell → medium risk
repeated shells → score increases
triggers automatic quarantine
🚨 Response Engine
Log event
Send alert (Telegram)
Manual review (approval workflow)
Automatic quarantine
🔒 Quarantine Capabilities
Label pod as quarantined
Apply deny-all NetworkPolicy
Scale deployment to zero (critical workloads)
📊 Dashboard
Real-time incident monitoring
Decision transparency (score, reasons)
AI behavior insights
Manual approval actions
📩 Alerting
Telegram integration (real-time notifications)
📜 Forensics
Incident storage
Timeline reconstruction
Human-readable event history
🧪 Demo (End-to-End)
1. Trigger attack
kubectl exec -it test-shell -n demo-app -- sh
2. System reaction
Falco detects shell execution
Event sent via Falcosidekick
Decision engine assigns score
AI detects behavior (if repeated)
System decides → manual review or quarantine
3. Behavior escalation

Repeat attack multiple times:

kubectl exec -it test-shell -n demo-app -- sh

👉 Score increases due to repeated behavior

4. Production scenario
kubectl exec -it test-shell -n prod -- sh

👉 Automatic quarantine triggered

5. Deployment containment
kubectl exec -it <nginx-pod> -n prod -- sh

👉 Deployment scaled to 0

6. Verify isolation
kubectl exec test-shell -n demo-app -- wget -O- http://<service-ip>

👉 ❌ Connection refused

7. Verify normal pod
kubectl exec network-check -n demo-app -- wget -O- http://<service-ip>

👉 ✅ Success

8. View timeline
curl http://localhost:8000/api/v1/incidents/timeline

Example:

[07:45:53] Event detected: Terminal shell in container
[07:45:53] Target: pod=test-shell namespace=demo-app
[07:45:53] Risk score: 100
[07:45:53] Action: quarantine executed
🔐 Security Capabilities
Runtime syscall monitoring
MITRE ATT&CK mapping (Falco rules)
Behavior-based anomaly detection
Automated containment
Network-level isolation
Deployment-level containment
Incident evidence preservation
Policy-driven response
📊 Metrics (Demo)
Detection time: ~2–5 seconds
Response time: ~3–10 seconds
Isolation success rate: 100%
🧱 Tech Stack
Kubernetes (k3d)
Python (FastAPI)
Falco + Falcosidekick
React (Dashboard)
PostgreSQL
Docker
Kubernetes NetworkPolicy
🧠 Why not just use Falco?

Falco = detection
CloudQuarantine = detection + decision + response + forensics

👉 It transforms alerts into automated security actions

🌍 Use Cases
SaaS platforms running Kubernetes
Fintech / sensitive workloads
Cloud-native startups
Multi-tenant clusters
DevSecOps automation pipelines
🚀 Future Improvements
Slack / advanced alerting
Multi-cluster control plane
Advanced policy engine (OPA / Kyverno)
Incident replay mode
ML-based anomaly detection
👨‍💻 Author

Built by Iheb Mrabet
DevSecOps Engineer (aspiring)

⭐ Final Note

This project demonstrates:

✔ Real-world DevSecOps architecture
✔ Runtime security automation
✔ Behavior-based detection
✔ Kubernetes deep understanding
✔ Event-driven systems

👉 Designed to operate like a mini security platform, not a simple project.
