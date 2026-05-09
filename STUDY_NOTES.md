# MyCode OS Study Notes

These notes are for reviewing and defending the CS50x final project.

## What app.py Does

`app.py` is the main Flask application file. It creates the Flask app, configures the database path, defines constants for project statuses, task priorities, task statuses, and payment methods, and contains all routes.

It also includes:

- Database connection helpers.
- The `init-db` command.
- Authentication routes.
- Dashboard route.
- Client routes.
- Project routes.
- Task routes.
- Payment route.
- Project notes route.
- Error handlers.

## What schema.sql Does

`schema.sql` defines the SQLite database structure. It drops old tables first and then creates fresh tables for:

- `users`
- `clients`
- `projects`
- `tasks`
- `payments`
- `project_notes`

It also defines foreign keys so clients, projects, tasks, payments, and notes are connected logically.

## What requirements.txt Does

`requirements.txt` lists the Python packages needed to run the app:

- `Flask`
- `Werkzeug`

Flask also installs related dependencies such as Jinja2 and Click.

## What templates/ Contains

`templates/` contains the Jinja HTML files. These are rendered by Flask routes.

- `layout.html`: shared page layout, sidebar, header, flash messages.
- `login.html`: login form.
- `register.html`: registration form.
- `dashboard.html`: dashboard metrics and recent work.
- `clients.html`: client list.
- `client_form.html`: create/edit client form.
- `projects.html`: project list and status filters.
- `project_form.html`: create/edit project form.
- `project_detail.html`: project details, tasks, payments, notes.
- `tasks.html`: all tasks page.
- `error.html`: simple error page.

## What static/ Contains

`static/` contains files served directly by Flask:

- `styles.css`: the dark dashboard visual style.
- `app.js`: the small canvas chart used on the dashboard.
- `mycode-logo.png`: the MyCode logo used in the sidebar.

## How Register Works

The `/register` route accepts GET and POST.

GET shows the registration form. POST reads the username, password, and password confirmation. It checks that required fields are present, the password is at least six characters, and both password fields match.

If validation passes, the password is hashed with `generate_password_hash`, and the username plus hash are inserted into the `users` table. The plain password is never stored.

## How Login Works

The `/login` route accepts GET and POST.

GET shows the login form. POST looks up the user by username. If the user exists, the submitted password is checked against the stored hash using `check_password_hash`.

If the password is correct, the app clears any old session and stores:

- `session["user_id"]`
- `session["username"]`

Then the user is redirected to the dashboard.

## How Logout Works

The `/logout` route clears the session with `session.clear()`. After that, the user no longer has `user_id` in the session and cannot access protected routes.

## How Sessions Work

Flask sessions store small pieces of user state between requests. In this project, the session stores the logged-in user's id and username.

Protected routes use the `login_required` decorator. If `session["user_id"]` is missing, the user is redirected to `/login`.

## How Password Hashing Works

The app uses Werkzeug:

- `generate_password_hash(password)` when registering.
- `check_password_hash(stored_hash, password)` when logging in.

This means the database stores a hash, not the original password.

## How The Tables Relate

`users` is the main account table.

Each `client` belongs to one user through `user_id`.

Each `project` belongs to one user and one client through `user_id` and `client_id`.

Each `task`, `payment`, and `project_note` belongs to one user and one project through `user_id` and `project_id`.

This structure lets each user have private clients and projects.

## Main Routes

- `/`: redirects logged-in users to the dashboard and others to login.
- `/register`: creates a new user.
- `/login`: authenticates a user.
- `/logout`: clears the session.
- `/dashboard`: shows metrics and recent work.
- `/clients`: lists clients.
- `/clients/new`: creates a client.
- `/clients/<client_id>/edit`: edits a client.
- `/clients/<client_id>/delete`: deletes a client if it has no projects.
- `/projects`: lists and filters projects.
- `/projects/new`: creates a project.
- `/projects/<project_id>`: shows project details.
- `/projects/<project_id>/edit`: edits a project.
- `/projects/<project_id>/delete`: deletes a project and its related tasks, payments, and notes.
- `/projects/<project_id>/tasks`: adds a task.
- `/tasks`: lists all tasks.
- `/tasks/<task_id>/complete`: marks a task as completed.
- `/projects/<project_id>/payments`: records a payment.
- `/projects/<project_id>/notes`: saves a project note.

## Important SQL Queries

The app uses parameterized SQL queries with `?` placeholders. This is important because it avoids building SQL strings directly from user input.

Important examples:

- Register user: inserts username and password hash into `users`.
- Login: selects a user by username.
- Dashboard counts: counts clients, projects, active projects, delivered projects, pending tasks, and overdue tasks.
- Fetch owned client: selects a client by `id` and `user_id`.
- Fetch owned project: selects a project by `id` and `user_id`.
- Client CRUD: inserts, updates, and deletes clients by `user_id`.
- Project CRUD: inserts, updates, and deletes projects by `user_id`.
- Project detail: selects tasks, payments, and notes by `project_id` and `user_id`.

## What To Show In The Video Demo

1. Open the app locally.
2. Show registration.
3. Log in.
4. Explain the dashboard.
5. Create a client.
6. Create a project for that client.
7. Open the project detail page.
8. Add a task.
9. Mark the task complete.
10. Add a payment.
11. Add a note.
12. Show that routes are protected by logging out.
13. Briefly explain the database and files.

## 10 Technical Questions And Simple Answers

1. What problem does this project solve?
It helps freelancers keep clients, projects, tasks, payments, and notes in one private dashboard.

2. Why did you use Flask?
Flask is simple, lightweight, and good for learning routes, templates, sessions, and SQL-backed web apps.

3. Why did you use SQLite?
SQLite is easy to run locally and works well for a small CS50x project without a separate database server.

4. How are passwords stored?
Passwords are hashed with Werkzeug. The plain password is not stored in the database.

5. How does the app know who is logged in?
After login, the app stores the user's id and username in the Flask session.

6. How are routes protected?
Private routes use `@login_required`, which checks if `session["user_id"]` exists.

7. How does each user only see their own data?
Private queries include `WHERE user_id = ?` using the current user's session id.

8. Why do you use parameterized SQL queries?
They keep user input separate from SQL code and help prevent SQL injection.

9. What happens when a project is deleted?
The app deletes related notes, payments, and tasks, then deletes the project.

10. What would you improve next?
I would add search, task editing/deletion, payment editing/deletion, CSRF protection, and better reporting.
