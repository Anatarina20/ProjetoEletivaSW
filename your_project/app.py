from flask import Flask, render_template, jsonify
from flask_jwt import JWT, jwt_required
from datetime import datetime, timedelta
from model import employees, user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'ssys'

CSS_STYLE = """
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 0;
}

.header {
    background-color: #333;
    color: white;
    padding: 10px;
    text-align: center;
}

.container {
    max-width: 800px;
    margin: 20px auto;
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.form-group {
    margin-bottom: 15px;
}

.btn {
    background-color: #007bff;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 3px;
    cursor: pointer;
}

.btn:hover {
    background-color: #0056b3;
}
"""

@app.route('/', methods=['GET'])
def home():
    css_style = '<style>{}</style>'.format(CSS_STYLE)
    return render_template("index.html", css_style=css_style)

def authenticate(username,password):
    auth_user = user.UserModel.find_by_name(username)
    dict_error = {'erro':'Usuário ou senha inválidos'}
    if auth_user and safe_str_cmp(auth_user.password.encode('utf-8'),password.encode('utf-8')):
        return auth_user
    return auth_user, 401

def identity(payload):
    user_id = payload['user_name']
    return user.UserModel.find_by_name(user_id)

jwt = JWT(app,authenticate,identity)

@jwt.jwt_payload_handler
def make_payload(jwt_identity):
    expiration = datetime.now() + timedelta(hours=10)
    nbf = datetime.now() + timedelta(seconds=1)
    iat = datetime.now()
    return {
        'user_id' : jwt_identity.id,
        'user_name' : jwt_identity.name,
        'iat':iat,
        'exp':expiration,
        'nbf':nbf
    }

@app.before_first_request
def create_tables():
    alchemy.create_all()

@app.route('/', methods=['GET'])
def home():
    return"API SSYS WORKIMG", 200

@app.route("/signup",methods=['POST'])
def signup():
  request_data = request.get_json()
  if (user.UserModel.find_by_name(request_data['username'])):
      return {'message': 'O e-mail informado já esta sendo utilizado'}, 409
  new_user = user.UserModel(name=request_data['username'],password=request_data['password'])
  new_user.save_to_db()
  return new_user.json()

@app.route('/employees/', methods=['GET'])
@jwt_required()
def get_all_employee():
    "Retorna todos os employee"
    result = employees.Employee.query.all()
    items = []
    for item in result:
        items.append(item.json())
    if items:
        return jsonify(items)
    else:
        return {'message': 'Employees not found'}, 404

@app.route('/employees/', methods=['POST'])
@jwt_required()
def create_employee():
    "Cria um employee"
    request_data = request.get_json()
    new_employee = employees.Employee(request_data['name'],
                                      request_data['email'],
                                      request_data['department'],
                                      request_data['salary'],
                                      request_data['birth_date']
                                      )

    new_employee.save_to_db()
    result = new_employee.find_by_id(new_employee.id)
    return jsonify(result.json())

@app.route('/employees/<int:id>/')
@jwt_required()
def get_employee(id):
    "Retorna o employee especifico por id"
    result = employees.Employee.find_by_id(id)
    if result:
        return result.json()
    else:
        return {'message': 'Employee not found'}, 404

@app.route('/employees/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_employee(id):
    employee_deleted = employees.Employee.find_by_id(id)
    employee_deleted.delete_from_db()
    return {'message':'Excluído com sucesso'}, 202

@app.route('/employees/<int:id>/', methods=['PUT'])
@jwt_required()
def update_employee(id):
    request_data = request.get_json()
    employee_updated = employees.Employee.find_by_id(id)
    employee_updated.id = id
    employee_updated.name = request_data['name']
    employee_updated.email = request_data['email']
    employee_updated.department = request_data['department']
    employee_updated.salary = request_data['salary']
    employee_updated.birth_date = datetime.strptime(request_data['birth_date'], '%m-%d-%Y')
    employee_updated.update()
    result = employee_updated.find_by_id(id)
    if result:
        return result.json(), 200
    else:
        return {'message': 'Employee not found'}, 404

#reports

@app.route('/reports/employees/salary/', methods=['GET'])
@jwt_required()
def get_report_salary():
    result = employees.Employee.query.all()
    maior = result[0]
    menor = result[0]
    media = 0.00
    qtd = 0

    for item in result:
        qtd = qtd + 1
        media = media + float(item.salary)

        if maior.salary < item.salary:
            maior = item

        if menor.salary > item.salary:
            menor = item

    report = {"lowest": menor.json(),
              "highest": maior.json(),
              "average": media/qtd
              }

    if report:
        return report
    else:
        return {'message': 'Report not found'}, 404


@app.route('/reports/employees/age/', methods=['GET'])
@jwt_required()
def get_report_age():
    result = employees.Employee.query.all()
    younger = result[0]
    older = result[0]
    media = 0.00
    qtd = 0
    now_year = datetime.now().year
    for item in result:
        qtd = qtd + 1
        media = media + (now_year - item.birth_date.year)

        if younger.birth_date < item.birth_date:
            younger = item

        if older.birth_date > item.birth_date:
            older = item

    report = {"younger": younger.json(),
              "older": older.json(),
              "average": media/qtd
              }

    if report:
        return report
    else:
        return {'message': 'Report not found'}, 404

if __name__ == '__main__':
    from data import alchemy
    alchemy.init_app(app)
    app.run(port=8000, debug=True)


