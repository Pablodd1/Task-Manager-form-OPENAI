# Team Task Manager

A friendly, efficient, and simple task manager designed for teams. Track assignments, manage workflows, and ensure daily focus with automated reminders. Built with Flask and ready for deployment on Vercel.

## Features

- **Employee Task Tracking**: Assign tasks to specific staff members with email and due dates.
- **Review Workflow**: Structured status progression:
  - `Todo` -> `In Progress` -> `Under Review` -> `Done`
- **Friendly UI**: A clean, card-based interface for easy visualization.
- **Daily Reminders**: Automated daily reminders for pending tasks (integrated with Vercel Cron).
- **Serverless Ready**: Configured for seamless deployment on Vercel Free Tier.

## Data Storage Note

This application uses **In-Memory Storage**.
- Data **will reset** if the application restarts or (on Vercel) when the serverless function cold-starts.
- This is by design for a simple, zero-configuration setup. For persistent storage, a database (like PostgreSQL or MongoDB) would need to be integrated.

## Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app/main.py
   ```
   Access the app at `http://127.0.0.1:5000`.

## Vercel Deployment

This project includes a `vercel.json` configuration file optimized for the Vercel Python Runtime.

1. **Push to GitHub**: Ensure your code is in a GitHub repository.
2. **Import to Vercel**:
   - Go to [Vercel](https://vercel.com).
   - Click "Add New Project" and select your GitHub repository.
   - Vercel will detect the configuration and deploy automatically.
3. **Cron Jobs**:
   - The `vercel.json` includes a Cron job that hits `/api/cron/reminders` daily at 9:00 AM UTC.
   - You can view the execution logs in the Vercel Dashboard.

## API Endpoints

- `GET /tasks`: List all tasks.
- `POST /tasks`: Create a new task.
- `PUT /tasks/<id>`: Update task status or details.
- `DELETE /tasks/<id>`: Remove a task.
- `POST /api/cron/reminders`: Trigger daily reminders (logs to stdout).

## License

Open Source.
