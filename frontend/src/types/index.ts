/**
 * Intervia — Global TypeScript Types
 * Shared interfaces and types used across the entire frontend.
 * Phase-specific types live in their feature directories.
 */

// ---- API Response wrapper --------------------------------
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// ---- Health Check ----------------------------------------
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

// ---- User (Phase 1) --------------------------------------
export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  created_at: string;
}

// ---- Resume (Phase 2) ------------------------------------
export interface Resume {
  id: string;
  user_id: string;
  filename: string;
  created_at: string;
  candidate_profile?: CandidateProfile;
}

export interface CandidateProfile {
  skills: string[];
  projects: Project[];
  experience: Experience[];
  education: Education[];
  certifications: string[];
  achievements: string[];
}

export interface Project {
  name: string;
  description: string;
  technologies: string[];
  duration?: string;
}

export interface Experience {
  company: string;
  role: string;
  duration: string;
  responsibilities: string[];
}

export interface Education {
  institution: string;
  degree: string;
  field: string;
  year: string;
  gpa?: string;
}

// ---- Job Description (Phase 3) --------------------------
export interface JobDescription {
  id: string;
  user_id: string;
  role: string;
  required_skills: string[];
  preferred_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  skill_gaps: string[];
  created_at: string;
}

// ---- Interview (Phase 5+) --------------------------------
export type InterviewType =
  | "hr"
  | "technical"
  | "behavioral"
  | "resume_deep_dive"
  | "job_specific"
  | "mixed"
  | "pressure";

export type InterviewStatus =
  | "scheduled"
  | "in_progress"
  | "completed"
  | "cancelled";

export interface Interview {
  id: string;
  user_id: string;
  resume_id: string;
  job_id?: string;
  type: InterviewType;
  difficulty: number;
  duration: number;
  status: InterviewStatus;
  started_at?: string;
  completed_at?: string;
  overall_score?: number;
}

// ---- Evaluation (Phase 9) --------------------------------
export interface AnswerEvaluation {
  relevance: number;
  technical_accuracy: number;
  technical_depth: number;
  clarity: number;
  conciseness: number;
  structure: number;
  feedback: string;
  evidence: string[];
}

// ---- Readiness Score (Phase 14) -------------------------
export interface ReadinessScore {
  overall: number;
  technical: number;
  communication: number;
  behavioral: number;
  problem_solving: number;
  resume_knowledge: number;
  answer_quality: number;
}
