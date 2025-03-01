from flask import Flask, jsonify,send_file,request,render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL database configuration (Replace with your actual credentials)
DB_USERNAME = "22CS10015"
DB_PASSWORD = "22CS10015"
DB_HOST = "10.5.18.69"
DB_PORT = "5432"  # Default PostgreSQL port
DB_NAME = "22CS10015"

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Data base tables definations
# An example

class Citizen(db.Model):
    __tablename__ = 'citizen'  # Table name in PostgreSQL
    id = db.Column(db.Integer, primary_key=True)
    citizen_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    household_id = db.Column(db.Integer)
    contact_number = db.Column(db.String(15))
    job = db.Column(db.String(50))
    qualification = db.Column(db.String(50))


class Passkey(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "Admin/Employee/Citizen/Monitor"
    citizen_id = db.Column(db.Integer, db.ForeignKey('citizen.id'))

class Employee(db.Model):
    __tablename__ = 'panchayat_employee'
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, nullable=False)
    employee_role = db.Column(db.String(10))

@app.route('/')
def login_page():
    return send_file("Home.html")

@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Get JSON data from request

    # Validate input
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    username = data['username']
    password = data['password']

    query = ''# An explample query "SELECT id FROM Passkey WHERE username = :username AND password = :password;"
    params = {"username": username, "password": password}

    result = db.session.execute(db.text(query), params).fetchone()

    if not result:
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({'id': result[0], 'success': 'Login successful!'})

@app.route('/home')
def home():
    d = request.args.get('id', type=int)
    print("Id: ",d)

    employee = Employee.query.filter_by(citizen_id = d).first()
    citizen = Citizen.query.filter_by(id=d).first()

    if employee:
        return render_template("Home_employee.html", username=citizen.citizen_name)

    if not citizen:
        return "User not found", 404
    
    # Change with suitable query
    return render_template("Home_citizen.html", username=citizen.citizen_name)

@app.route('/profile')
def profile():
    d = request.args.get('id', type=int)
    employee = Employee.query.filter_by(citizen_id = d).first()
    citizen = Citizen.query.filter_by(id=d).first()
    if employee:
        return send_file("Profile_employee.html")
    if not citizen:
        return "User not found", 404
    
    return send_file("Profile_citizen.html")

@app.route('/get-citizen')
def get_citizen():
    d = request.args.get('id', type=int)

    if not d:
        return jsonify({"error": "Citizen ID is required"}), 400

    citizen = Citizen.query.filter_by(id=d).first()
    if not citizen:
        return jsonify({"error": "Citizen not found"}), 404

    employee = Employee.query.filter_by(citizen_id=d).first()
    #passkey = Passkey.query.filter_by(citizen_id = d).first()
    
    response = {
        "id": citizen.id,
        "name": citizen.citizen_name,
        #"username": passkey.username,
        "dob": citizen.dob.strftime('%Y-%m-%d'),  # Convert Date to string
        "gender": citizen.gender,
        "household_id": citizen.household_id,
        "phone": citizen.contact_number,
        "job": citizen.job,
        "qualification": citizen.qualification,
        "father_id": citizen.father_id,
        "mother_id": citizen.mother_id,
        "is_employee": bool(employee),
        "employee_role": employee.employee_role if employee else None
    }

    return jsonify(response)

@app.route('/update-citizen', methods=['POST'])
def update_citizen():
    data = request.json
    citizen_id = data.get("id")

    if not citizen_id:
        return jsonify({"error": "Citizen ID is required"}), 400

    citizen = Citizen.query.filter_by(id=citizen_id).first()
    #passkey = Passkey.query.filter_by(id=citizen_id).first()

    if not citizen:
        return jsonify({"error": "Citizen not found"}), 404

    # Update only provided values
    # if "username" in data and passkey:
    #     passkey.username = data["username"]
    # if "password" in data and passkey:
    #     passkey.password = data["password"]
    if "job" in data:
        citizen.job = data["job"]
    if "qualification" in data:
        citizen.qualification = data["qualification"]

    try:
        db.session.commit()
        return jsonify({"success": "Profile updated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route('/citizen')
def home_citizen():
    d = request.args.get('id', type=int)

    if d is None:
        return jsonify({'error': 'Citizen ID is required'}), 400

    citizen = Citizen.query.filter_by(id=d).first()

    if not citizen:
        return jsonify({'error': 'Citizen not found'}), 404

    citizen_data = {
        # An example usage
        # "id": citizen.id,
        # "citizen_name": citizen.citizen_name,
        # "dob": str(citizen.dob),
        # "gender": citizen.gender,
        # "household_id": citizen.household_id,
        # "contact_number": citizen.contact_number,
        # "job": citizen.job,
        # "qualification": citizen.qualification,
        # "father_id": citizen.father_id,
        # "mother_id": citizen.mother_id
    }

    return jsonify({"citizen": citizen_data}), send_file("Home_citizen.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5173, debug=True)

# @app.route('/query_raw', methods=['GET'])
# def run_custom_query():
#     d = 5  # Example value for 'd'
    
#     query = "SELECT a FROM x WHERE x.c > :d;"
#     result = db.session.execute(db.text(query), {"d": d})

#     return jsonify([row[0] for row in result])

# from flask import request

# @app.route('/query_dynamic', methods=['GET'])
# def query_dynamic():
#     d = request.args.get('d', type=int)  # Get 'd' from URL parameters

#     query = "SELECT a FROM x WHERE x.c > :d;"
#     result = db.session.execute(db.text(query), {"d": d})

#     return jsonify([row[0] for row in result])


