# 📘 CloudQuarantine User Guide

This guide helps you understand, run, and test CloudQuarantine step by step.

---

# 🧠 What is CloudQuarantine?

CloudQuarantine is a runtime security system for Kubernetes.

It:
- detects suspicious behavior (Falco)
- evaluates risk (decision engine)
- understands behavior (AI layer)
- reacts automatically (response engine)

---

# ⚙️ Prerequisites

Make sure you have:

- Docker installed
- kubectl installed
- k3d installed
- Helm installed
- Node.js (for dashboard)

---

# 🚀 Step 1 — Start Kubernetes cluster

```bash
k3d cluster create cloudquarantine

Check:

kubectl get nodes
🚀 Step 2 — Deploy CloudQuarantine
helm upgrade --install cloudquarantine helm/cloudquarantine

Check pods:

kubectl get pods

Make sure:

controller is running
Falco is running
Falcosidekick is running
🚀 Step 3 — Start dashboard
cd dashboard
npm install
npm start

Open:

http://localhost:3000
🧪 Step 4 — Create test environment
kubectl create namespace demo-app

kubectl run test-shell \
  --image=busybox \
  --restart=Never \
  -n demo-app \
  -- sleep 3600
🔍 Step 5 — Trigger a security event
kubectl exec -it test-shell -n demo-app -- sh
📊 What happens?
Falco detects the shell
Event is sent to CloudQuarantine
Risk score is calculated
Decision = manual review

👉 You will see it in the dashboard

🔁 Step 6 — Simulate attack (important)

Run multiple times:

kubectl exec -it test-shell -n demo-app -- sh
📈 Result
AI detects repeated behavior
Score increases
Risk escalates

👉 System becomes smarter based on behavior

🚨 Step 7 — Production scenario
kubectl create namespace prod

kubectl run test-shell \
  --image=busybox \
  --restart=Never \
  -n prod \
  -- sleep 3600

kubectl exec -it test-shell -n prod -- sh
💥 Result
High risk detected
Automatic quarantine triggered
🔒 Step 8 — Verify quarantine

Try network access:

kubectl exec test-shell -n prod -- wget -O- http://<service-ip>

👉 Expected:

Connection refused
🧪 Step 9 — Deployment attack
kubectl create deployment nginx-test --image=nginx -n prod
kubectl get pods -n prod

kubectl exec -it <pod-name> -n prod -- sh
💥 Result
System escalates response
Deployment scaled to zero
📊 Dashboard Explanation
🔹 Incidents

List of detected events

🔹 Decision

Shows:

score
severity
reasons
🔹 AI Behavior

Shows:

repeated activity
escalation patterns
🔹 Response

Shows:

actions executed by system
📩 Telegram Alerts

If configured, alerts are sent in real time.

Check:

TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
⚠️ Troubleshooting
❌ No incidents
Check Falco:
kubectl logs -l app=falco
❌ No alerts
Check controller logs:
kubectl logs deployment/cloudquarantine-controller
❌ No quarantine
Check policy thresholds
Check namespace (prod vs demo)
🧠 Key Concept

CloudQuarantine does NOT react to a single event.

It reacts to:

repetition
behavior
context
✅ Summary

CloudQuarantine:

detects threats
understands behavior
decides response
acts automatically
🎯 Recommended Demo Flow
Run shell → see alert
Repeat → see score increase
Run in prod → see quarantine
Attack deployment → see scale to zero

👉 This shows full system power
