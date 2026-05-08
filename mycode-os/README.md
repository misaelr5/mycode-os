# MyCode OS

Video demo: TODO - add CS50x video URL here.

## Description

MyCode OS is a Flask and SQLite web application for freelance web developers and small digital studios. It helps manage clients, projects, tasks, payments, notes, and delivery workflows from a single dark dashboard.

The project was built as a CS50x final project, but it is also designed to be useful in a real web studio and presentable as a portfolio project.

## Problem It Solves

Small studios often track leads in chats, project status in spreadsheets, payments in notes, and tasks in separate tools. MyCode OS puts the essential workflow into one simple local web app so a developer can see what is active, what is overdue, what has been paid, and what still needs delivery.

## Main Features

- User registration, login, logout, secure password hashing, and Flask sessions.
- Private data by account using `user_id` checks in every protected query.
- Dashboard metrics for clients, projects, active work, delivered work, tasks, overdue tasks, estimated revenue, paid amount, and pending amount.
- Client CRUD: create, list, edit, and delete clients.
- Project CRUD with status filters and client linking.
- Project detail workspace with project info, client info, tasks, payments, and notes.
- Add tasks, mark tasks completed, record payments, and save project notes.
- Basic server-side validation and flash messages.
- Responsive dark interface with graphite cards and electric blue accents.
- Simple JavaScript canvas chart for project status distribution.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Jinja templates
- Werkzeug password hashing

## Database Design

The database uses six tables:

- `users`: stores account credentials with hashed passwords.
- `clients`: stores client contact and source information.
- `projects`: stores project details, status, dates, budget, and technology notes.
- `tasks`: stores delivery tasks linked to projects.
- `payments`: stores payment records linked to projects.
- `project_notes`: stores internal notes for project delivery.

Each private table includes `user_id`, which is used by the Flask routes to make sure logged-in users can only access their own data.

## File Structure

```text
mycode-os/
├── app.py
├── helpers.py
├── schema.sql
├── requirements.txt
├── README.md
├── static/
│   ├── styles.css
│   └── app.js
└── templates/
    ├── layout.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── clients.html
    ├── client_form.html
    ├── projects.html
    ├── project_detail.html
    ├── project_form.html
    ├── tasks.html
    └── error.html
```

## Design Decisions

The app avoids complex frameworks so it remains easy to explain in a short CS50x demo. Flask routes are explicit, SQLite keeps setup simple, and templates use regular Jinja inheritance.

The UI uses a dark studio dashboard style because the target user is a freelance developer or small digital studio. The first screen after login focuses on metrics and current work instead of marketing content.

Payments are recorded manually because the project intentionally avoids external payment gateways. The app is meant to track business workflow, not process real money.

## How To Run Locally

From inside the `mycode-os` folder:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

Then open the local URL shown by Flask, usually:

```text
http://127.0.0.1:5000
```

## Future Improvements

- Add search for clients and projects.
- Add task editing and deletion.
- Add payment editing and deletion.
- Add export to CSV for invoices or reports.
- Add a lightweight invoice generator.
- Add better analytics for monthly revenue.
- Add file uploads for contracts, briefs, and final assets.

## AI Usage Disclosure

AI assistance was used to help draft and organize parts of this project, including route structure, template structure, CSS styling, README organization, and a small JavaScript chart. Comments were added in source files where AI assistance was directly relevant. The code was reviewed and adapted for the project requirements.
