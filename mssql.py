import pyodbc
import sys
import webbrowser
from flask import Flask, render_template_string, jsonify, request, redirect, url_for
from threading import Timer

app = Flask(__name__)
db = None  # To hold the database instance

class MSSQLDatabase:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = self.connect_to_database()

    def connect_to_database(self):
        try:
            conn_str = f"DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password};"
            return pyodbc.connect(conn_str)
        except pyodbc.Error as e:
            print(f"Error: {e}")
            return None

    def get_table_names(self):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            tables = [row.TABLE_NAME for row in cursor.fetchall()]
            cursor.close()
            return tables
        return []

    def get_table_data(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return {"columns": columns, "rows": rows}

    def save_record(self, table, values):
        columns_str = ', '.join(values.keys())
        placeholders = ', '.join(['?'] * len(values))
        values_str = tuple(values.values())

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})", values_str)
            self.connection.commit()
            return True
        except Exception as e:
            return str(e)

    def update_record(self, table, values, key):
        primary_key_column = self.get_primary_key_column(table)
        if not primary_key_column:
            return "Primary key column not found."

        set_values = ', '.join([f"{col} = ?" for col in values.keys()])
        update_query = f"UPDATE {table} SET {set_values} WHERE {primary_key_column} = ?"

        cursor = self.connection.cursor()
        try:
            cursor.execute(update_query, list(values.values()) + [key])
            self.connection.commit()
            return True
        except Exception as e:
            return str(e)

    def delete_record(self, table, key):
        primary_key_column = self.get_primary_key_column(table)
        if not primary_key_column:
            return "Primary key column not found."

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"DELETE FROM {table} WHERE {primary_key_column}=?", (key,))
            self.connection.commit()
            return True
        except Exception as e:
            return str(e)

    def get_primary_key_column(self, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + CONSTRAINT_NAME), 'IsPrimaryKey') = 1 AND TABLE_NAME = '{table_name}'")
        row = cursor.fetchone()
        cursor.close()
        if row:
            return row[0]
        else:
            return None

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Connection</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Connect to Database</h1>
        <form method="POST" action="/connect">
            <div class="form-group">
                <label for="server">Server</label>
                <input type="text" class="form-control" id="server" name="server" required>
            </div>
            <div class="form-group">
                <label for="database">Database</label>
                <input type="text" class="form-control" id="database" name="database" required>
            </div>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Connect</button>
        </form>
        {% if message %}
        <div class="alert alert-info mt-3">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
""")

@app.route('/connect', methods=['POST'])
def connect():
    global db
    server = request.form['server']
    database = request.form['database']
    username = request.form['username']
    password = request.form['password']
    db = MSSQLDatabase(server, database, username, password)
    if db.connection:
        message = "Connected successfully"
        return redirect(url_for('select_tables'))
    else:
        message = "Failed to connect to the database"
        return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Connection</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Connect to Database</h1>
        <form method="POST" action="/connect">
            <div class="form-group">
                <label for="server">Server</label>
                <input type="text" class="form-control" id="server" name="server" required>
            </div>
            <div class="form-group">
                <label for="database">Database</label>
                <input type="text" class="form-control" id="database" name="database" required>
            </div>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Connect</button>
        </form>
        <div class="alert alert-danger mt-3">Failed to connect to the database</div>
    </div>
</body>
</html>
""")

@app.route('/select_tables')
def select_tables():
    tables = db.get_table_names()
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Select Tables</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Select Tables to Operate</h1>
        <form method="POST" action="/operate">
            <div class="form-group">
                {% for table in tables %}
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" name="tables" value="{{ table }}" id="table{{ loop.index }}">
                    <label class="form-check-label" for="table{{ loop.index }}">{{ table }}</label>
                </div>
                {% endfor %}
            </div>
            <button type="submit" class="btn btn-primary">Next</button>
        </form>
    </div>
</body>
</html>
""", tables=tables)
@app.route('/operate', methods=['POST'])
def operate():
    selected_tables = request.form.getlist('tables')
    tables = {table: db.get_table_data(table) for table in selected_tables}
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Operate on Tables</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Operate on Tables</h1>
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
            <a class="navbar-brand" href="#">Tables</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav mr-auto">
                    {% for table, data in tables.items() %}
                    <li class="nav-item">
                        <a class="nav-link" href="#" onclick="loadTable('{{ table }}')">{{ table }}</a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </nav>
        <div id="tableContainer" class="mt-3"></div>
        <div id="formContainer"></div>

        <!-- Add/Edit Modal -->
        <div class="modal fade" id="recordModal" tabindex="-1" role="dialog" aria-labelledby="recordModalLabel" aria-hidden="true">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="recordModalLabel">Record Form</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form id="recordForm"></form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="saveButton">Save</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadTable(tableName) {
            fetch(`/table/${tableName}`)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('tableContainer');
                container.innerHTML = '';

                const table = document.createElement('table');
                table.className = 'table table-bordered';

                const thead = document.createElement('thead');
                const trHead = document.createElement('tr');
                data.columns.forEach(column => {
                    const th = document.createElement('th');
                    th.textContent = column;
                    trHead.appendChild(th);
                });
                const actionTh = document.createElement('th');
                actionTh.textContent = 'Actions';
                trHead.appendChild(actionTh);
                thead.appendChild(trHead);

                const tbody = document.createElement('tbody');
                data.rows.forEach(row => {
                    const trBody = document.createElement('tr');
                    data.columns.forEach(column => {
                        const td = document.createElement('td');
                        td.textContent = row[column];
                        trBody.appendChild(td);
                    });
                    const actionTd = document.createElement('td');
                    actionTd.innerHTML = `
                        <button class="btn btn-primary btn-sm" onclick="showEditForm('${tableName}', this)">Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteRow('${tableName}', this)">Delete</button>
                    `;
                    trBody.appendChild(actionTd);
                    tbody.appendChild(trBody);
                });

                table.appendChild(thead);
                table.appendChild(tbody);
                container.appendChild(table);
                document.getElementById('formContainer').innerHTML = `
                    <button class="btn btn-success mt-3" onclick="showAddForm('${tableName}')">Add Record</button>
                `;
            });
        }

        function showAddForm(tableName) {
            fetch(`/table_columns/${tableName}`)
            .then(response => response.json())
            .then(columns => {
                const form = document.getElementById('recordForm');
                form.innerHTML = columns.map(column => `
                    <div class="form-group">
                        <label for="${column}">${column}</label>
                        <input type="text" class="form-control" id="${column}" name="${column}">
                    </div>
                `).join('');

                document.getElementById('saveButton').onclick = function() {
                    saveRecord('add', tableName);
                };

                $('#recordModal').modal('show');
            });
        }

        function showEditForm(tableName, button) {
            const tr = button.parentElement.parentElement;
            const table = tr.parentElement.parentElement;
            const columns = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent);
            const rowData = Array.from(tr.querySelectorAll('td')).map(td => td.textContent);

            const form = document.getElementById('recordForm');
            form.innerHTML = columns.slice(0, -1).map((column, i) => `
                <div class="form-group">
                    <label for="${column}">${column}</label>
                    <input type="text" class="form-control" id="${column}" name="${column}" value="${rowData[i]}">
                </div>
            `).join('');

            document.getElementById('saveButton').onclick = function() {
                saveRecord('edit', tableName, rowData[0]);
            };

            $('#recordModal').modal('show');
        }

        function saveRecord(action, tableName, key) {
            const form = document.getElementById('recordForm');
            const formData = new FormData(form);
            const values = Object.fromEntries(formData.entries());

            const url = action === 'add' ? '/add_record' : '/update_record';
            const data = action === 'add' ? { table: tableName, values } : { table: tableName, values, key };

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success === true) {
                    $('#recordModal').modal('hide');
                    loadTable(tableName);
                } else {
                    alert('Save failed: ' + data.success);
                }
            });
        }

        function deleteRow(tableName, button) {
            const tr = button.parentElement.parentElement;
            const rowData = Array.from(tr.querySelectorAll('td')).map(td => td.textContent);

            if (!confirm('Are you sure you want to delete this record?')) return;

            fetch('/delete_record', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ table: tableName, key: rowData[0] })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success === true) {
                    loadTable(tableName);
                } else {
                    alert('Delete failed: ' + data.success);
                }
            });
        }
    </script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
""", tables=tables)
@app.route('/table_columns/<table_name>')
def get_table_columns(table_name):
    table_data = db.get_table_data(table_name)
    return jsonify(table_data["columns"])
@app.route('/table/<table_name>')
def get_table(table_name):
    table_data = db.get_table_data(table_name)
    return jsonify(table_data)

@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.get_json()
    table = data['table']
    values = data['values']
    success = db.save_record(table, values)
    if success is True:
        return jsonify({"success": True})
    else:
        return jsonify({"success": success})  # Return the error message

@app.route('/update_record', methods=['POST'])
def update_record():
    data = request.get_json()
    table = data['table']
    values = data['values']
    key = data['key']
    success = db.update_record(table, values, key)
    if success is True:
        return jsonify({"success": True})
    else:
        return jsonify({"success": success})  # Return the error message

@app.route('/delete_record', methods=['POST'])
def delete_record():
    data = request.get_json()
    table = data['table']
    key = data['key']
    success = db.delete_record(table, key)
    if success is True:
        return jsonify({"success": True})
    else:
        return jsonify({"success": success})  # Return the error message

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True)
