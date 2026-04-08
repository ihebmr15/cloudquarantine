# CloudQuarantine

Event-driven Kubernetes runtime security platform for detection, decision-making, automated response, and incident forensics.

CloudQuarantine is a runtime security control plane designed for Kubernetes environments. It receives security events from Falco, evaluates their risk, enriches them with workload context and behavior analysis, then decides whether to log, alert, request manual approval, or automatically quarantine the affected workload.

Instead of stopping at detection, CloudQuarantine turns runtime alerts into concrete security actions.

## Why CloudQuarantine?

Runtime security tools often detect suspicious activity but leave the response to humans. That creates a gap between detection and containment.

CloudQuarantine closes that gap by adding:

- Risk-based decision-making
- Behavior-aware scoring
- Automated quarantine workflows
- Manual review when automation is risky
- Forensic visibility for every incident

This makes it useful not only as a detection layer, but as a lightweight runtime security platform.

## What it does

CloudQuarantine can:

- Detect suspicious container activity through Falco
- Normalize and process runtime events
- Score incidents using a policy-driven decision engine
- Enrich decisions with AI-style behavior analysis
- Trigger automatic quarantine for high-risk workloads
- Support manual approval for medium-risk incidents
- Isolate pods with labels + NetworkPolicy
- Scale Deployments to zero in critical scenarios
- Store incidents for forensic analysis
- Show incidents and decisions in a dashboard
- Send Telegram alerts in real time

## Core concept
```text
Falco = detection
CloudQuarantine = detection + decision + response + forensics
```

CloudQuarantine does not only ask “Was something suspicious?”  
It also asks:

- How risky is it?
- Is this happening repeatedly?
- Is this in production?
- Should the system act automatically or wait for approval?

## High-level architecture
```text
Falco (Runtime Detection)
        ↓
Falcosidekick (Event Routing)
        ↓
CloudQuarantine Controller (FastAPI)
        ↓
Decision Engine (Risk Scoring)
        ↓
AI Behavior Layer (Repetition + Context)
        ↓
Response Engine (Playbooks)
        ↓
Kubernetes API
        ↓
Isolation / Quarantine / Scaling
        ↓
Forensics Store + Dashboard + Alerts
```

## Key features

### Runtime threat detection

- Detects shell execution inside containers
- Detects suspicious root activity
- Processes Falco runtime events in real time

### Risk-based decision engine

- Policy-based scoring
- Context-aware evaluation using:
  - namespace
  - workload type
  - criticality
  - mounts and privileges
- Clear decision modes:
  - log only
  - manual review
  - automatic quarantine

### Behavior analysis layer

- Tracks repeated activity on the same pod
- Tracks anomaly patterns at namespace level
- Increases score when suspicious behavior repeats
- Makes decisions more adaptive than static rules alone

### Automated response

- Label compromised pod as quarantined
- Apply deny-all `NetworkPolicy`
- Scale owning `Deployment` to zero when needed
- Preserve a response trail for review

### Manual approval workflow

Some incidents are intentionally not auto-contained. Operators can approve or reject actions from the dashboard.

### Dashboard

- Incident list with filters
- Severity and status badges
- Score, reasons, and matched rules
- AI behavior insights
- Response result details
- Approve / Reject actions for pending incidents

### Alerting

- Telegram notifications for real-time incident awareness

### Forensics

- Incident persistence
- Timeline generation
- Raw event visibility for investigation

## AI / behavior layer
CloudQuarantine includes a lightweight behavior analysis layer that improves scoring.

It looks at patterns such as:

- repeated suspicious activity on the same pod
- repeated suspicious activity inside the same namespace
- activity continuing after previous containment

This means a single shell event may only require manual review, while repeated shell activity can raise the risk score and push the system toward stronger containment.
Example:

- First shell in `demo-app` → medium risk → manual review
- Repeated shells in same pod → score increases
- Same action in `prod` → automatic quarantine
- Same action on a Deployment-backed workload → deployment scaled to zero

## Quarantine capabilities
Depending on policy and workload type, CloudQuarantine can perform:

- Pod labeling  
  marks the affected pod as quarantined
- Network isolation  
  applies a deny-all NetworkPolicy to block communication
- Deployment containment  
  resolves ReplicaSet → Deployment ownership  
  scales the workload to zero for stronger containment

These actions are designed to be Kubernetes-native and easy to audit.

## Incident lifecycle
A typical incident goes through this flow:

1. Falco detects suspicious behavior
2. Falcosidekick forwards the event
3. CloudQuarantine normalizes the payload
4. Noise and duplicates are filtered
5. Workload context is collected
6. Risk score is calculated
7. Behavior analysis adjusts the score if necessary
8. Decision is made:
   - log
   - manual review
   - automatic quarantine
9. Response is executed
10. Incident is stored and shown in the dashboard
11. Telegram alert is sent if configured

## Example demo scenarios

### 1) Manual review scenario

Trigger a shell inside a pod in a non-production namespace:

```bash
kubectl exec -it test-shell -n demo-app -- sh
```
Expected result:

- incident appears in dashboard
- medium risk score
- decision mode = manual review
- operator can approve or reject

### 2) Automatic quarantine scenario

Trigger the same type of event in production:

```bash
kubectl exec -it test-shell -n prod -- sh
```
Expected result:

- high risk score
- automatic quarantine
- pod labeled and network isolated

### 3) Deployment containment scenario

Trigger a shell inside a Deployment-backed pod:

```bash
kubectl exec -it <nginx-pod> -n prod -- sh
```
Expected result:

- deployment owner resolved
- deployment scaled to zero
- incident stored with full response details

## Tech stack

- Kubernetes (k3d)
- Falco
- Falcosidekick
- FastAPI
- React
- PostgreSQL
- Helm
- Telegram Bot API

## Use cases
CloudQuarantine is useful in environments such as:

- SaaS platforms running Kubernetes
- Cloud-native startups
- Fintech / regulated workloads
- Multi-tenant clusters
- DevSecOps labs and automation workflows
- Runtime security demonstrations and research

## Roadmap / future improvements
Potential next steps include:

- Slack / Teams alerting
- Multi-cluster control plane
- Richer policy engine integration (OPA / Kyverno)
- Incident replay mode
- More advanced anomaly detection
- Screenshot-rich dashboard analytics
- Role-based access to approval workflows

## Author
Iheb Mrabet  
Aspiring DevSecOps Engineer

## Final note
CloudQuarantine was built to behave like a small runtime security platform, not just a detection demo.
It demonstrates:

- Kubernetes runtime security understanding
- Risk-based automation
- Incident response design
- Behavior-aware detection
- Full-stack DevSecOps thinking
