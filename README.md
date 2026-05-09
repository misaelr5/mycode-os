# MyCode OS

#### Video Demo: TODO

#### Description

MyCode OS is a Flask and SQLite web application made for the CS50x final project. It is designed for a freelance web developer or a small web studio that needs a simple place to manage clients, projects, tasks, payments, notes, and delivery workflow.

The application is not a public SaaS product or a complete business platform. It is a local web app with authentication, private user data, a dashboard, and CRUD-style project management features. My goal was to build something practical, understandable, and useful while practicing Python, Flask, SQL, HTML, CSS, Jinja templates, sessions, and password hashing.

## Problem It Solves

Freelancers often keep client information, project status, task lists, payments, and notes in different places such as chat messages, spreadsheets, notebooks, or separate apps. MyCode OS centralizes the basic workflow in one dashboard.

With this project, a user can:

- Register and log in to a private workspace.
- Store clients and their contact information.
- Create projects linked to clients.
- Track project status, budget, dates, description, and technologies.
- Add tasks to projects and mark them as completed.
- Record manual payments.
- Save internal project notes.
- See dashboard metrics for active work, delivered projects, pending tasks, overdue tasks, estimated revenue, paid amount, and pending amount.

## Main Features

- User registration, login, and logout.
- Password hashing with Werkzeug.
- Flask sessions for authentication.
- Protected routes using a `login_required` helper.
- Data separation by `user_id`.
- Client create, list, edit, and delete.
- Project create, list, edit, delete, detail view, and status filter.
- Task creation and task completion.
- Payment recording.
- Project notes.
- Dashboard metrics.
- Basic server-side validation.
- Error pages for 404 and 500 responses.
- Dark dashboard interface using plain CSS.
- Small JavaScript canvas chart for project status distribution.

## Technologies Used

- Python
- Flask
- SQLite
- SQL
- HTML
- CSS
- JavaScript
- Jinja2 templates
- Werkzeug password hashing
- Git and GitHub

## File Structure

```text
mycode-os/
|-- app.py
|-- helpers.py
|-- schema.sql
|-- requirements.txt
|-- README.md
|-- STUDY_NOTES.md
|-- .gitignore
|-- static/
|   |-- app.js
|   |-- styles.css
|   `-- mycode-logo.png
`-- templates/
    |-- layout.html
    |-- login.html
    |-- register.html
    |-- dashboard.html
    |-- clients.html
    |-- client_form.html
    |-- projects.html
    |-- project_detail.html
    |-- project_form.html
    |-- tasks.html
    `-- error.html
```

The local `instance/` folder is created by Flask when the database is initialized. It is ignored by Git because it contains local data. The database can be rebuilt from `schema.sql`.

## Installation

Run these commands from the folder that contains `app.py`.

### Windows

```bash
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

Then open:

```text
http://127.0.0.1:5000
```

## How To Use The App

1. Open the local Flask URL.
2. Create an account using the register page.
3. Log in with that account.
4. Create a client.
5. Create a project for that client.
6. Open the project detail page.
7. Add tasks, payments, and notes.
8. Use the dashboard to review current metrics.
9. Log out when finished.

After logging out, protected pages redirect back to the login page.

## Database Design

The database has six main tables:

- `users`: stores usernames and password hashes.
- `clients`: stores client contact information and notes.
- `projects`: stores project information and links each project to a client and user.
- `tasks`: stores tasks linked to projects.
- `payments`: stores manual payment records linked to projects.
- `project_notes`: stores internal notes linked to projects.

Most tables include a `user_id` column. Routes filter queries by the current session user so that one user cannot access another user's clients, projects, tasks, payments, or notes through normal app routes.

## Design Decisions

I used Flask because it is small enough to understand clearly but powerful enough for routing, sessions, templates, and database-backed applications.

I used SQLite because it is simple for a local CS50x project and does not require running a separate database server.

I used plain CSS and JavaScript instead of a frontend framework because the focus of the project is Flask, SQL, authentication, and CRUD behavior. The interface uses a dark dashboard style because the target user is a web freelancer or small studio.

Payments are recorded manually. The app does not process real transactions or connect to a payment gateway.

The project uses server-side rendering with Jinja templates. This keeps the request and response flow easier to explain in the final video.

## Current Limitations

- There is no task editing or task deletion.
- There is no payment editing or payment deletion.
- There is no search feature for clients or projects.
- There is no file upload system.
- There is no real payment gateway integration.
- There are no CSRF tokens.
- The app is intended for local/demo use, not production deployment.
- The default development secret key should be replaced with a real environment variable before deploying anywhere public.

## Possible Future Improvements

- Add search for clients and projects.
- Add task editing and deletion.
- Add payment editing and deletion.
- Add CSV export for basic reports.
- Add simple invoice generation.
- Add better date and revenue analytics.
- Add CSRF protection.
- Add deployment configuration for a production environment.

## What I Learned

While building MyCode OS, I practiced organizing a Flask application with routes, templates, helpers, static files, and a SQLite schema. I learned how to connect forms to SQL inserts and updates, how to protect routes with sessions, how to hash passwords, and how to keep records separated by user.

I also learned that small design decisions matter. For example, every private query needs to check `user_id`, and every form needs basic validation so user mistakes do not create server errors. I also practiced writing documentation that explains not only what the project does, but why it was built this way.

## Academic Honesty And Tool Assistance

During development, I used AI-based tools as technical assistance to review code structure, debug errors, improve documentation, and clarify concepts. The project idea, implementation decisions, testing, and final submission are my own.

I did not use assistance to hide the origin of the work or to avoid understanding the code. I reviewed the project so I can explain the routes, database schema, authentication flow, and design decisions in my own words.
