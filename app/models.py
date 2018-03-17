from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin, FileColumn, ImageColumn
from sqlalchemy import Column, Integer, String, ForeignKey  
from sqlalchemy.orm import relationship

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
def mydefault():
    print('by mydefaul function')
    return 'func'

class Unit(Model):
    __tablename__ = "unit"
    id = Column(Integer, primary_key=True)
    unit = Column(String(3))
    description = Column(String(100))

    def __repr__(self):
        return self.unit

class Materialclass(Model):
    __tablename__ = "materialclass"
    id = Column(Integer, primary_key=True)
    materialclass = Column(String(1))
    description = Column(String(100))

    def __repr__(self):
        return self.materialclass

class Doctype(Model):
    __tablename__ = "doctype"
    id = Column(Integer, primary_key=True)
    doctype = Column(String(3))
    description = Column(String(100))
    
    def __repr__(self):
        return self.doctype

class Partner(Model):
    __tablename__ = "partner"
    id = Column(Integer, primary_key=True)
    partner = Column(String(20))
    description = Column(String(100))
    
    def __repr__(self):
        return self.partner


class Matrix(Model):
    __tablename__ = "matrix"
    id = Column(Integer, primary_key=True)
    matrix = Column(String(20))
    counter = Column(Integer)
    #encodings_id = Column(Integer, ForeignKey("encodings.id"), nullable=False)
    #encodings = relationship('Encodings')
    
    def __repr__(self):
        return self.matrix


class Encodings(Model):
    __tablename__ = "encodings"
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('unit.id'), nullable=False)
    unit = relationship('Unit')
    materialclass_id = Column(Integer, ForeignKey('materialclass.id'), nullable=False)
    materialclass = relationship('Materialclass')
    doctype_id = Column(Integer, ForeignKey('doctype.id'), nullable=False)
    doctype = relationship('Doctype')
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    partner = relationship('Partner')
    matrix_id = Column(Integer, ForeignKey('matrix.id'))
    #matrix_id = Column(String(20), ForeignKey('matrix.matrix'), nullable=False)
    matrix = relationship('Matrix')
    matrix_r = Column(String(35))
    serial = Column(String(35))
    sheet = Column(String(3))
    #sheet = Column(Integer, default=mydefault, onupdate=mydefault)

    def __repr__(self):
        name = self.unit + self.materialclass + self.doctype + self.serial
        return name
    
    def __init__(self):
        print('this is the UNIT code:', self.unit)
        self.serial = mydefault()
