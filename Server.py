from flask import Flask, jsonify, send_file, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# PostgreSQL database configuration
DB_USERNAME = "postgres"
DB_PASSWORD = "sherlock221"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "postgres"

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

class AgriculturalLand(db.Model):
    __tablename__ = 'agriculturalland'
    landid = db.Column(db.Integer, primary_key=True)
    citizenid = db.Column(db.Integer, db.ForeignKey('citizens.citizenid', ondelete='CASCADE'), nullable=False)
    area = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=False)

class CultivationRecord(db.Model):
    __tablename__ = 'cultivationrecord'
    cultivationid = db.Column(db.Integer, primary_key=True)
    landid = db.Column(db.Integer, db.ForeignKey('agriculturalland.landid', ondelete='CASCADE') , nullable=False)
    year = db.Column(db.Integer, nullable=False)
    citizenid = db.Column(db.Integer, db.ForeignKey('citizens.citizenid', ondelete='CASCADE'), nullable=False)
    season = db.Column(db.String(50), nullable=False)
    croptype = db.Column(db.String(100), nullable=False)
    cultivatedarea = db.Column(db.Float, nullable=False)
    productionquantity = db.Column(db.Float)


class Asset(db.Model):
    __tablename__ = 'assets'
    assetid = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    # assetid = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    installationdate = db.Column(db.Date, nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    lastmaintenancedate = db.Column(db.Date)
    
class ServiceRequest(db.Model):
    __tablename__ = 'servicerequests'
    requestid = db.Column(db.Integer, primary_key=True)
    citizenid = db.Column(db.Integer, db.ForeignKey('citizens.citizenid', ondelete='CASCADE'), nullable=False)
    requesttype = db.Column(db.String(50), nullable=False)
    requestdate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    citizen = db.relationship("Citizen", backref="requests")

    
    
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

    return send_file("Schemes_employee.html" if employee else "Schemes_citizen.html")

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

@app.route('/schemes/getpendingschemes')
def getpendingscheme():
    schemes = []
    pending_schemes = (
            db.session.query(Scheme, Schemeapp.remarks,Schemeapp.citizenid,Schemeapp.applicationid)
            .join(Schemeapp, Scheme.schemeid == Schemeapp.schemeid)
            .filter(Schemeapp.status == False)
            .all()
        )
    for scheme,remarks, citizenid,applicationid in pending_schemes:
            schemes.append({
                "schemeid": scheme.schemeid,
                "applicationid": applicationid,
                "SchemeName": scheme.schemename,
                "Description": scheme.description,
                "EligibilityCriteria": scheme.eligibilitycriteria,
                "Benefits": scheme.benefits,
                "Department": scheme.department,
                "ValidTill": scheme.validtill.strftime('%Y-%m-%d'),
                "citizenid": citizenid,
                "remarks": remarks
            })
    return jsonify(schemes)
    

@app.route('/applyschemes', methods=['POST'])
def apply_schemes():
    data = request.json
    userid = request.args.get('id', type=int)
    is_user = request.args.get('user', default="false").lower() == "true"

    if not userid:
        return jsonify({"error": "User ID is required"}), 400

    if not data or 'schemeids' not in data:
        return jsonify({"error": "Scheme IDs are required"}), 400

    scheme_ids = data["schemeids"]
    applied_schemes = []

    if is_user:  
        # Case when it's a citizen applying for schemes
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
    else:
        # Case when it's an admin or non-user updating the scheme table
        for app in scheme_ids:
            applicationid = app["applicationid"]
            remarks = app["remarks"]
            status = app["status"]

            scheme_app = Schemeapp.query.filter_by(applicationid=applicationid).first()
            if scheme_app:
                scheme_app.remarks = remarks
                scheme_app.status = status
            else:
                applied_schemes.append({"applicationid": applicationid, "message": "Application Not Found"})

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

@app.route('/farmland', methods=['GET'])
def get_farmlands():
    """Fetch all farmland owned by a user."""
    userid = request.args.get('userid', type=int)
    if not userid:
        return jsonify({"error": "User ID is required"}), 400

    lands = AgriculturalLand.query.filter_by(citizenid=userid).all()
    return jsonify([{
        "landid": land.landid,
        "Area": land.area,
        "Address": land.address
    } for land in lands])

@app.route('/cultivationrecords', methods=['GET'])
def get_cultivation_records():
    """Fetch all cultivation records for the user's farmlands."""
    userid = request.args.get('userid', type=int)
    if not userid:
        return jsonify({"error": "User ID is required"}), 400

    records = db.session.query(CultivationRecord).join(AgriculturalLand).filter(AgriculturalLand.citizenid == userid).all()
    return jsonify([{
        "cultivationid": record.cultivationid,
        "landid": record.landid,
        "year": record.year,
        "season": record.season,
        "croptype": record.croptype,
        "cultivatedarea": record.cultivatedarea,
        "productionquantity": record.productionquantity
    } for record in records])

@app.route('/addcultivation', methods=['POST'])
def add_cultivation():
    """Add a cultivation record."""
    data = request.json
    required_fields = ["landid", "year", "season", "croptype", "cultivatedarea", "productionquantity", "citizenid"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    new_record = CultivationRecord(
        landid=data['landid'],
        year=data['year'],
        season=data['season'],
        croptype=data['croptype'],
        cultivatedarea=data['cultivatedarea'],
        productionquantity=data['productionquantity'],
        citizenid=data['citizenid']
    )

    db.session.add(new_record)
    db.session.commit()

    return jsonify({"message": "Cultivation record added successfully!"}), 201

# Employee - Resources

@app.route('/resources')
def resources_page():
    d = request.args.get('id', type=int)
    employee = Employee.query.filter_by(citizenid = d).first()
    if not employee:
        return "User not found", 404
    return send_file('Resources_employee.html')

@app.route('/api/resources', methods=['GET'])
def get_resources():
    resources = Asset.query.all()
    return jsonify([{
        'id': resource.assetid,
        'type': resource.type,
        'location': resource.location,
        'installationdate': resource.installationdate.strftime('%Y-%m-%d'),
        'condition': resource.condition,
        'lastmaintenancedate': resource.lastmaintenancedate.strftime('%Y-%m-%d') if resource.lastmaintenancedate else 'N/A'
    } for resource in resources])

@app.route('/api/resources', methods=['POST'])
def add_resource():
    data = request.json
    new_resource = Asset(
        type=data['type'],
        location=data['location'],
        installationdate=datetime.strptime(data['installationdate'], '%Y-%m-%d'),
        condition=data['condition'],
        lastmaintenancedate=datetime.strptime(data['lastmaintenancedate'], '%Y-%m-%d') if data.get('lastmaintenancedate') else None
    )
    db.session.add(new_resource)
    db.session.commit()
    return jsonify({'message': 'Resource added successfully'}), 201

@app.route('/api/resources/<int:assetid>', methods=['DELETE'])
def delete_resource(assetid):
    resource = Asset.query.get(assetid)
    if resource:
        db.session.delete(resource)
        db.session.commit()
        return jsonify({'message': 'Resource deleted successfully'}), 200
    return jsonify({'error': 'Resource not found'}), 404

#Citizen - Service Requests

#Employee - Service Requests

@app.route('/servicerequests')
def servicerequests_page():
    d = request.args.get('id', type=int)
    employee = Employee.query.filter_by(citizenid = d).first()
    if not employee:
        return "User not found", 404
    return send_file('Services_employee.html')

@app.route('/api/servicerequests', methods=['GET'])
def get_service_requests():
    requests = db.session.query(
        ServiceRequest.requestid,
        Citizen.fullname.label('citizenname'),
        ServiceRequest.requesttype,
        ServiceRequest.requestdate,
        ServiceRequest.status
    ).join(Citizen, ServiceRequest.citizenid == Citizen.citizenid).filter(ServiceRequest.status == "Pending").order_by(ServiceRequest.requestdate.asc()).all()
    return jsonify([
        {
            'requestid': req.requestid,
            'citizenname': req.citizenname,
            'requesttype': req.requesttype,
            'requestdate': req.requestdate.strftime('%Y-%m-%d'),
            'status': req.status
        }
        for req in requests
    ])

@app.route('/api/servicerequests/<int:requestid>', methods=['PUT'])
def update_service_request(requestid):
    data = request.json
    new_status = data.get('status')

    if new_status not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400

    request_entry = ServiceRequest.query.get(requestid)
    if not request_entry:
        return jsonify({'error': 'Request not found'}), 404

    request_entry.status = new_status.capitalize()
    print(request_entry.status)
    db.session.commit()

    return jsonify({'message': f'Service request {new_status} successfully'}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5173, debug=True)
