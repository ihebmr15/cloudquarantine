# 📘 CloudQuarantine User Guide

This guide explains how to install, configure and operate the **CloudQuarantine** platform.  It targets operators who want to deploy the system in their own clusters, as well as developers looking to customise policies and response playbooks.

---

## 1 – Prerequisites

* **Kubernetes cluster**: tested with [k3d](https://k3d.io/) but works with any Kubernetes 1.21+.
* **Helm 3** for deploying the chart.
* **Docker** to build images if you modify code.
* **kubectl** configured to talk to your cluster.
* **Telegram bot token & chat ID** if you want Telegram notifications (optional).

---

## 2 – Installation

### 2.1  Set up a local k3d cluster (optional)

```bash
# create a three-node k3d cluster called 'cloudquarantine'
k3d cluster create cloudquarantine --servers 1 --agents 2 \
  --k3s-server-arg "--disable=traefik" \
  --k3s-server-arg "--disable=servicelb"
```

### 2.2  Install Falco & Falcosidekick

Use the [Falco helm chart](https://github.com/falcosecurity/charts):

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
helm install falco falcosecurity/falco \
  --namespace security-monitoring --create-namespace \
  --set falcosidekick.enabled=true \
  --set falcosidekick.webui.enabled=true
```

> Falcosidekick will forward events to the CloudQuarantine controller.

### 2.3  Deploy CloudQuarantine

Clone the repository and update values:

```bash
git clone https://github.com/ihebmr15/cloudquarantine.git
cd cloudquarantine/helm/cloudquarantine

# edit values.yaml to set environment:
# env:
#   APP_ENV: prod
#   RESPONSE_MODE: enforce
#   TELEGRAM_CHAT_ID: "your-chat-id"
#   DATABASE_URL: "postgresql://user:pass@hostname:5432/cloudquarantine"
#   CQ_POLICY_PATH: "/policies/prod-policy.yaml"

helm install cloudquarantine . \
  --namespace cloudquarantine --create-namespace
```

If you modify the controller code:

```bash
docker build --no-cache -t cloudquarantine/controller:latest ../controller
k3d image import cloudquarantine/controller:latest -c cloudquarantine
helm upgrade --install cloudquarantine .
```

---

## 3 – Configuration

### 3.1  Runtime policies

Policies live under `controller/policies`.  Use `prod-policy.yaml` or create your own:

* **thresholds**: base score triggers auto‑quarantine, manual review or dismiss.
* **signals**: per‑signal score boosts (shell spawn, root user, execve, privileged container, hostPath mount, secret mounts, critical workloads).
* **namespace_rules** & **workload_rules**: apply additional score boosts or enforce manual review for specific namespaces, labels or conditions.
* **safety_guards**: prevent auto‑quarantine in system namespaces, require manual review for critical workloads, or avoid isolating single replicas.
* **response_profiles**: define what actions to take for each decision (`send_alert`, `label_pod`, `apply_network_policy`, `persist_incident`).

Update `values.yaml` to point `CQ_POLICY_PATH` at your policy file.

### 3.2  Environment variables

* `APP_ENV`: `dev` (monitor only) or `prod` (enforce).
* `RESPONSE_MODE`: `monitor` (no quarantine) or `enforce`.
* `TELEGRAM_CHAT_ID`: the chat ID for Telegram alerts.
* `TELEGRAM_BOT_TOKEN`: stored in a Kubernetes `Secret`.
* `DATABASE_URL`: PostgreSQL connection string.
* `CQ_POLICY_PATH`: path to policy file inside the controller container.

### 3.3  NetworkPolicy template

The built‑in response engine applies a `NetworkPolicy` named `quarantine-deny-all` in the target namespace.  Adjust `controller/app/kube/network_policy_ops.py` if you need a custom isolation rule.

---

## 4 – Usage

### 4.1  Trigger an attack

Create a test pod and open a shell to simulate suspicious activity:

```bash
# demo namespace
kubectl create ns demo-app --dry-run=client -o yaml | kubectl apply -f -
kubectl run test-shell --image=busybox --restart=Never -n demo-app -- sleep 3600
kubectl exec -it test-shell -n demo-app -- sh
# inside the container, just type 'ls /' or run any command, then exit
```

Falco will emit an event that CloudQuarantine interprets as a shell spawn with root privileges.

### 4.2  Observe system reaction

1. **Falco** logs the event.
2. **Falcosidekick** forwards it to the controller.
3. **Decision Engine** calculates a score; if thresholds dictate, it chooses manual review or automatic quarantine.
4. **Response Engine** executes the playbook:

   * labels the pod with `cloudquarantine/status=quarantined`.
   * applies the `quarantine-deny-all` `NetworkPolicy` in the namespace (automatic mode).
   * scales the Deployment to zero if `advanced quarantine` is enabled for multi‑replica workloads.

### 4.3  Verify isolation

In automatic mode you should see:

```bash
kubectl exec test-shell -n demo-app -- wget -O- http://kubernetes.default
# -> Connection refused

# Another pod in the namespace:
kubectl run network-check --image=busybox -n demo-app --restart=Never \
  -- wget -O- http://kubernetes.default
# -> Success (not quarantined)
```

In manual review mode the controller logs will show **[MODE] MANUAL REVIEW → Alert only, no quarantine** and the pod will not be isolated until you approve it.

---

## 5 – Dashboard

Run `npm install && npm start` inside `dashboard/` to launch the React UI (it uses `vite`).  The dashboard features:

* **Incidents list** with filters (status, severity, namespace).
* **Score & AI insights** — repeated pod or namespace activity adds a visible **(+20 AI boost)** next to the score.
* **Decision mode** clearly labelled (“Automatic” or “Manual review”).
* **Approval state with icons**: 🟢 approved, 🔴 contained, 🟡 waiting (manual review).
* **Manual approval buttons** to approve or reject quarantines.
* **Human‑readable timeline** for each incident, plus the original Falco JSON for deeper inspection.

---

## 6 – Customisation

* **Define new Falco rules** to detect additional behaviours (e.g. crypto‑mining).
* **Write new response playbooks** in `controller/app/response/` for actions beyond labelling and network isolation.
* **Extend the AI layer** in `controller/app/services/decision_engine.py` to add more signals (e.g. time‑weighted scoring, user behaviour analytics).
* **Integrate other alerting channels** by implementing `app/alerting/<channel>.py` and updating `values.yaml`.
* **Tweak the dashboard** (React) to add new insights, charts, or authentication.

---

## 7 – Demo Scenario

To showcase CloudQuarantine end‑to‑end:

1. Deploy the system as described above.
2. Trigger a shell in a pod (`kubectl exec -it test-shell -n demo-app -- sh`).
3. Watch the controller logs or Telegram chat for the alert.
4. Navigate to the dashboard at `http://localhost:3000` (default dev port).
5. Inspect the incident — note the AI insights and that manual review is required.
6. Click **Approve** to quarantine.  The dashboard will update the pod state and network isolation will take effect.
7. Try connecting from inside the quarantined pod (expect failure) and from another pod (expect success).
8. View the timeline at `/api/v1/incidents/timeline` for a chronological view of the event, decision, and response.

---

## 8 – Troubleshooting

* **No incidents appear** — ensure Falco and Falcosidekick are running and that the controller’s `/api/v1/webhook/falco` endpoint is reachable (check DNS or use `values.yaml` to configure sidekick Webhook).
* **Telegram errors** — verify `TELEGRAM_BOT_TOKEN` is stored in the Secret and `TELEGRAM_CHAT_ID` is set in `values.yaml`.
* **Pods never quarantined** — check `RESPONSE_MODE` and policy thresholds.  In `dev` or `monitor` modes the system only logs.
* **Database errors** — confirm `DATABASE_URL` points to a reachable PostgreSQL instance; you may deploy the included `cq-postgres` helm chart for local testing.
* **Dashboard shows “Failed to fetch”** — ensure the controller (`cloudquarantine-controller`) is running and accessible from the UI.

---
