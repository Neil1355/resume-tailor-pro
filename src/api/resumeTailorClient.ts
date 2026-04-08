// API client for resume tailor backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const TAILOR_TIMEOUT_MS = 120000;

export interface TailorRequest {
  job_description: string;
}

export interface TailorResponse {
  message: string;
  output_docx_path: string;
  output_pdf_path: string | null;
  original_bullets: Record<string, string>;
  tailored_bullets: Record<string, string>;
}

export async function tailorResume(jobDescription: string): Promise<TailorResponse> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), TAILOR_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/tailor`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ job_description: jobDescription }),
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Tailoring timed out after 2 minutes. Please try again.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }

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

export async function downloadTailoredResume(format: "pdf" | "docx"): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/download/${format}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Download failed: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `tailored_resume.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
