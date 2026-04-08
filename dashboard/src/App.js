import React, { useEffect, useMemo, useState } from "react";
import { getIncidents } from "./api";

function severityColor(severity) {
  switch ((severity || "").toLowerCase()) {
    case "critical":
      return "#b91c1c";
    case "high":
      return "#dc2626";
    case "medium":
      return "#d97706";
    case "low":
      return "#16a34a";
    default:
      return "#6b7280";
  }
}

function statusColor(status) {
  switch ((status || "").toLowerCase()) {
    case "pending":
      return "#d97706";
    case "contained":
      return "#dc2626";
    case "closed":
      return "#6b7280";
    case "approved":
      return "#2563eb";
    case "rejected":
      return "#7c3aed";
    default:
      return "#374151";
  }
}

function badgeStyle(color) {
  return {
    display: "inline-block",
    padding: "4px 10px",
    borderRadius: "999px",
    color: "white",
    backgroundColor: color,
    fontSize: "12px",
    fontWeight: "bold",
  };
}

function cardStyle(selected) {
  return {
    border: selected ? "2px solid #2563eb" : "1px solid #e5e7eb",
    borderRadius: "14px",
    padding: "16px",
    marginBottom: "14px",
    background: "white",
    boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
    cursor: "pointer",
  };
}

function sectionTitle(text) {
  return (
    <h3
      style={{
        marginTop: "18px",
        marginBottom: "10px",
        fontSize: "15px",
        fontWeight: "700",
        color: "#111827",
      }}
    >
      {text}
    </h3>
  );
}

function prettyJson(data) {
  return JSON.stringify(data, null, 2);
}

function formatTimestamp(value) {
  if (!value) return "unknown";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function StatCard({ label, value }) {
  return (
    <div
      style={{
        background: "white",
        border: "1px solid #e5e7eb",
        borderRadius: "14px",
        padding: "16px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
      }}
    >
      <div style={{ fontSize: "13px", color: "#6b7280", marginBottom: "8px" }}>
        {label}
      </div>
      <div style={{ fontSize: "24px", fontWeight: "700", color: "#111827" }}>
        {value}
      </div>
    </div>
  );
}

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");

  const [statusFilter, setStatusFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [namespaceFilter, setNamespaceFilter] = useState("all");

  async function loadIncidents(isRefresh = false) {
    try {
      setError("");

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const data = await getIncidents();
      const items = data.incidents || [];
      setIncidents(items);

      setSelectedIncident((current) => {
        if (!items.length) return null;
        if (!current) return items[0];
        return items.find((item) => item.id === current.id) || items[0];
      });
    } catch (err) {
      setError(err.message || "Failed to load incidents");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  async function approveIncident(incidentId) {
    try {
      setActionLoading(true);
      setError("");

      const response = await fetch(
        `http://localhost:8000/api/v1/incidents/${incidentId}/approve`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Approve failed: ${text}`);
      }

      await loadIncidents(true);
    } catch (err) {
      setError(err.message || "Failed to approve incident");
    } finally {
      setActionLoading(false);
    }
  }

  async function rejectIncident(incidentId) {
    try {
      setActionLoading(true);
      setError("");

      const response = await fetch(
        `http://localhost:8000/api/v1/incidents/${incidentId}/reject`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Reject failed: ${text}`);
      }

      await loadIncidents(true);
    } catch (err) {
      setError(err.message || "Failed to reject incident");
    } finally {
      setActionLoading(false);
    }
  }

  useEffect(() => {
    loadIncidents();

    const interval = setInterval(() => {
      loadIncidents(true);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const namespaces = useMemo(() => {
    const values = new Set();
    incidents.forEach((incident) => {
      const ns =
        incident?.decision?.context?.workload_profile?.namespace ||
        incident?.decision?.context?.namespace ||
        "unknown";
      values.add(ns);
    });
    return ["all", ...Array.from(values)];
  }, [incidents]);

  const filteredIncidents = useMemo(() => {
    return incidents.filter((incident) => {
      const status = (incident.status || "").toLowerCase();
      const severity = (
        incident.decision?.severity ||
        incident.severity ||
        ""
      ).toLowerCase();
      const namespace =
        incident?.decision?.context?.workload_profile?.namespace ||
        incident?.decision?.context?.namespace ||
        "unknown";

      if (statusFilter !== "all" && status !== statusFilter) return false;
      if (severityFilter !== "all" && severity !== severityFilter) return false;
      if (namespaceFilter !== "all" && namespace !== namespaceFilter) return false;

      return true;
    });
  }, [incidents, statusFilter, severityFilter, namespaceFilter]);

  const stats = useMemo(() => {
    const total = incidents.length;
    const pending = incidents.filter(
      (i) => (i.status || "").toLowerCase() === "pending"
    ).length;
    const contained = incidents.filter(
      (i) => (i.status || "").toLowerCase() === "contained"
    ).length;
    const highOrCritical = incidents.filter((i) => {
      const sev = (i.decision?.severity || i.severity || "").toLowerCase();
      return sev === "high" || sev === "critical";
    }).length;

    return { total, pending, contained, highOrCritical };
  }, [incidents]);

  const detail = selectedIncident;
  const decision = detail?.decision || {};
  const context = decision?.context || {};
  const workload = context?.workload_profile || {};
  const response = detail?.response || {};
  const canReview = detail?.approval_state === "waiting";

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f3f4f6",
        padding: "24px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div style={{ maxWidth: "1400px", margin: "0 auto" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "22px",
          }}
        >
          <div>
            <h1 style={{ margin: 0, fontSize: "30px", color: "#111827" }}>
              CloudQuarantine Dashboard
            </h1>
            <p style={{ margin: "8px 0 0 0", color: "#6b7280" }}>
              Runtime security incidents, policy decisions, and response actions
            </p>
          </div>

          <button
            onClick={() => loadIncidents(true)}
            disabled={refreshing}
            style={{
              background: "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "10px",
              padding: "10px 16px",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {error && (
          <div
            style={{
              background: "#fee2e2",
              border: "1px solid #fecaca",
              color: "#991b1b",
              padding: "12px 14px",
              borderRadius: "10px",
              marginBottom: "18px",
            }}
          >
            {error}
          </div>
        )}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            gap: "14px",
            marginBottom: "22px",
          }}
        >
          <StatCard label="Total incidents" value={stats.total} />
          <StatCard label="Pending review" value={stats.pending} />
          <StatCard label="Contained" value={stats.contained} />
          <StatCard label="High / Critical" value={stats.highOrCritical} />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "320px 1fr",
            gap: "20px",
            alignItems: "start",
          }}
        >
          <div>
            <div
              style={{
                background: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "14px",
                padding: "16px",
                marginBottom: "16px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
              }}
            >
              <h2 style={{ marginTop: 0, marginBottom: "14px", fontSize: "18px" }}>
                Filters
              </h2>

              <label style={{ display: "block", marginBottom: "12px" }}>
                <div style={{ marginBottom: "6px", fontSize: "13px", color: "#374151" }}>
                  Status
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  style={{ width: "100%", padding: "8px", borderRadius: "8px" }}
                >
                  <option value="all">All</option>
                  <option value="pending">Pending</option>
                  <option value="contained">Contained</option>
                  <option value="closed">Closed</option>
                </select>
              </label>

              <label style={{ display: "block", marginBottom: "12px" }}>
                <div style={{ marginBottom: "6px", fontSize: "13px", color: "#374151" }}>
                  Severity
                </div>
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  style={{ width: "100%", padding: "8px", borderRadius: "8px" }}
                >
                  <option value="all">All</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </label>

              <label style={{ display: "block" }}>
                <div style={{ marginBottom: "6px", fontSize: "13px", color: "#374151" }}>
                  Namespace
                </div>
                <select
                  value={namespaceFilter}
                  onChange={(e) => setNamespaceFilter(e.target.value)}
                  style={{ width: "100%", padding: "8px", borderRadius: "8px" }}
                >
                  {namespaces.map((ns) => (
                    <option key={ns} value={ns}>
                      {ns}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div
              style={{
                background: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "14px",
                padding: "16px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
              }}
            >
              <h2 style={{ marginTop: 0, marginBottom: "14px", fontSize: "18px" }}>
                Incidents
              </h2>

              {loading ? (
                <div style={{ color: "#6b7280" }}>Loading incidents...</div>
              ) : filteredIncidents.length === 0 ? (
                <div style={{ color: "#6b7280" }}>No incidents found.</div>
              ) : (
                filteredIncidents.map((incident) => {
                  const sev = incident?.decision?.severity || incident?.severity || "unknown";
                  const ns =
                    incident?.decision?.context?.workload_profile?.namespace ||
                    incident?.decision?.context?.namespace ||
                    "unknown";
                  const pod =
                    incident?.decision?.context?.workload_profile?.pod_name ||
                    incident?.decision?.context?.pod_name ||
                    "unknown";

                  return (
                    <div
                      key={incident.id}
                      onClick={() => setSelectedIncident(incident)}
                      style={cardStyle(selectedIncident?.id === incident.id)}
                    >
                      <div
                        style={{
                          fontSize: "12px",
                          color: "#6b7280",
                          marginBottom: "8px",
                          wordBreak: "break-all",
                        }}
                      >
                        {incident.id}
                      </div>

                      <div
                        style={{
                          display: "flex",
                          gap: "8px",
                          flexWrap: "wrap",
                          marginBottom: "10px",
                        }}
                      >
                        <span style={badgeStyle(severityColor(sev))}>{sev}</span>
                        <span style={badgeStyle(statusColor(incident.status))}>
                          {incident.status}
                        </span>
                      </div>

                      <div style={{ fontWeight: "700", color: "#111827", marginBottom: "6px" }}>
                        {incident?.event?.rule || "Unknown rule"}
                      </div>

                      <div style={{ fontSize: "13px", color: "#4b5563" }}>
                        Namespace: {ns}
                      </div>
                      <div style={{ fontSize: "13px", color: "#4b5563" }}>
                        Pod: {pod}
                      </div>
                      <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "8px" }}>
                        {formatTimestamp(incident.timestamp)}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          <div
            style={{
              background: "white",
              border: "1px solid #e5e7eb",
              borderRadius: "14px",
              padding: "20px",
              boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
              minHeight: "700px",
            }}
          >
            {!detail ? (
              <div style={{ color: "#6b7280" }}>Select an incident to view details.</div>
            ) : (
              <>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "12px",
                    alignItems: "start",
                    marginBottom: "18px",
                  }}
                >
                  <div>
                    <h2 style={{ margin: 0, color: "#111827" }}>
                      {detail?.event?.rule || "Incident Detail"}
                    </h2>
                    <div style={{ color: "#6b7280", marginTop: "8px", wordBreak: "break-all" }}>
                      ID: {detail.id}
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                    <span style={badgeStyle(severityColor(decision.severity))}>
                      {decision.severity || "unknown"}
                    </span>
                    <span style={badgeStyle(statusColor(detail.status))}>
                      {detail.status || "unknown"}
                    </span>
                  </div>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                    gap: "10px",
                    marginBottom: "16px",
                  }}
                >
                  <div><strong>Timestamp:</strong> {formatTimestamp(detail.timestamp)}</div>
                  <div><strong>Score:</strong> {decision.score ?? "unknown"}</div>
                  <div><strong>Policy:</strong> {decision.policy_name || "unknown"}</div>
                  <div><strong>Policy Version:</strong> {decision.policy_version || "unknown"}</div>
                  <div><strong>Namespace:</strong> {context.namespace || workload.namespace || "unknown"}</div>
                  <div><strong>Pod:</strong> {context.pod_name || workload.pod_name || "unknown"}</div>
                  <div><strong>Mode:</strong> {decision.decision_mode || "unknown"}</div>
                  <div><strong>Recommended Action:</strong> {decision.recommended_action || "unknown"}</div>
                  <div><strong>Approval State:</strong> {detail.approval_state || "unknown"}</div>
                  <div><strong>Approved Action:</strong> {detail.approved_action || "none"}</div>
                </div>

                <div style={{ display: "flex", gap: "10px", marginBottom: "18px" }}>
                  <button
                    onClick={() => approveIncident(detail.id)}
                    disabled={!canReview || actionLoading}
                    style={{
                      padding: "10px 14px",
                      borderRadius: "10px",
                      border: "none",
                      background: "#16a34a",
                      color: "white",
                      fontWeight: "700",
                      opacity: !canReview || actionLoading ? 0.6 : 1,
                      cursor: !canReview || actionLoading ? "not-allowed" : "pointer",
                    }}
                  >
                    {actionLoading ? "Working..." : "Approve"}
                  </button>

                  <button
                    onClick={() => rejectIncident(detail.id)}
                    disabled={!canReview || actionLoading}
                    style={{
                      padding: "10px 14px",
                      borderRadius: "10px",
                      border: "none",
                      background: "#dc2626",
                      color: "white",
                      fontWeight: "700",
                      opacity: !canReview || actionLoading ? 0.6 : 1,
                      cursor: !canReview || actionLoading ? "not-allowed" : "pointer",
                    }}
                  >
                    {actionLoading ? "Working..." : "Reject"}
                  </button>

                  {!canReview && (
                    <div style={{ alignSelf: "center", color: "#6b7280", fontSize: "13px" }}>
                      This incident is no longer waiting for manual review.
                    </div>
                  )}
                </div>

                {sectionTitle("Reasons")}
                <ul style={{ marginTop: 0, color: "#374151" }}>
                  {(decision.reasons || []).map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>

                {sectionTitle("Matched Rules")}
                <ul style={{ marginTop: 0, color: "#374151" }}>
                  {(decision.matched_rules || []).map((rule, index) => (
                    <li key={index}>{rule}</li>
                  ))}
                </ul>

                {sectionTitle("Response Profile")}
                <pre
                  style={{
                    background: "#111827",
                    color: "#f9fafb",
                    padding: "14px",
                    borderRadius: "10px",
                    overflowX: "auto",
                    fontSize: "12px",
                  }}
                >
                  {prettyJson(decision.response_profile || {})}
                </pre>

                {sectionTitle("Workload Context")}
                <pre
                  style={{
                    background: "#111827",
                    color: "#f9fafb",
                    padding: "14px",
                    borderRadius: "10px",
                    overflowX: "auto",
                    fontSize: "12px",
                  }}
                >
                  {prettyJson(workload || {})}
                </pre>

                {sectionTitle("Response Result")}
                <pre
                  style={{
                    background: "#111827",
                    color: "#f9fafb",
                    padding: "14px",
                    borderRadius: "10px",
                    overflowX: "auto",
                    fontSize: "12px",
                  }}
                >
                  {prettyJson(response || {})}
                </pre>

                {sectionTitle("Original Event")}
                <pre
                  style={{
                    background: "#111827",
                    color: "#f9fafb",
                    padding: "14px",
                    borderRadius: "10px",
                    overflowX: "auto",
                    fontSize: "12px",
                  }}
                >
                  {prettyJson(detail.event || {})}
                </pre>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
