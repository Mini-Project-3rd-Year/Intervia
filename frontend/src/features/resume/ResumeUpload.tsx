import { useRef, useState } from "react";
import type { DragEvent, KeyboardEvent } from "react";
import { isAxiosError } from "axios";
import apiClient from "../../services/api";

interface Props {
  onUploadComplete: (resumeId: string) => void;
}

const allowedTypes = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];
const maxSizeBytes = 10 * 1024 * 1024;

export default function ResumeUpload({ onUploadComplete }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (!allowedTypes.includes(file.type)) {
      setError("Only PDF or DOCX files are accepted.");
      return;
    }
    if (file.size > maxSizeBytes) {
      setError("File must be under 10MB.");
      return;
    }

    setError(null);
    setUploading(true);
    const form = new FormData();
    form.append("file", file);

    try {
      const { data } = await apiClient.post<{ resume_id: string }>(
        "/resume/upload",
        form,
        { headers: { "Content-Type": "multipart/form-data" } },
      );
      onUploadComplete(data.resume_id);
    } catch (error) {
      setError(
        (isAxiosError<{ detail?: string }>(error)
          ? error.response?.data?.detail
          : undefined) ||
          "Upload failed. Please try again.",
      );
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files[0];
    if (file) void handleFile(file);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      inputRef.current?.click();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Choose a PDF or DOCX resume to upload"
      aria-busy={uploading}
      onKeyDown={handleKeyDown}
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? "#60a5fa" : "rgba(255,255,255,0.18)"}`,
        borderRadius: 16,
        padding: "3rem 1.5rem",
        textAlign: "center",
        cursor: uploading ? "wait" : "pointer",
        background: dragging ? "rgba(99,102,241,0.08)" : "rgba(255,255,255,0.03)",
        transition: "all 0.2s",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        hidden
        disabled={uploading}
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void handleFile(file);
        }}
      />
      {uploading ? (
        <p style={{ color: "rgba(255,255,255,0.65)" }}>Processing resume…</p>
      ) : (
        <>
          <p style={{ fontSize: "2rem", marginBottom: 8 }}>📄</p>
          <p style={{ fontWeight: 600 }}>Drop your resume here or browse</p>
          <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.875rem", marginTop: 8 }}>
            PDF or DOCX · Max 10MB
          </p>
        </>
      )}
      {error && (
        <p role="alert" style={{ color: "#f87171", marginTop: 12, fontSize: "0.875rem" }}>
          {error}
        </p>
      )}
    </div>
  );
}
