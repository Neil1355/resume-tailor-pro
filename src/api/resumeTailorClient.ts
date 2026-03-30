// API client for resume tailor backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface TailorRequest {
  job_description: string;
}

export interface TailorResponse {
  message: string;
  output_docx_path: string;
  output_pdf_path: string;
}

export async function tailorResume(jobDescription: string): Promise<TailorResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tailor`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ job_description: jobDescription }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}
