import React, { useEffect, useMemo, useState } from "react";
import { getIncidents, approveIncident, rejectIncident } from "./api";

function severityColor(severity) {
  switch ((severity || "").toLowerCase()) {
    case "critical":
      return "#dc2626";
    case "high":
      return "#ea580c";
    case "medium":
      return "#ca8a04";
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
    default:
      return "#2563eb";
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
    marginLeft: "8px",
  };
}

function buttonStyle(bg) {
  return {
    backgroundColor: bg,
    color: "white",
    border: "none",
    padding: "8px 14px",
    borderRadius: "8px",
    cursor: "pointer",
    marginRight: "10px",
    fontWeight: "bold",
  };
}

function sectionTitleStyle() {
  return {
    marginTop: "14px",
    marginBottom: "6px",
    fontSize: "14px",
    fontWeight: "bold",
    color: "#111827",
  };
}

function listStyle() {
  return {
    marginTop: "4px",
    marginBottom: "8px",
    paddingLeft: "20px",
  };
}

function preStyle() {
  return {
    backgroundColor: "#f3f4f6",
    padding: "10px",
    borderRadius: "8px",
    overflowX: "auto",
    fontSize: "12px",
  };
}

function App() {
  const [incidents, setIncidents] = useState([]);
  const [filter, setFilter] = useState("all");

  async function load() {
    try {
      const data = await getIncidents();
      setIncidents(data.incidents || []);
    } catch (err) {
      console.error("Failed to load incidents:", err);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  const filteredIncidents = useMemo(() => {
    if (filter === "all") return incidents;
    if (filter === "pending") {
      return incidents.filter((inc) => inc.status === "pending");
    }
    if (filter === "contained") {
      return incidents.filter((inc) => inc.status === "contained");
    }
    if (filter === "closed") {
      return incidents.filter((inc) => inc.status === "closed");
    }
    if (filter === "critical") {
      return incidents.filter((inc) => inc.decision?.severity === "critical");
    }
    if (filter === "high") {
      return incidents.filter((inc) => inc.decision?.severity === "high");
    }
    if (filter === "medium") {
      return incidents.filter((inc) => inc.decision?.severity === "medium");
    }
    return incidents;
  }, [incidents, filter]);

  return (
    <div
      style={{
        padding: "24px",
        backgroundColor: "#f8fafc",
        minHeight: "100vh",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1 style={{ marginBottom: "20px" }}>CloudQuarantine Dashboard</h1>

      <div style={{ marginBottom: "20px" }}>
        <label style={{ marginRight: "10px", fontWeight: "bold" }}>Filter:</label>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ padding: "8px", borderRadius: "8px" }}
        >
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="contained">Contained</option>
          <option value="closed">Closed</option>
          <option value="critical">Critical only</option>
          <option value="high">High only</option>
          <option value="medium">Medium only</option>
        </select>
      </div>

      {filteredIncidents.length === 0 ? (
        <p>No incidents found.</p>
      ) : (
        filteredIncidents.map((incident) => (
          <div
            key={incident.id}
            style={{
              backgroundColor: "white",
              borderRadius: "14px",
              padding: "18px",
              marginBottom: "18px",
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              borderLeft: `8px solid ${severityColor(incident.decision?.severity)}`,
            }}
          >
            <p><b>ID:</b> {incident.id}</p>
            <p><b>Timestamp:</b> {incident.timestamp}</p>
            <p><b>Score:</b> {incident.decision?.score}</p>

            <p>
              <b>Severity:</b>
              <span style={badgeStyle(severityColor(incident.decision?.severity))}>
                {incident.decision?.severity}
              </span>
            </p>

            <p>
              <b>Status:</b>
              <span style={badgeStyle(statusColor(incident.status))}>
                {incident.status}
              </span>
            </p>

            <p><b>Mode:</b> {incident.decision?.decision_mode}</p>
            <p><b>Policy:</b> {incident.policy_name} ({incident.policy_version})</p>
            <p><b>Namespace:</b> {incident.decision?.context?.namespace || "unknown"}</p>
            <p><b>Pod:</b> {incident.decision?.context?.pod_name || "unknown"}</p>

            <div style={sectionTitleStyle()}>Reasons</div>
            <ul style={listStyle()}>
              {(incident.decision_reasons || []).map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>

            <div style={sectionTitleStyle()}>Matched Rules</div>
            <ul style={listStyle()}>
              {(incident.matched_rules || []).map((rule, index) => (
                <li key={index}>{rule}</li>
              ))}
            </ul>

            {(incident.safety_blocks || []).length > 0 && (
              <>
                <div style={sectionTitleStyle()}>Safety Blocks</div>
                <ul style={listStyle()}>
                  {incident.safety_blocks.map((block, index) => (
                    <li key={index}>{block}</li>
                  ))}
                </ul>
              </>
            )}

            <div style={sectionTitleStyle()}>Response Profile</div>
            <pre style={preStyle()}>
              {JSON.stringify(incident.response_profile || {}, null, 2)}
            </pre>

            {(incident.decision?.context?.workload_profile || incident.decision?.context?.workload_profile === {}) && (
              <>
                <div style={sectionTitleStyle()}>Workload Context</div>
                <pre style={preStyle()}>
                  {JSON.stringify(incident.decision?.context?.workload_profile || {}, null, 2)}
                </pre>
              </>
            )}

            {incident.approval_state === "waiting" && (
              <div style={{ marginTop: "14px" }}>
                <button
                  style={buttonStyle("#dc2626")}
                  onClick={async () => {
                    await approveIncident(incident.id);
                    load();
                  }}
                >
                  Approve
                </button>

                <button
                  style={buttonStyle("#6b7280")}
                  onClick={async () => {
                    await rejectIncident(incident.id);
                    load();
                  }}
                >
                  Reject
                </button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default App;
