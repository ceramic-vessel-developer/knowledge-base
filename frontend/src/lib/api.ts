import { getToken } from "./auth";
import type {
  Chat,
  ChatAskReturn,
  ChatMessage,
  Document,
  FileType,
  HealthStatus,
  Paginated,
  Token,
  User,
  Workspace,
  WorkspaceOption,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : `Request failed (${status})`);
    this.status = status;
    this.detail = detail;
  }
}

async function parseError(res: Response): Promise<never> {
  let detail: unknown = res.statusText;
  try {
    const body = await res.json();
    detail = body.detail ?? body;
  } catch {
    /* ignore */
  }
  throw new ApiError(res.status, detail);
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (auth) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) await parseError(res);
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthStatus>("/health", {}, false),

  register: (username: string, email: string, password: string) =>
    request<User>(
      "/users",
      {
        method: "POST",
        body: JSON.stringify({ username, email, password }),
      },
      false,
    ),

  login: async (username: string, password: string) => {
    const body = new URLSearchParams();
    body.set("username", username);
    body.set("password", password);
    return request<Token>(
      "/token",
      {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      },
      false,
    );
  },

  me: () => request<User>("/users/me"),

  listWorkspaces: (skip = 0, limit = 20) =>
    request<Paginated<Workspace>>(`/workspace?skip=${skip}&limit=${limit}`),

  workspaceOptions: () => request<WorkspaceOption[]>("/workspace/options"),

  getWorkspace: (id: string) => request<Workspace>(`/workspace/${id}`),

  createWorkspace: (name: string, type: string = "basic") =>
    request<Workspace>("/workspace", {
      method: "POST",
      body: JSON.stringify({ name, type }),
    }),

  renameWorkspace: (id: string, name: string) =>
    request<Workspace>(`/workspace/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ name }),
    }),

  deleteWorkspace: (id: string) =>
    request<void>(`/workspace/${id}`, { method: "DELETE" }),

  listDocuments: (workspaceId: string, skip = 0, limit = 20) =>
    request<Paginated<Document>>(
      `/documents?workspace_id=${encodeURIComponent(workspaceId)}&skip=${skip}&limit=${limit}`,
    ),

  getDocument: (id: string) => request<Document>(`/documents/${id}`),

  uploadDocument: (params: {
    filename: string;
    filetype: FileType;
    workspaceId: string;
    file: File;
  }) => {
    const form = new FormData();
    form.set("filename", params.filename);
    form.set("filetype", String(params.filetype));
    form.set("workspace_id", params.workspaceId);
    form.set("file", params.file);
    return request<Document>("/documents", { method: "POST", body: form });
  },

  deleteDocument: (id: string) =>
    request<void>(`/documents/${id}`, { method: "DELETE" }),

  listChats: (workspaceId: string, skip = 0, limit = 20) =>
    request<Paginated<Chat>>(
      `/chats?workspace_id=${encodeURIComponent(workspaceId)}&skip=${skip}&limit=${limit}`,
    ),

  getChat: (id: string) => request<Chat>(`/chats/${id}`),

  createChat: (name: string, workspaceId: string) =>
    request<Chat>("/chats", {
      method: "POST",
      body: JSON.stringify({ name, workspace_id: workspaceId }),
    }),

  renameChat: (id: string, name: string) =>
    request<Chat>(`/chats/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ name }),
    }),

  deleteChat: (id: string) =>
    request<void>(`/chats/${id}`, { method: "DELETE" }),

  listMessages: (chatId: string, skip = 0, limit = 50) =>
    request<Paginated<ChatMessage>>(
      `/chats/${chatId}/messages?skip=${skip}&limit=${limit}`,
    ),

  ask: (chatId: string, question: string) =>
    request<ChatAskReturn>(`/chats/${chatId}/ask`, {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
};
