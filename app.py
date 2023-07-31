# app.py
from flask import Flask, jsonify, request, session
from flask_mysqldb import MySQL, MySQLdb
from flask_cors import CORS
from datetime import timedelta
import datetime

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'clientuser'
app.config['MYSQL_PASSWORD'] = 'ClientPassword'
app.config['MYSQL_DB'] = 'air_bot'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_AUTH_PLUGIN_NAME'] = 'caching_sha2_password'

mysql = MySQL(app)

@app.route('/verify', methods=['POST'])
def verify():
    _json = request.json
    _users_key = _json['users_key']
    _users_pc_name = _json['users_pc_name']
    _users_pc_cpu = _json['users_pc_cpu']

    # Get the current datetime
    current_datetime = datetime.datetime.now()
    _users_datetime = current_datetime.strftime(r'%Y-%m-%d %H:%M:%S')
    print(f"SERVER: Verifying User Data:\n        Key: {_users_key}\n        PC Name: {_users_pc_name}\n        CPU: {_users_pc_cpu}")
    
    # validate the received values
    if _users_key and _users_pc_name and _users_pc_cpu:
        # check user exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Prepare the SQL query to check for a matching entry
        query = "SELECT * FROM users WHERE users_key = %s"
        values = (_users_key,)

        cursor.execute(query, values)
        # Check if a matching entry was found
        row = cursor.fetchone()
        if row:
            print('SERVER: Key exists in the Database')
            # User exists, check if users_ip is associated with users_key
            if row['users_pc_name'] is None and row['users_cpu_info'] is None:
                print('SERVER: Fresh Key detected, adding User data')
                # users_pc_name is not set, update it
                update_query = "UPDATE users SET users_pc_name = %s, users_cpu_info = %s, users_start_date = %s WHERE users_key = %s"
                update_values = (_users_pc_name, _users_pc_cpu, _users_datetime, _users_key)

                # Execute the query
                cursor.execute(update_query, update_values)
                mysql.connection.commit()
                return "True"
            elif row['users_pc_name'] is None or row['users_cpu_info'] is None: 
                print('SERVER: Inconsistencies detected in the Database, please check')
            else:
                query = "SELECT * FROM users WHERE users_key = %s AND users_pc_name = %s AND users_cpu_info = %s"
                values = (_users_key, _users_pc_name, _users_pc_cpu)

                cursor.execute(query, values)

                # Check if a row was found (a match exists)
                row = cursor.fetchone()
                if row:
                    print('SERVER: Found the record of matching Key information')

                    # Check if users_permanent is 1 (True)
                    if row['users_permanent'] == 1:
                        print('SERVER: User is a Permanent User')
                        return "True"
                    else:
                        # Get the users_start_date and users_sub_duration from the record
                        users_start_date = row['users_start_date']
                        users_sub_duration = row['users_sub_duration']
                        
                        if users_sub_duration is None:
                            return "True"
                        
                        # Calculate the end_date
                        end_date = users_start_date + datetime.timedelta(days=users_sub_duration)
                        print(f"{end_date} End and Current is {current_datetime}")
                        # Check if the end_date has not passed
                        if end_date >= current_datetime:
                            return "True"
                        else:
                            print('SERVER: Users key is no longer valid')
                            return "False"
                else:
                    print('SERVER: Did not find the record of matching Key information')
                    return "False"
            
        else:
            print('SERVER: Key does not exist in the Database')
            return "False"
    else:
        print('SERVER: Key does not exist in the Database')
        return "False"

if __name__ == "__main__":
    app.run(host='localhost', port=8070)