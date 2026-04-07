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

function App() {
  const [incidents, setIncidents] = useState([]);
  const [filter, setFilter] = useState("all");

  async function load() {
    const data = await getIncidents();
    setIncidents(data.incidents || []);
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
          <option value="medium">Medium only</option>
        </select>
      </div>

      {filteredIncidents.length === 0 ? (
        <p>No incidents found.</p>
      ) : (
        filteredIncidents.map((inc) => (
          <div
            key={inc.id}
            style={{
              backgroundColor: "white",
              borderRadius: "14px",
              padding: "18px",
              marginBottom: "18px",
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              borderLeft: `8px solid ${severityColor(inc.decision?.severity)}`,
            }}
          >
            <p><b>ID:</b> {inc.id}</p>
            <p><b>Score:</b> {inc.decision?.score}</p>
            <p>
              <b>Severity:</b>
              <span style={badgeStyle(severityColor(inc.decision?.severity))}>
                {inc.decision?.severity}
              </span>
            </p>
            <p>
              <b>Status:</b>
              <span style={badgeStyle(statusColor(inc.status))}>
                {inc.status}
              </span>
            </p>
            <p><b>Mode:</b> {inc.decision?.decision_mode}</p>

            {inc.approval_state === "waiting" && (
              <div style={{ marginTop: "14px" }}>
                <button
                  style={buttonStyle("#dc2626")}
                  onClick={async () => {
                    await approveIncident(inc.id);
                    load();
                  }}
                >
                  Approve
                </button>

                <button
                  style={buttonStyle("#6b7280")}
                  onClick={async () => {
                    await rejectIncident(inc.id);
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
