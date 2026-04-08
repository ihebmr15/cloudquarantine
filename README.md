# 🛡️ CloudQuarantine

*Event‑driven Kubernetes security control plane for automatic threat detection, response, and forensic analysis*

CloudQuarantine combines **Falco**, a risk‑aware **Decision Engine**, and Kubernetes‑native response playbooks to automatically detect, assess and respond to runtime attacks in your clusters.  It doesn’t just raise alerts—it **quarantines compromised pods**, applies **network policies** to isolate them, records detailed **forensic timelines**, and surfaces **AI‑derived insights** to guide manual review when needed.

---

## 🎯 Problem

Modern Kubernetes environments typically rely on runtime detectors (e.g. Falco) that generate logs or alerts when suspicious behaviour occurs.  However:

* **Threats are detected… but not contained** — malicious processes continue to run until a human intervenes.
* **Alerts are overwhelming** — security teams struggle to prioritise which events matter most.
* **No clear forensic record** — responding to incidents is harder without a timeline of actions.

These gaps lead to delayed response, lateral movement, and limited visibility into what happened.

---

## 💡 Solution

CloudQuarantine orchestrates detection, risk scoring and response in a single workflow:

1. **Falco** monitors syscalls and emits detailed events.
2. **Falcosidekick** forwards those events to the CloudQuarantine controller.
3. The **Decision Engine** evaluates severity using policy thresholds, workload context and AI‑driven insights (e.g. repeated pod activity, namespace anomaly).
4. According to the policy it chooses one of three modes:

   * **Automatic quarantine** — label pod and enforce a “deny‑all” `NetworkPolicy`.
   * **Manual review** — alert only; operator approves before quarantining.
   * **Dismiss** — log and move on.
5. **Forensics** — all events, decisions and responses are stored; a timeline API visualises them.
6. A **Dashboard** surfaces incidents, highlights risk scores, AI explanations and approval status, and provides “Approve / Reject” actions for manual review.

This tight feedback loop turns runtime alerts into automated actions with an audit trail.

---

## 🧠 Architecture

```text
Falco (Runtime Detection)
        ↓
Falcosidekick (Event Routing)
        ↓
FastAPI Controller (Control Plane)
        ↓
Decision Engine (Risk Scoring & AI insights)
        ↓
Response Engine (Playbooks)
        ↓
Kubernetes API
        ↓
NetworkPolicy Isolation
        ↓
Forensics Store + Timeline API
        ↓
Dashboard UI & Notifications
```

* **Falco**: Detects syscall anomalies and known TTPs (mapped to MITRE ATT&CK).
* **Decision Engine**: Scores events based on configurable thresholds, workload profile (privileged containers, hostPath usage, secrets mounts, etc.), policy rules, and AI‑derived context (e.g. repeated behaviour after quarantine).
* **Response Engine**: Executes playbooks: label pod, apply `NetworkPolicy`, scale deployment to zero (advanced quarantine), or simply log/alert for manual review.
* **Forensics**: Stores incidents in a database (PostgreSQL); provides timeline API for analysis.
* **Dashboard**: Single‑page React application to review incidents, approve or reject actions, and see AI insights.
* **Notifications**: Integrates with Telegram (and easily extendable to Slack, email) to send incident summaries.

---

## ⚡ Features

* 🔍 **Runtime threat detection** with Falco and MITRE ATT&CK mapping.
* 🧠 **Risk‑based decision engine** — customisable thresholds and workload rules (criticality, namespaces, etc.).
* 🤖 **AI layer** surfaces patterns like repeated pod activity or namespace anomalies and adjusts risk (+20 by default).
* ⚡ **Automated response playbooks**: label pods, apply network isolation, scale deployments.
* 🔐 **Kubernetes‑native quarantine** — uses labels and `NetworkPolicy` for isolation; safe for single or multiple replicas.
* 👁 **Manual approval workflow** for medium‑risk events; reviewers can approve or reject quarantine actions.
* 📊 **Incident forensics API** with human‑readable timeline generation.
* 🎛 **Dashboard** with filtering (status, severity, namespace), AI explanations, risk score adjustments, and approval state icons.
* 📦 **CI/CD security validation** — includes GitHub Actions workflows to lint charts and build/push images.
* 🔁 **Event‑driven architecture** — integrates seamlessly with Falco & Falcosidekick.

---

## 🌍 Use Cases

* SaaS platforms running multi‑tenant Kubernetes clusters.
* Fintech or regulated environments with sensitive workloads.
* Cloud‑native startups needing automated runtime security.
* Teams adopting DevSecOps and seeking to close the loop between detection and response.

---

## 🚀 Future Improvements

* Slack alerting (currently supports Telegram).
* Multi‑cluster control plane & centralised forensics.
* Advanced policy engines (OPA, Kyverno) integration.
* Replay & simulation mode for training and testing.
* Persistent storage pluggable back‑ends (e.g. NoSQL).

---

## 👨‍💻 Author

Built by **Iheb Mrabet** – DevSecOps engineer .

---

## ⭐ Final Note

This project demonstrates:

✔ Real‑world DevSecOps architecture
✔ Security automation & incident response
✔ Deep Kubernetes understanding
✔ Event‑driven systems

It’s designed as a **mini security platform**, not just a demo.  Contributions and feedback are welcome!
