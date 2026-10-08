export type UserRole = "user" | "admin";
export type WorkspaceType = "basic";
export type MessageAuthor = "user" | "ai";
export type FileType = 1 | 2 | 3;

export interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  created_at: string;
  modified_at: string;
  deleted_at: string | null;
  is_deleted: boolean;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Workspace {
  id: string;
  name: string;
  type: WorkspaceType;
  user_id: string;
  created_at: string;
  modified_at: string;
  deleted_at: string | null;
  is_deleted: boolean;
}

export interface WorkspaceOption {
  id: string;
  name: string;
  type: WorkspaceType;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface Document {
  id: string;
  filename: string;
  filetype: FileType;
  workspace_id: string;
  created_at: string;
  modified_at: string;
  deleted_at: string | null;
  is_deleted: boolean;
}

export interface Chat {
  id: string;
  name: string;
  workspace_id: string;
  created_at: string;
  modified_at: string;
  deleted_at: string | null;
  is_deleted: boolean;
}

export interface ChatMessage {
  id: string;
  content: string;
  author: MessageAuthor;
  chat_id: string;
  created_at: string;
  modified_at: string;
  deleted_at: string | null;
  is_deleted: boolean;
}

export interface ChatAskReturn {
  user_message: ChatMessage;
  ai_message: ChatMessage;
}

export interface HealthStatus {
  status: string;
  database: boolean;
  vector_store: boolean;
}

export const FILE_TYPE_LABELS: Record<FileType, string> = {
  1: "PDF",
  2: "TXT",
  3: "OTHER",
};
