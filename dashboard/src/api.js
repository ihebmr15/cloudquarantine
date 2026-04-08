const API_BASE_URL = "http://localhost:8000/api/v1";

async function handleResponse(response) {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }
  return response.json();
}

export async function getIncidents() {
  const response = await fetch(`${API_BASE_URL}/incidents`);
  return handleResponse(response);
}

export async function getTimeline() {
  const response = await fetch(`${API_BASE_URL}/incidents/timeline`);
  return handleResponse(response);
}

export async function approveIncident(incidentId) {
  const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}/approve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}

export async function rejectIncident(incidentId) {
  const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}/reject`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(response);
}
