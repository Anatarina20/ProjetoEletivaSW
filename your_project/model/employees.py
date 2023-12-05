from datetime import datetime
from data import alchemy

class Employee(alchemy.Model):
    __tablename__ = 'employee'

    id = alchemy.Column(alchemy.Integer, primary_key = True)
    name = alchemy.Column(alchemy.String(80))
    email = alchemy.Column(alchemy.String(80))
    department = alchemy.Column(alchemy.String(80))
    salary = alchemy.Column(alchemy.Float(15,2))
    birth_date = alchemy.Column(alchemy.Date)

    def __init__(self, name, email, department, salary, birth_date):
        self.name = name
        self.email = email
        self.department = department
        self.salary = float(salary)
        self.birth_date = datetime.strptime(birth_date, '%m-%d-%Y')

    def json(self):
        return {'id':self.id,
                'name':self.name,
                'email':self.email,
                'department':self.department,
                'salary': str(round(self.salary, 2)),
                'birth_date': self.birth_date.strftime('%m-%d-%Y')
                }

    def save_to_db(self):
        alchemy.session.add(self)
        alchemy.session.commit()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def delete_from_db(self):
        alchemy.session.delete(self)
        alchemy.session.commit()

    def update(self):
        alchemy.session.commit()
