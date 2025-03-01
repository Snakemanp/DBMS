from flask import Flask, jsonify, send_file, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# PostgreSQL database configuration
DB_USERNAME = "22CS10015"
DB_PASSWORD = "22CS10015"
DB_HOST = "10.5.18.69"
DB_PORT = "5432"
DB_NAME = "22CS10015"

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database Models
class Citizen(db.Model):
    __tablename__ = 'citizens'
    citizenid = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(255), nullable=False)
    dateofbirth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    householdid = db.Column(db.Integer)
    contactnumber = db.Column(db.String(15))
    job = db.Column(db.String(50))
    educationalqualification = db.Column(db.String(50))
    fatherid = db.Column(db.Integer, db.ForeignKey('citizens.citizenid', ondelete='SET NULL'), nullable=True)
    motherid = db.Column(db.Integer, db.ForeignKey('citizens.citizenid', ondelete='SET NULL'), nullable=True)

class Employee(db.Model):
    __tablename__ = 'employee'
    employeeid = db.Column(db.Integer, primary_key=True)
    citizenid = db.Column(db.Integer, db.ForeignKey('citizens.citizenid', ondelete='CASCADE'), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    citizenid = db.Column(db.Integer, db.ForeignKey('citizens.citizenid', ondelete='SET NULL'), nullable=True)

class Scheme(db.Model):
    __tablename__ = 'welfarescheme'  # Table name in the database

    schemeid = db.Column(db.Integer, primary_key=True)

    # Scheme Details
    schemename = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    eligibilitycriteria = db.Column(db.String(200), nullable=False)
    benefits = db.Column(db.Text, nullable=False)
    launchdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    department = db.Column(db.String(100), nullable=False)
    validtill = db.Column(db.DateTime, nullable=False)

class Schemeapp(db.Model):
    __tablename__ = 'schemeapplication'
    applicationid = db.Column(db.Integer, primary_key=True)
    citizenid = db.Column(db.Integer, db.ForeignKey('citizens.citizenid', ondelete='CASCADE'), nullable=False)
    schemeid = db.Column(db.Integer, db.ForeignKey('welfarescheme.schemeid', ondelete='CASCADE'), nullable=False)
    applicationdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Boolean, nullable=False, default=False)
    remarks = db.Column(db.Text)

@app.route('/')
def login_page():
    return send_file("Home.html")

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if not user or user.password != data['password']:
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return jsonify({'id': user.citizenid, 'success': True})

@app.route('/home')
def home():
    userid = request.args.get('id', type=int)
    citizen = Citizen.query.filter_by(citizenid=userid).first()
    employee = Employee.query.filter_by(citizenid=userid).first()
    
    if not citizen:
        return "User not found", 404
    
    return render_template("Home_employee.html" if employee else "Home_citizen.html", username=citizen.fullname)

@app.route('/profile')
def profile():
    userid = request.args.get('id', type=int)
    citizen = Citizen.query.filter_by(citizenid=userid).first()
    employee = Employee.query.filter_by(citizenid=userid).first()
    
    if not citizen:
        return "User not found", 404
    
    return send_file("Profile_employee.html" if employee else "Profile_citizen.html")

@app.route('/get-citizen')
def get_citizen():
    user_id = request.args.get('id', type=int)
    citizen = Citizen.query.filter_by(citizenid=user_id).first()
    employee = Employee.query.filter_by(citizenid=user_id).first()
    passkey = User.query.filter_by(citizenid=user_id).first()
    
    if not citizen:
        return jsonify({"error": "Citizen not found"}), 404
    
    response = {
        "id": citizen.citizenid,
        "name": citizen.fullname,
        "dob": citizen.dateofbirth.strftime('%Y-%m-%d'),
        "gender": citizen.gender,
        "household_id": citizen.householdid,
        "phone": citizen.contactnumber,
        "job": citizen.job,
        "qualification": citizen.educationalqualification,
        "father_id": citizen.fatherid,
        "mother_id": citizen.motherid,
        "is_employee": bool(employee),
        "username": passkey.username,
        "employee_role": employee.role if employee else None
    }
    return jsonify(response)

@app.route('/update-citizen', methods=['POST'])
def update_citizen():
    data = request.json
    citizen_id = data.get("id")
    
    if not citizen_id:
        return jsonify({"error": "Citizen ID is required"}), 400
    
    citizen = Citizen.query.filter_by(citizenid=citizen_id).first()
    passkey = User.query.filter_by(citizenid=citizen_id).first()
    if not citizen:
        return jsonify({"error": "Citizen not found"}), 404
    
    if "password" in data and data["password"]:
        passkey.password = data["password"]
    if "username" in data and data["username"]:
        passkey.username = data["username"]
    if "job" in data and data["job"]:
        citizen.job = data["job"]
    if "qualification" in data and data["qualification"]:
        citizen.educationalqualification = data["qualification"]

    
    try:
        db.session.commit()
        return jsonify({"success": "Profile updated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/schemes')
def scheme():
    userid = request.args.get('id', type=int)
    citizen = Citizen.query.filter_by(citizenid=userid).first()
    employee = Employee.query.filter_by(citizenid=userid).first()
    
    if not citizen:
        return "User not found", 404

    return send_file("Home_employee.html" if employee else "Schemes_citizen.html")

@app.route('/schemes/getschemes')
def getscheme():
    userid = request.args.get('id', type=int)
    only_applied = request.args.get('onlyapplied', default="false").lower() == "true"

    schemes = []
    if not userid:
        return jsonify({"error": "User ID is required"}), 400

    if not only_applied:
        allschemes = Scheme.query.all()
        for scheme in allschemes:
            schemes.append({
                "schemeid": scheme.schemeid,
                "SchemeName": scheme.schemename,
                "Description": scheme.description,
                "EligibilityCriteria": scheme.eligibilitycriteria,
                "Benefits": scheme.benefits,
                "LaunchDate": scheme.launchdate.strftime('%Y-%m-%d'),
                "Department": scheme.department,
                "ValidTill": scheme.validtill.strftime('%Y-%m-%d'),
                "status": None  # Status is not relevant when fetching all schemes
            })
    else:
        # Fetch schemes along with their application status from Schemeapp
        applied_schemes = (
            db.session.query(Scheme, Schemeapp.remarks)
            .join(Schemeapp, Scheme.schemeid == Schemeapp.schemeid)
            .filter(Schemeapp.citizenid == userid)
            .all()
        )

        for scheme, status in applied_schemes:
            schemes.append({
                "schemeid": scheme.schemeid,
                "SchemeName": scheme.schemename,
                "Description": scheme.description,
                "EligibilityCriteria": scheme.eligibilitycriteria,
                "Benefits": scheme.benefits,
                "LaunchDate": scheme.launchdate.strftime('%Y-%m-%d'),
                "Department": scheme.department,
                "ValidTill": scheme.validtill.strftime('%Y-%m-%d'),
                "status": status  # Status from Schemeapp table
            })

    return jsonify(schemes)

@app.route('/applyschemes', methods=['POST'])
def apply_schemes():
    data = request.json
    userid = request.args.get('id', type=int)

    if not userid:
        return jsonify({"error": "User ID is required"}), 400

    if not data or 'schemeids' not in data:
        return jsonify({"error": "Scheme IDs are required"}), 400

    scheme_ids = data["schemeids"]
    applied_schemes = []

    for schemeid in scheme_ids:
        existing_application = Schemeapp.query.filter_by(citizenid=userid, schemeid=schemeid).first()

        if existing_application:
            applied_schemes.append({"schemeid": schemeid, "message": "Already Applied"})
        else:
            new_application = Schemeapp(
                citizenid=userid,
                schemeid=schemeid,
                remarks="Pending Approval"
            )
            db.session.add(new_application)

    try:
        db.session.commit()
        return jsonify({"success": applied_schemes})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    
#Agri Records
@app.route('/agrirecords')
def agripage():
    userid = request.args.get('id', type=int)
    citizen = Citizen.query.filter_by(citizenid=userid).first()
    if not citizen:
        return "User not found", 404

    return send_file("Agri_citizen.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5173, debug=True)
