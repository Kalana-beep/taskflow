# TaskFlow Frontend

A modern, responsive Next.js 14 task management dashboard interface with Tailwind CSS, Lucide icons, and full end-to-end task workflow controls.

## Features

- **SaaS Dashboard Layout:** Visual metrics for total, todo, in progress, completed, and high priority tasks.
- **Full CRUD Support:** Create, read, edit, delete tasks with instant feedback.
- **Dynamic Search & Filtering:** Filter tasks instantly by title/description, status, or priority.
- **FastAPI Integration:** Robust typed API client connecting to the FastAPI backend.
- **Accessible & Responsive:** Fluid responsive experience for mobile, tablet, and desktop viewports.
- **Isolated Testing:** Component and integration testing with Vitest and React Testing Library.

## Getting Started

### Local Development

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to view the application.

### Scripts

- `npm run dev`: Launch local development server
- `npm run build`: Compile standalone production bundle
- `npm run start`: Start production server
- `npm run lint`: Execute ESLint checks
- `npm run typecheck`: Run TypeScript static type verification
- `npm test`: Run Vitest component test suite
