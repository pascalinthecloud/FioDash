from flask import Flask, request, jsonify, render_template_string
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
app = Flask(__name__)

# Configure MySQL connection
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DATABASE")

mysql = MySQL(app)

# HTML template for the live table with a dropdown and a nuke button
html_template = """
<!doctype html>
<html>
<head>
    <title>FioDash</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f9;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 3px rgba(0,0,0,0.1);
            background-color: #fff;
        }
        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: center;
        }
        th {
            background-color: #f8f8f8;
            color: #333;
        }
        tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .button-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .btn {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .btn-danger {
            background-color: #dc3545;
        }
        .btn-refresh {
            background-color: #007bff;
        }
        .btn-danger:hover {
            background-color: #c82333;
        }
    </style>
    <script type="text/javascript">
        function startPolling() {
            setInterval(fetchAllData, 5000); // Poll every 5 seconds
         }
        // Fetch all hostnames to populate the dropdown
        function fetchAllData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    updateDropdown(data);
                    updateTable(data); // Display all hosts initially
                })
                .catch(error => console.error('Error fetching all data:', error));
        }

        // Fetch data for the selected hostname
        function fetchHostnameData(hostname) {
            fetch('/data/' + hostname)
                .then(response => response.json())
                .then(data => {
                    updateTable(data);
                })
                .catch(error => console.error('Error fetching hostname data:', error));
        }

        // Update dropdown menu with hostnames
        function updateDropdown(data) {
            let dropdown = document.getElementById('hostname_select');
            dropdown.innerHTML = '<option value="">Select hostname</option>';
            let uniqueHostnames = [...new Set(data.map(item => item.hostname))]; // Ensure unique hostnames
            uniqueHostnames.forEach(hostname => {
                let option = document.createElement('option');
                option.value = hostname;
                option.innerText = hostname;
                dropdown.appendChild(option);
            });

            // Restore the selected value
            let selectedValue = localStorage.getItem('selected_hostname');
            if (selectedValue) {
                dropdown.value = selectedValue;
                fetchHostnameData(selectedValue);
            } else {
                updateTable(data); // Display all hosts if no selection
            }
        }

        // Update the table with data
        function updateTable(data) {
            let table = document.getElementById('iops_table');
            table.innerHTML = '';
            if (data.length === 0) {
                let tr = document.createElement('tr');
                let td = document.createElement('td');
                td.colSpan = 5;
                td.innerText = 'No data available';
                tr.appendChild(td);
                table.appendChild(tr);
                return;
            }
            data.forEach(row => {
                let tr = document.createElement('tr');

                let td_hostname = document.createElement('td');
                td_hostname.innerText = row.hostname;

                let td_read_iops = document.createElement('td');
                td_read_iops.innerText = row.read_iops.toFixed(2);

                let td_write_iops = document.createElement('td');
                td_write_iops.innerText = row.write_iops.toFixed(2);

                let td_cpu_usage = document.createElement('td');
                td_cpu_usage.innerText = row.cpu_usage + " %";
                let td_timestamp = document.createElement('td');
                td_timestamp.innerText = row.timestamp;



                tr.appendChild(td_hostname);
                tr.appendChild(td_read_iops);
                tr.appendChild(td_write_iops);
                tr.appendChild(td_cpu_usage);
                tr.appendChild(td_timestamp);
                table.appendChild(tr);
            });
        }

        // Nuke the database and update UI
        function nukeDatabase() {
            fetch('/nuke', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Database nuked successfully!');
                        fetchAllData(); // Refresh the dropdown and table
                        document.getElementById('iops_table').innerHTML = ''; // Clear the table
                        localStorage.removeItem('selected_hostname'); // Clear selected hostname
                    } else {
                        alert('Failed to nuke database.');
                    }
                })
                .catch(error => console.error('Error nuking database:', error));
        }
        function refreshPage() {
            location.reload();
        }

        // Event listener for DOMContentLoaded to fetch initial data
        document.addEventListener('DOMContentLoaded', function() {
            fetchAllData();
            document.getElementById('hostname_select').addEventListener('change', function() {
                let selectedValue = this.value;
                localStorage.setItem('selected_hostname', selectedValue);
                if (selectedValue) {
                    fetchHostnameData(selectedValue);
                } else {
                    fetchAllData(); // Fetch all data if no hostname is selected
                }
            });
        });
    </script>
</head>
<body>
    <div class="button-container">
        <button class="btn btn-danger" onclick="nukeDatabase()">Nuke Database</button>
    </div>
    <div class="button-container">
        <button class="btn btn-refresh" onclick="refreshPage()">Refresh</button>
    </div>
    <h1>FioDash</h1>
    <select id="hostname_select" class="btn">
        <!-- Options will be added here by JavaScript -->
    </select>
    <table>
        <thead>
            <tr>
                <th>Hostname</th>
                <th>(&#x2205;) Read IOPS</th>
                <th>(&#x2205;) Write IOPS</th>
                <th>(Max) CPU Usage</th>
                <th>(Last) Timestamp</th>
            </tr>
        </thead>
        <tbody id="iops_table">
            <!-- Rows will be added here by JavaScript -->
        </tbody>
    </table>
</body>
</html>


"""


@app.route('/data', methods=['GET'])
def get_data():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT hostname, AVG(read_iops) as read_iops, AVG(write_iops) as write_iops, MAX(timestamp) as timestamp, MAX(cpu_usage) as cpu_usage
        FROM iops_data
        GROUP BY hostname
        ORDER BY hostname
    ''')
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@app.route('/data/<hostname>', methods=['GET'])
def get_data_by_hostname(hostname):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT hostname, read_iops, write_iops, timestamp, cpu_usage
        FROM iops_data
        WHERE hostname = %s
        ORDER BY timestamp DESC
    ''', (hostname,))
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@app.route('/update', methods=['POST'])
def update_data():
    try:
        json_data = request.json
        if not json_data:
            return jsonify("No JSON data provided")

        hostname = json_data.get('hostname')
        read_iops = json_data.get('read_iops')
        write_iops = json_data.get('write_iops')
        cpu_usage = json_data.get('cpu_usage')

        if not all([hostname, read_iops, write_iops, cpu_usage]):
            return jsonify("Missing one or more required fields")

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO iops_data (hostname, read_iops, write_iops, cpu_usage) VALUES (%s, %s, %s, %s)',
                       (hostname, read_iops, write_iops, cpu_usage))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/nuke', methods=['POST'])
def nuke_database():
    cursor = mysql.connection.cursor()
    cursor.execute('TRUNCATE TABLE iops_data')
    mysql.connection.commit()
    cursor.close()
    return jsonify({'status': 'success'})


@app.route('/')
def index():
    return render_template_string(html_template)


if __name__ == '__main__':
    app.run(debug=True)
