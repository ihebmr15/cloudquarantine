const API = "http://localhost:8000/api/v1";

export async function getIncidents() {
  const res = await fetch(`${API}/incidents`);
  if (!res.ok) throw new Error("Failed to fetch incidents");
  return res.json();
}

export async function approveIncident(id) {
  const res = await fetch(`${API}/incidents/${id}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "quarantine" }),
  });
  if (!res.ok) throw new Error("Failed to approve incident");
  return res.json();
}

export async function rejectIncident(id) {
  const res = await fetch(`${API}/incidents/${id}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("Failed to reject incident");
  return res.json();
}
