# 🛡️ CloudQuarantine

> 🚀 Event-driven Kubernetes security control plane for automatic threat detection, response, and forensic analysis

---

## 🎯 Problem

Modern Kubernetes environments lack **automated runtime security response**.

* Threats are detected… but not contained ❌
* Security tools are reactive, not proactive ❌
* No clear forensic trace of incidents ❌

👉 Result: delayed response, lateral movement, and lack of visibility.

---

## 💡 Solution

**CloudQuarantine** is an **event-driven DevSecOps platform** that:

* Detects runtime threats using Falco
* Evaluates risk through a decision engine
* Automatically quarantines compromised workloads
* Enforces network isolation using Kubernetes policies
* Generates forensic timelines for incident analysis

---

## 🧠 Architecture

```
Falco (Runtime Detection)
        ↓
Falcosidekick (Event Routing)
        ↓
FastAPI Controller (Control Plane)
        ↓
Decision Engine (Risk Scoring)
        ↓
Response Engine (Playbooks)
        ↓
Kubernetes API
        ↓
NetworkPolicy Isolation
        ↓
Forensics (Incident Storage + Timeline)
```

---

## ⚡ Features

* 🔍 Runtime threat detection (Falco)
* 🧠 Risk-based decision engine
* ⚡ Automated response playbooks
* 🔐 Kubernetes-native quarantine (labels + NetworkPolicy)
* 📊 Incident forensics API
* 📜 Human-readable timeline generation
* 🔁 Event-driven architecture
* 🧪 Attack simulation support
* 🧰 CI/CD security validation (GitHub Actions)

---

## 🧪 Demo (End-to-End)

### 1. Trigger attack

```bash
kubectl exec -it test-shell -n demo-app -- sh
ls /
```

---

### 2. System reaction

* Falco detects shell execution
* Event sent via Falcosidekick
* Controller evaluates risk
* Pod is labeled `quarantined`
* NetworkPolicy applied automatically

---

### 3. Verify isolation

```bash
kubectl exec test-shell -n demo-app -- wget -O- http://<service-ip>
```

👉 ❌ Connection refused

---

### 4. Verify normal pod still works

```bash
kubectl exec network-check -n demo-app -- wget -O- http://<service-ip>
```

👉 ✅ Success

---

### 5. View incident timeline

```bash
curl http://localhost:8000/api/v1/incidents/timeline
```

Example:

```
[07:45:53] Event detected: Terminal shell in container
[07:45:53] Target: pod=test-shell namespace=demo-app
[07:45:53] Risk score: 100
[07:45:53] Action: pod_labeled_and_network_isolated
```

---

## 🔐 Security Capabilities

* Runtime syscall monitoring
* MITRE ATT&CK mapping (Falco rules)
* Automated containment (quarantine)
* Network-level isolation
* Incident evidence preservation
* Policy-driven response

---

## 📊 Metrics (Demo)

* Detection time: ~2–5 seconds
* Response time: ~3–10 seconds
* Isolation success rate: 100%

---

## 🧱 Tech Stack

* Kubernetes (k3d)
* Python (FastAPI)
* Falco + Falcosidekick
* Docker
* GitHub Actions (CI/CD)
* Kubernetes NetworkPolicy

---

## 🧠 Why not just use Falco?

* Falco = detection
* CloudQuarantine = detection + decision + response + forensics

👉 It transforms alerts into **automated security actions**

---

## 🌍 Use Cases

* SaaS platforms running Kubernetes
* Fintech / sensitive workloads
* Cloud-native startups
* Multi-tenant clusters
* DevSecOps security automation

---

## 🚀 Future Improvements

* Slack / Telegram alerting
* Persistent storage (database)
* Multi-cluster control plane
* Advanced policy engine (OPA / Kyverno)
* Incident replay mode

---

## 👨‍💻 Author

Built by **Iheb Mrabet**
DevSecOps Engineer (aspiring)

---

## ⭐ Final Note

This project demonstrates:

✔ Real-world DevSecOps architecture
✔ Security automation
✔ Kubernetes deep understanding
✔ Event-driven systems

👉 Designed to operate like a **mini security platform**, not a simple project.

