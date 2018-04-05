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
    name = Column(String(100))
    start = Column(Integer, default=0)
    stop = Column(Integer)
    unit_type = Column(String(20), default='standard') 
    description = Column(String(100))

    def __repr__(self):
        return self.unit

class Materialclass(Model):
    __tablename__ = "materialclass"
    id = Column(Integer, primary_key=True)
    materialclass = Column(String(1), unique=True, nullable=False)
    name = Column(String(100))
    description = Column(String(100))

    def __repr__(self):
        return self.materialclass 

class Doctype(Model):
    __tablename__ = "doctype"
    id = Column(Integer, primary_key=True)
    doctype = Column(String(3), unique=True, nullable=False)
    name = Column(String(100))
    description = Column(String(100))
    
    def __repr__(self):
        return self.doctype

class Partner(Model):
    __tablename__ = "partner"
    id = Column(Integer, primary_key=True)
    partner = Column(String(50), unique=True, nullable=False)
    name = Column(String(100))
    description = Column(String(100))
    common_start = Column(Integer, default=0)
    common_stop = Column(Integer, default=0)
    
    def __repr__(self):
        return self.partner


class Documentclass(Model):
    __tablename__ = "documentclass"
    id = Column(Integer, primary_key=True)
    documentclass = Column(String(1), unique=True, nullable=False)
    name = Column(String(100))
    description = Column(String(100))

    def __repr__(self):
        return self.documentclass


class Cdrlitem(Model):
    __tablename__ = "cdrlitem"
    id = Column(Integer, primary_key=True)
    cdrlitem = Column(String(35), unique=True, nullable=False)
    name = Column(String(100))
    description = Column(String(100))

    def __repr__(self):
        return self.cdrlitem


class Vendor(Model):
    __tablename__ = "vendor"
    id = Column(Integer, primary_key=True)
    vendor = Column(String(50), unique=True, nullable=False)
    name = Column(String(100))
    description = Column(String(100))

    def __repr__(self):
        return self.vendor


class Mr(Model):
    __tablename__ = "mr"
    id = Column(Integer, primary_key=True)
    mr = Column(String(50), unique=True, nullable=False)
    name = Column(String(100))
    description = Column(String(100))

    def __repr__(self):
        return self.mr


class Matrix(Model):
    __tablename__ = "matrix"
    id = Column(Integer, primary_key=True)
    matrix = Column(String(50))
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
        doc_param = "-".join([str(x) for x in [self.unit, self.materialclass, self.doctype]])

        return '[ '+ str(self.quantity) +' ] '+ doc_param + ' by ' + str(self.created_by) +' on ' + str(self.created())

    # def __init__(self):
    def csv(self):
        return Markup('<a href="/static/csv/bapco_request_'+ str(self.id) +'.xlsx" download>'+'<img border="0" src="/static/img/excel.png" alt="W3Schools" width="24" height="24">'+'</a>')
        
    def created(self):
        date = self.created_on
        return date.strftime('We are the %d, %b %Y')
        return self.created_on.strftime('%d, %b %Y - %H:%M:%S')

    def modified(self):
        date = self.created_on
        #return date.strftime('We are the %d, %b %Y')
        return self.changed_on.strftime('%d, %b %Y - %H:%M:%S')
    
    def req_type(self):
        
        if self.request_type == 'vendor':
            return Markup('<img border="0" src="/static/img/vendor.png" alt="W3Schools" width="24" height="24"> ' + self.request_type[0:3])
            
        elif self.request_type == 'engineering':
            return Markup('<img border="0" src="/static/img/engineering.png" alt="W3Schools" width="24" height="24"> ' + self.request_type[0:3])
            
        else:
            return '#ND'
        
    
    def req_description(self):
        req_code = str(self.unit) + ' '+ str(self.materialclass.materialclass) + ' '+  str(self.doctype)
        req_quantity = str(self.quantity)
        desc_eng = 'Request by ' +'<strong>'+ str(self.created_by) +'</strong>' + ' for '+'<span style="color:#f89406">[ ' +'</span><strong>'+ req_quantity +'</strong>'+ '<span style="color:#f89406">'+ ' ] </span>' + '</span></strong>'+ req_code
        desc_vend = 'Request by ' +'<strong>'+ str(self.created_by) +'</strong>' + ' for '+'<span style="color:#f89406">[ ' +'</span><strong>'+ req_quantity +'</strong>'+ '<span style="color:#f89406">'+ ' ] </span>' + '</span></strong>'+ req_code  + ' | <span style="color:#5bc0de">'+ str(self.vendor)+'</span> -> '+ str(self.mr)+' |'
        
        if self.request_type == 'vendor':
            return Markup(desc_vend)
            #return 'description1'
        return Markup(desc_eng)
    
    
class Document(AuditMixin, Model):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    code = Column(String(35))
    oldcode = Column(String(35), default='empty')
    docrequests_id = Column(Integer, ForeignKey('docrequests.id'))
    docrequests = relationship(DocRequests)
    comments = Column(String(150))
    notes = Column(String(150))
    status = Column(String(30))

    def __repr__(self):
        name = 'some Document name'
        return name

    def status(self):
        if self.oldcode == 'empty':
            return Markup('<img border="0" src="/static/img/pending.png" alt="W3Schools" width="16" height="16">'+' P')
        elif self.oldcode == 'void':
            return Markup('<img border="0" src="/static/img/destroyed.png" alt="W3Schools" width="16" height="16">'+' D')
        else:
            return Markup('<img border="0" src="/static/img/reserved.png" alt="W3Schools" width="16" height="16">'+' R')

    def code_type(self):
        return self.docrequests.req_type()

    def created(self):
        #date = self.created_on
        #return date.strftime('We are the %d, %b %Y')
        return self.created_on.strftime('%d, %b %Y - %H:%M:%S')
    
    def modified(self):
        #date = self.created_on
        #return date.strftime('We are the %d, %b %Y')
        return self.changed_on.strftime('%d, %b %Y - %H:%M:%S')
    
    def bapco_code(self):
        if self.oldcode == 'empty':
            return Markup('<span style="color:#f89406">[ '+'<span style="color:white">'+ self.code + '<span style="color:#f89406"> ]')
        
        elif self.oldcode == 'void':
            return Markup('<span style="color:#ee5f5b">[ '+'<span style="color:white">'+ self.code + '<span style="color:#ee5f5b"> ]')

        else:
            return Markup('<span style="color:#5bc0de">[ '+'<span style="color:white">'+ self.code + '<span style="color:#5bc0de"> ]') 


class Comments(Model):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    code = Column(String(35))
    notes = Column(String(35))
    rel = Column(String(30))
    rel2 = Column(String(30))

