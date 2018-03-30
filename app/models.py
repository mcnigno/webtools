from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, ForeignKey  
from sqlalchemy.orm import relationship
from time import gmtime, strftime
from flask import Markup

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
    unit = Column(String(3), unique=True, nullable=False)
    name = Column(String(35), nullable=False)
    start = Column(Integer, default=0)
    stop = Column(Integer)
    unit_type = Column(String(20), default='standard') 
    description = Column(String(100))

    def __repr__(self):
        return self.unit

class Materialclass(Model):
    __tablename__ = "materialclass"
    id = Column(Integer, primary_key=True)
    materialclass = Column(String(1))
    name = Column(String(35), nullable=False)
    description = Column(String(100))

    def __repr__(self):
        return self.materialclass

class Doctype(Model):
    __tablename__ = "doctype"
    id = Column(Integer, primary_key=True)
    doctype = Column(String(3))
    name = Column(String(35), nullable=False)
    description = Column(String(100))
    
    def __repr__(self):
        return self.doctype

class Partner(Model):
    __tablename__ = "partner"
    id = Column(Integer, primary_key=True)
    partner = Column(String(20))
    name = Column(String(35), nullable=False)
    description = Column(String(100))
    common_start = Column(Integer, default=0)
    common_stop = Column(Integer, default=0)
    
    def __repr__(self):
        return self.partner


class Documentclass(Model):
    __tablename__ = "documentclass"
    id = Column(Integer, primary_key=True)
    documentclass = Column(String(35), unique=True)
    name = Column(String(35), nullable=False)
    description = Column(String(100))

    def __repr__(self):
        return self.documentclass


class Cdrlitem(Model):
    __tablename__ = "cdrlitem"
    id = Column(Integer, primary_key=True)
    cdrlitem = Column(String(35), unique=True)
    name = Column(String(35), nullable=False)
    description = Column(String(100))

    def __repr__(self):
        return self.cdrlitem


class Vendor(Model):
    __tablename__ = "vendor"
    id = Column(Integer, primary_key=True)
    vendor = Column(String(35), unique=True)
    name = Column(String(35), nullable=False)
    description = Column(String(100))

    def __repr__(self):
        return self.vendor


class Mr(Model):
    __tablename__ = "mr"
    id = Column(Integer, primary_key=True)
    mr = Column(String(35), unique=True)
    name = Column(String(35), nullable=False)
    description = Column(String(100))

    def __repr__(self):
        return self.mr


class Matrix(Model):
    __tablename__ = "matrix"
    id = Column(Integer, primary_key=True)
    matrix = Column(String(20))
    counter = Column(Integer, default=1)
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship('Document')
    
    def __repr__(self):
        return self.matrix


class DocRequests(AuditMixin, Model):
    __tablename__ = "docrequests"
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('unit.id'), nullable=False)
    unit = relationship('Unit')
    materialclass_id = Column(Integer, ForeignKey('materialclass.id'), nullable=False)
    materialclass = relationship('Materialclass')
    doctype_id = Column(Integer, ForeignKey('doctype.id'), nullable=False)
    doctype = relationship('Doctype')
    sheet = Column(String(3), default='001')
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    partner = relationship('Partner')
    cdrlitem_id = Column(Integer, ForeignKey('cdrlitem.id'))
    cdrlitem = relationship('Cdrlitem')
    documentclass_id = Column(Integer, ForeignKey('documentclass.id'))
    documentclass = relationship('Documentclass')
    vendor_id = Column(Integer, ForeignKey('vendor.id'))
    vendor = relationship('Vendor')
    mr_id = Column(Integer, ForeignKey('mr.id'))
    mr = relationship('Mr')
    matrix_id = Column(Integer, ForeignKey('matrix.id'))
    matrix = relationship('Matrix')
    quantity = Column(Integer, default=1)
    request_type = Column(String(20))
    

    def __repr__(self):
        name = str(self.unit) + str(self.materialclass) + str(self.doctype)
        return name
    
    # def __init__(self):
    def csv(self):
        return Markup('<a href="/static/csv/bapco_request_'+ str(self.id) +'.xlsx" download>'+'<img border="0" src="/static/img/excel.png" alt="W3Schools" width="24" height="24">'+'</a>')
    

    
    
    
    
class Document(AuditMixin, Model):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    code = Column(String(35))
    oldcode = Column(String(35), default='empty')
    docrequests_id = Column(Integer, ForeignKey('docrequests.id'))
    docrequests = relationship(DocRequests)

    def __repr__(self):
        name = 'some Document name'
        return name

    def status(self):
        if self.oldcode != 'empty':
            return Markup('<img border="0" src="/static/img/reserved.png" alt="W3Schools" width="16" height="16">'+' Reserved')
        return Markup('<img border="0" src="/static/img/pending.png" alt="W3Schools" width="16" height="16">'+' Pending')
