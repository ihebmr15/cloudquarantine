# CloudQuarantine User Guide

This guide explains how to install, run, test, and understand CloudQuarantine.

It is written for users who want to:

- deploy the project locally
- trigger demo incidents
- understand how the system reacts
- explore the dashboard and response flow

## 1. What is CloudQuarantine?
CloudQuarantine is a Kubernetes runtime security system.
A simple way to think about it:

- Falco is the detector
- CloudQuarantine is the decision-maker and responder

Falco notices suspicious behavior.  
CloudQuarantine decides what that behavior means and what to do next.
So instead of only saying:
> “something suspicious happened”
the system can say:
> “this is medium risk, show it for manual review”
or
> “this is high risk, isolate it now”

## 2. What the system is made of
The platform has several parts working together:

- **Falco**  
  Watches runtime activity inside containers and detects suspicious behavior.
- **Falcosidekick**  
  Forwards Falco events to the controller.
- **CloudQuarantine Controller**  
  Receives events, filters them, scores them, and decides what action to take.
- **Decision Engine**  
  Calculates incident risk based on rules and workload context.
- **Behavior Layer**  
  Raises the score when suspicious behavior repeats.
- **Response Engine**  
  Executes actions such as:
  - alerting
  - labeling pods
  - isolating network traffic
  - scaling deployments to zero
- **Dashboard**  
  Shows incidents, decisions, AI insights, and manual approval actions.
- **Telegram Integration**  
  Sends incident summaries in real time.

## 3. Prerequisites
Before using CloudQuarantine, make sure you have:

- Docker
- kubectl
- k3d
- Helm
- Node.js and npm
- access to a Kubernetes cluster (local k3d is enough for demo)
- a Telegram bot token and chat ID if you want alerts

## 4. Start the environment

### Step 1 — Create a cluster
```bash
k3d cluster create cloudquarantine
```
Check that it is running:
```bash
kubectl get nodes
```

### Step 2 — Deploy CloudQuarantine
From the project root:
```bash
helm upgrade --install cloudquarantine helm/cloudquarantine
```
Check deployed resources:
```bash
kubectl get pods
kubectl get svc
```
You should see the controller and supporting components running.

### Step 3 — Start the dashboard
Go to the dashboard folder:
```bash
cd dashboard
npm install
npm start
```
Open the browser at:
```text
http://localhost:3000
```
If your backend is inside Kubernetes and not directly exposed, also forward the API port:
```bash
kubectl port-forward svc/cloudquarantine-controller 8000:8000
```

## 5. Configure Telegram alerts
CloudQuarantine can send Telegram alerts for incidents.
You need:
`TELEGRAM_BOT_TOKEN`
`TELEGRAM_CHAT_ID`
These are usually configured through the Helm chart.
Make sure your values file contains the real token, not a placeholder.
Example:
```yaml
secretEnv:
  TELEGRAM_BOT_TOKEN: "your-real-bot-token"

env:
  TELEGRAM_CHAT_ID: "your-chat-id"
```
After updating values, redeploy:
```bash
helm upgrade --install cloudquarantine helm/cloudquarantine
kubectl rollout restart deployment/cloudquarantine-controller
kubectl rollout status deployment/cloudquarantine-controller
```
To verify:
```bash
kubectl get secret cloudquarantine-secrets -o jsonpath='{.data.TELEGRAM_BOT_TOKEN}' | base64 -d && echo
kubectl exec -it deploy/cloudquarantine-controller -- printenv | grep TELEGRAM
```
If configured correctly, alerts should reach Telegram with status `200`.

## 6. How the system thinks
When a Falco event arrives, CloudQuarantine goes through these steps:

1. **Receive the event**  
   The controller receives the webhook payload.
2. **Filter noise**  
   It ignores:
   - empty events
   - internal controller activity
   - system noise
   - known irrelevant events
3. **Deduplicate**  
   If the same event appears multiple times from Falco/Falcosidekick replicas, duplicates are skipped.
4. **Enrich workload context**  
   The system asks Kubernetes for more information:
   - namespace
   - pod name
   - labels
   - service account
   - privilege level
   - volume types
   - owner kind
   - replicas
   - deployment ownership
5. **Score the risk**  
   The policy engine assigns a score using:
   - rule type
   - root usage
   - shell execution
   - namespace rules
   - workload rules
6. **Apply behavior analysis**  
   The AI layer may increase the score if:
   - the same pod shows repeated suspicious activity
   - the namespace becomes noisy
   - suspicious behavior continues after containment
7. **Decide response mode**  
   Depending on the final score and safety guards, the system chooses:
   - log only
   - manual review
   - automatic quarantine
8. **Execute response**  
   If needed, the response engine:
   - labels the pod
   - applies deny-all network isolation
   - scales the deployment to zero
9. **Persist and alert**  
   The incident is saved, shown in the dashboard, and optionally sent to Telegram.

## 7. Run your first test

### Create a test namespace
```bash
kubectl create namespace demo-app
```

### Create a demo pod
```bash
kubectl run test-shell --image=busybox --restart=Never -n demo-app -- sleep 3600
```

### Trigger a shell event
```bash
kubectl exec -it test-shell -n demo-app -- sh
```
Exit the shell:
```sh
exit
```

## 8. What you should expect
After that command:

- Falco detects the shell
- the controller receives the event
- the dashboard shows a new incident
- the score is calculated
- the event is likely marked manual review in `demo-app`

This is the normal behavior for a lower-risk environment.

## 9. Test repeated behavior
To simulate a repeated suspicious pattern, run the same command multiple times:
```bash
kubectl exec -it test-shell -n demo-app -- sh
```
Do it three or more times.
Expected result
The AI behavior layer should detect repetition.
In the dashboard, you should start seeing things like:

- repeated activity detected on same pod
- namespace shows suspicious activity
- AI score boost

This proves the system is not relying only on static rules.

## 10. Test automatic quarantine in production
Create a production namespace and a pod:
```bash
kubectl create namespace prod
kubectl run test-shell --image=busybox --restart=Never -n prod -- sleep 3600
```
Trigger the event:
```bash
kubectl exec -it test-shell -n prod -- sh
```
Expected result
Because the event happens in a production namespace, the response should be stronger.
You should see:

- higher severity
- automatic quarantine
- response result showing network isolation or containment

## 11. Test Deployment containment
Create a Deployment-backed workload:
```bash
kubectl create deployment nginx-test --image=nginx -n prod
kubectl get pods -n prod
```
Pick the pod name, then run:
```bash
kubectl exec -it <pod-name> -n prod -- sh
```
Expected result
CloudQuarantine should:

- resolve the Deployment owner
- quarantine the workload
- scale the Deployment to zero

This is one of the strongest demos of the platform.

## 12. Understanding the dashboard
The dashboard is your main control surface.

### Incident list

Shows all incidents with:

- severity
- status
- namespace
- pod
- rule
- timestamp

### Filters

You can filter by:

- status
- severity
- namespace

### Incident details

When you click an incident, you see:

- score
- decision mode
- recommended action
- approval state
- matched rules
- reasons
- AI insights
- workload context
- response result
- raw original event

### Manual review actions

If the incident is waiting for human review, you can:

- Approve
- Reject

These actions update the incident state and, if approved, execute the response.

## 13. Approval states explained
CloudQuarantine uses clear approval states:

- waiting → manual review needed
- approved → action accepted
- rejected → action denied
- not_required → automatic decision, no human step needed

This helps separate manual workflows from fully automated containment.

## 14. Common demo flow
A clean demo flow is:
Demo 1 — Manual review
```bash
kubectl exec -it test-shell -n demo-app -- sh
```
Show:

- medium score
- manual review
- dashboard approval buttons

Demo 2 — AI escalation
Repeat the same action several times.
Show:

- AI insights
- score increase
- repeated pod activity

Demo 3 — Automatic quarantine
```bash
kubectl exec -it test-shell -n prod -- sh
```
Show:

- automatic decision
- response result
- Telegram alert

Demo 4 — Deployment shutdown
```bash
kubectl exec -it <nginx-pod> -n prod -- sh
```
Show:

- deployment scaling to zero
- stronger containment

## 15. Troubleshooting

### No incidents in dashboard

Check:
```bash
kubectl logs deployment/cloudquarantine-controller
```
Also verify the frontend can reach the backend:
```bash
kubectl port-forward svc/cloudquarantine-controller 8000:8000
```

### No Telegram alerts

Check:

- token is correct
- chat ID is correct
- secret was updated by Helm
- controller pod has the correct environment variables

### No quarantine happening

Check:

- current namespace
- response mode
- policy thresholds
- whether the incident is manual review instead of automatic

### Dashboard says “Failed to fetch”

Usually the backend is not reachable from the browser. Use:
```bash
kubectl port-forward svc/cloudquarantine-controller 8000:8000
```

## 16. Key idea to remember
CloudQuarantine does not react only to a single event.
It reacts to:

- the event itself
- the workload context
- the namespace
- the behavior pattern
- the response policy

That is what makes it stronger than simple runtime detection.

## 17. Summary
CloudQuarantine is a runtime security platform that:

- detects suspicious behavior
- understands context
- analyzes repetition
- decides risk
- responds automatically
- preserves forensic visibility

It is useful both as a practical project and as a foundation for more advanced Kubernetes security automation.
