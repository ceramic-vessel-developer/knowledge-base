# Knowledge Workspace frontend

Next.js App Router UI for the FastAPI backend.

## Setup

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Set `NEXT_PUBLIC_API_URL` to your API base (default `http://localhost:8000`). The backend CORS list must include `http://localhost:3000`.

## Routes

- `/` — landing
- `/login`, `/register` — auth
- `/workspaces` — manage workspaces (logged-in home)
- `/workspaces/[id]` — documents + chats
- `/workspaces/[id]/documents/[documentId]` — document detail
- `/workspaces/[id]/chats/[chatId]` — chat Q&A
