import os
import sqlite3
from datetime import date

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, money, to_float


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["DATABASE"] = os.path.join(app.instance_path, "mycode_os.sqlite")

PROJECT_STATUSES = ["New", "Planning", "Design", "Development", "Review", "Delivered", "Cancelled"]
TASK_PRIORITIES = ["Low", "Medium", "High", "Urgent"]
TASK_STATUSES = ["Pending", "In Progress", "Completed"]
PAYMENT_METHODS = ["Cash", "Transfer", "Mercado Pago", "Card", "Other"]


def get_db():
    if "db" not in g:
        os.makedirs(app.instance_path, exist_ok=True)
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with app.open_resource("schema.sql") as schema:
        db.executescript(schema.read().decode("utf8"))


@app.cli.command("init-db")
def init_db_command():
    """AI-assisted comment: this CLI command was created with AI support and manually checked."""
    init_db()
    print("Initialized the MyCode OS database.")


@app.template_filter("money")
def money_filter(value):
    return money(value)


@app.context_processor
def inject_nav():
    return {"today": date.today().isoformat()}


def current_user_id():
    return session.get("user_id")


def fetch_owned_client(client_id):
    client = get_db().execute(
        "SELECT * FROM clients WHERE id = ? AND user_id = ?",
        (client_id, current_user_id()),
    ).fetchone()
    if client is None:
        abort(404)
    return client


def fetch_owned_project(project_id):
    project = get_db().execute(
        """
        SELECT projects.*, clients.name AS client_name, clients.company, clients.email, clients.phone
        FROM projects
        JOIN clients ON clients.id = projects.client_id
        WHERE projects.id = ? AND projects.user_id = ?
        """,
        (project_id, current_user_id()),
    ).fetchone()
    if project is None:
        abort(404)
    return project


def validate_required(fields):
    errors = []
    for label, value in fields:
        if not value or not value.strip():
            errors.append(f"{label} is required.")
    return errors


@app.route("/")
def index():
    if current_user_id():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        errors = validate_required([("Username", username), ("Password", password)])
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirmation:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html", username=username)

        try:
            get_db().execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            get_db().commit()
        except sqlite3.IntegrityError:
            flash("That username is already taken.", "error")
            return render_template("register.html", username=username)

        flash("Account created. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html", username=username)

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Welcome back to MyCode OS.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    uid = current_user_id()
    metrics = {
        "total_clients": db.execute("SELECT COUNT(*) FROM clients WHERE user_id = ?", (uid,)).fetchone()[0],
        "total_projects": db.execute("SELECT COUNT(*) FROM projects WHERE user_id = ?", (uid,)).fetchone()[0],
        "active_projects": db.execute(
            "SELECT COUNT(*) FROM projects WHERE user_id = ? AND status NOT IN ('Delivered', 'Cancelled')",
            (uid,),
        ).fetchone()[0],
        "delivered_projects": db.execute(
            "SELECT COUNT(*) FROM projects WHERE user_id = ? AND status = 'Delivered'",
            (uid,),
        ).fetchone()[0],
        "pending_tasks": db.execute(
            "SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status != 'Completed'",
            (uid,),
        ).fetchone()[0],
        "overdue_tasks": db.execute(
            """
            SELECT COUNT(*) FROM tasks
            WHERE user_id = ? AND status != 'Completed' AND due_date IS NOT NULL AND due_date < ?
            """,
            (uid, date.today().isoformat()),
        ).fetchone()[0],
    }

    totals = db.execute(
        """
        SELECT COALESCE(SUM(budget), 0) AS budget_total,
               COALESCE((SELECT SUM(amount) FROM payments WHERE user_id = ?), 0) AS paid_total
        FROM projects WHERE user_id = ?
        """,
        (uid, uid),
    ).fetchone()
    metrics["budget_total"] = totals["budget_total"]
    metrics["paid_total"] = totals["paid_total"]
    metrics["pending_total"] = max(totals["budget_total"] - totals["paid_total"], 0)

    recent_projects = db.execute(
        """
        SELECT projects.*, clients.name AS client_name
        FROM projects
        JOIN clients ON clients.id = projects.client_id
        WHERE projects.user_id = ?
        ORDER BY projects.created_at DESC
        LIMIT 5
        """,
        (uid,),
    ).fetchall()
    upcoming_tasks = db.execute(
        """
        SELECT tasks.*, projects.name AS project_name
        FROM tasks
        JOIN projects ON projects.id = tasks.project_id
        WHERE tasks.user_id = ? AND tasks.status != 'Completed'
        ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date ASC
        LIMIT 6
        """,
        (uid,),
    ).fetchall()
    status_counts = db.execute(
        "SELECT status, COUNT(*) AS total FROM projects WHERE user_id = ? GROUP BY status",
        (uid,),
    ).fetchall()

    return render_template(
        "dashboard.html",
        metrics=metrics,
        recent_projects=recent_projects,
        upcoming_tasks=upcoming_tasks,
        status_labels=[row["status"] for row in status_counts],
        status_values=[row["total"] for row in status_counts],
    )


@app.route("/clients")
@login_required
def clients():
    rows = get_db().execute(
        "SELECT * FROM clients WHERE user_id = ? ORDER BY created_at DESC",
        (current_user_id(),),
    ).fetchall()
    return render_template("clients.html", clients=rows)


@app.route("/clients/new", methods=["GET", "POST"])
@login_required
def client_new():
    if request.method == "POST":
        form = request.form
        name = form.get("name", "").strip()
        errors = validate_required([("Client name", name)])
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("client_form.html", client=form, mode="Create")

        get_db().execute(
            """
            INSERT INTO clients (user_id, name, company, phone, email, source, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user_id(),
                name,
                form.get("company", "").strip(),
                form.get("phone", "").strip(),
                form.get("email", "").strip(),
                form.get("source", "").strip(),
                form.get("notes", "").strip(),
            ),
        )
        get_db().commit()
        flash("Client created successfully.", "success")
        return redirect(url_for("clients"))
    return render_template("client_form.html", client={}, mode="Create")


@app.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
@login_required
def client_edit(client_id):
    client = fetch_owned_client(client_id)
    if request.method == "POST":
        form = request.form
        name = form.get("name", "").strip()
        if not name:
            flash("Client name is required.", "error")
            return render_template("client_form.html", client=form, mode="Edit")

        get_db().execute(
            """
            UPDATE clients
            SET name = ?, company = ?, phone = ?, email = ?, source = ?, notes = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                name,
                form.get("company", "").strip(),
                form.get("phone", "").strip(),
                form.get("email", "").strip(),
                form.get("source", "").strip(),
                form.get("notes", "").strip(),
                client_id,
                current_user_id(),
            ),
        )
        get_db().commit()
        flash("Client updated.", "success")
        return redirect(url_for("clients"))
    return render_template("client_form.html", client=client, mode="Edit")


@app.route("/clients/<int:client_id>/delete", methods=["POST"])
@login_required
def client_delete(client_id):
    fetch_owned_client(client_id)
    linked = get_db().execute(
        "SELECT COUNT(*) FROM projects WHERE client_id = ? AND user_id = ?",
        (client_id, current_user_id()),
    ).fetchone()[0]
    if linked:
        flash("Delete or move this client's projects before deleting the client.", "error")
        return redirect(url_for("clients"))
    get_db().execute("DELETE FROM clients WHERE id = ? AND user_id = ?", (client_id, current_user_id()))
    get_db().commit()
    flash("Client deleted.", "success")
    return redirect(url_for("clients"))


@app.route("/projects")
@login_required
def projects():
    status = request.args.get("status", "")
    params = [current_user_id()]
    query = """
        SELECT projects.*, clients.name AS client_name
        FROM projects JOIN clients ON clients.id = projects.client_id
        WHERE projects.user_id = ?
    """
    if status in PROJECT_STATUSES:
        query += " AND projects.status = ?"
        params.append(status)
    query += " ORDER BY projects.created_at DESC"
    rows = get_db().execute(query, params).fetchall()
    return render_template("projects.html", projects=rows, statuses=PROJECT_STATUSES, active_status=status)


def load_project_form(project=None):
    clients = get_db().execute(
        "SELECT id, name, company FROM clients WHERE user_id = ? ORDER BY name",
        (current_user_id(),),
    ).fetchall()
    return clients


def validate_project_form(form):
    errors = validate_required(
        [
            ("Project name", form.get("name", "")),
            ("Status", form.get("status", "")),
            ("Client", form.get("client_id", "")),
        ]
    )
    if form.get("status") not in PROJECT_STATUSES:
        errors.append("Select a valid project status.")
    client_id = form.get("client_id")
    if client_id:
        client = get_db().execute(
            "SELECT id FROM clients WHERE id = ? AND user_id = ?",
            (client_id, current_user_id()),
        ).fetchone()
        if client is None:
            errors.append("Select one of your clients.")
    return errors


@app.route("/projects/new", methods=["GET", "POST"])
@login_required
def project_new():
    clients = load_project_form()
    if not clients:
        flash("Create a client before starting a project.", "error")
        return redirect(url_for("client_new"))
    if request.method == "POST":
        form = request.form
        errors = validate_project_form(form)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("project_form.html", project=form, clients=clients, statuses=PROJECT_STATUSES, mode="Create")

        get_db().execute(
            """
            INSERT INTO projects
            (user_id, client_id, name, type, status, budget, paid_amount, start_date, deadline, description, technologies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            project_values(form),
        )
        get_db().commit()
        flash("Project created successfully.", "success")
        return redirect(url_for("projects"))
    return render_template("project_form.html", project={}, clients=clients, statuses=PROJECT_STATUSES, mode="Create")


def project_values(form):
    return (
        current_user_id(),
        form.get("client_id"),
        form.get("name", "").strip(),
        form.get("type", "").strip(),
        form.get("status", "New"),
        to_float(form.get("budget")),
        to_float(form.get("paid_amount")),
        form.get("start_date", ""),
        form.get("deadline", ""),
        form.get("description", "").strip(),
        form.get("technologies", "").strip(),
    )


@app.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def project_edit(project_id):
    project = fetch_owned_project(project_id)
    clients = load_project_form(project)
    if request.method == "POST":
        form = request.form
        errors = validate_project_form(form)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("project_form.html", project=form, clients=clients, statuses=PROJECT_STATUSES, mode="Edit")

        values = project_values(form)[1:] + (project_id, current_user_id())
        get_db().execute(
            """
            UPDATE projects
            SET client_id = ?, name = ?, type = ?, status = ?, budget = ?, paid_amount = ?,
                start_date = ?, deadline = ?, description = ?, technologies = ?
            WHERE id = ? AND user_id = ?
            """,
            values,
        )
        get_db().commit()
        flash("Project updated.", "success")
        return redirect(url_for("project_detail", project_id=project_id))
    return render_template("project_form.html", project=project, clients=clients, statuses=PROJECT_STATUSES, mode="Edit")


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def project_delete(project_id):
    fetch_owned_project(project_id)
    db = get_db()
    db.execute("DELETE FROM project_notes WHERE project_id = ? AND user_id = ?", (project_id, current_user_id()))
    db.execute("DELETE FROM payments WHERE project_id = ? AND user_id = ?", (project_id, current_user_id()))
    db.execute("DELETE FROM tasks WHERE project_id = ? AND user_id = ?", (project_id, current_user_id()))
    db.execute("DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, current_user_id()))
    db.commit()
    flash("Project and related workflow items deleted.", "success")
    return redirect(url_for("projects"))


@app.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    project = fetch_owned_project(project_id)
    db = get_db()
    uid = current_user_id()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE project_id = ? AND user_id = ? ORDER BY status, due_date",
        (project_id, uid),
    ).fetchall()
    payments = db.execute(
        "SELECT * FROM payments WHERE project_id = ? AND user_id = ? ORDER BY payment_date DESC, created_at DESC",
        (project_id, uid),
    ).fetchall()
    notes = db.execute(
        "SELECT * FROM project_notes WHERE project_id = ? AND user_id = ? ORDER BY created_at DESC",
        (project_id, uid),
    ).fetchall()
    paid_total = sum(payment["amount"] for payment in payments)
    pending_amount = max((project["budget"] or 0) - paid_total, 0)
    return render_template(
        "project_detail.html",
        project=project,
        tasks=tasks,
        payments=payments,
        notes=notes,
        paid_total=paid_total,
        pending_amount=pending_amount,
        priorities=TASK_PRIORITIES,
        task_statuses=TASK_STATUSES,
        payment_methods=PAYMENT_METHODS,
    )


@app.route("/projects/<int:project_id>/tasks", methods=["POST"])
@login_required
def task_add(project_id):
    fetch_owned_project(project_id)
    form = request.form
    title = form.get("title", "").strip()
    priority = form.get("priority", "Medium")
    status = form.get("status", "Pending")
    errors = validate_required([("Task title", title)])
    if priority not in TASK_PRIORITIES:
        errors.append("Select a valid priority.")
    if status not in TASK_STATUSES:
        errors.append("Select a valid task status.")
    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("project_detail", project_id=project_id))

    get_db().execute(
        """
        INSERT INTO tasks (user_id, project_id, title, description, priority, status, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            current_user_id(),
            project_id,
            title,
            form.get("description", "").strip(),
            priority,
            status,
            form.get("due_date", ""),
        ),
    )
    get_db().commit()
    flash("Task added.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required
def task_complete(task_id):
    task = get_db().execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, current_user_id()),
    ).fetchone()
    if task is None:
        abort(404)
    get_db().execute(
        "UPDATE tasks SET status = 'Completed' WHERE id = ? AND user_id = ?",
        (task_id, current_user_id()),
    )
    get_db().commit()
    flash("Task marked as completed.", "success")
    return redirect(url_for("project_detail", project_id=task["project_id"]))


@app.route("/tasks")
@login_required
def tasks():
    rows = get_db().execute(
        """
        SELECT tasks.*, projects.name AS project_name
        FROM tasks JOIN projects ON projects.id = tasks.project_id
        WHERE tasks.user_id = ?
        ORDER BY CASE WHEN tasks.status = 'Completed' THEN 1 ELSE 0 END, tasks.due_date
        """,
        (current_user_id(),),
    ).fetchall()
    return render_template("tasks.html", tasks=rows, priorities=TASK_PRIORITIES, statuses=TASK_STATUSES)


@app.route("/projects/<int:project_id>/payments", methods=["POST"])
@login_required
def payment_add(project_id):
    fetch_owned_project(project_id)
    form = request.form
    amount = to_float(form.get("amount"), -1)
    method = form.get("method", "Transfer")
    if amount <= 0:
        flash("Payment amount must be greater than zero.", "error")
        return redirect(url_for("project_detail", project_id=project_id))
    if method not in PAYMENT_METHODS:
        flash("Select a valid payment method.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    get_db().execute(
        """
        INSERT INTO payments (user_id, project_id, amount, method, payment_date, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            current_user_id(),
            project_id,
            amount,
            method,
            form.get("payment_date", date.today().isoformat()),
            form.get("notes", "").strip(),
        ),
    )
    get_db().commit()
    flash("Payment recorded.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/projects/<int:project_id>/notes", methods=["POST"])
@login_required
def note_add(project_id):
    fetch_owned_project(project_id)
    note = request.form.get("note", "").strip()
    if not note:
        flash("Note cannot be empty.", "error")
        return redirect(url_for("project_detail", project_id=project_id))

    get_db().execute(
        "INSERT INTO project_notes (user_id, project_id, note) VALUES (?, ?, ?)",
        (current_user_id(), project_id, note),
    )
    get_db().commit()
    flash("Note saved.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="The page or record was not found."), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", code=500, message="Something went wrong inside MyCode OS."), 500


if __name__ == "__main__":
    app.run(debug=True)
