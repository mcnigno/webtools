from flask import render_template, request, flash
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, BaseView, expose, has_access
from app import appbuilder, db
from .models import Encodings, Unit, Materialclass, Doctype, Partner, Matrix
#from app import bapco2 as bapco
from wtforms import Form, StringField, SelectField
#from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget, Select2Widget, Select2AJAXWidget
from flask_appbuilder.forms import DynamicForm, FlaskForm
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder import SimpleFormView
from flask_babel import lazy_gettext as _
from sqlalchemy.orm import relationship

def choice_unit():
    return db.session.query(Unit)
    
def matrixenc(self, item):
    
    print('matix ENC')
    
    item_matrix = str.join('-', (item.unit.unit, item.materialclass.materialclass, item.doctype.doctype, item.partner.partner))
    item_serial = str.join('-', (item.unit.unit, item.materialclass.materialclass, item.doctype.doctype))    
    m = self.datamodel.query_model_relation('matrix')
    #item.matrix = Matrix(matrix=item_matrix)
    print('numero di matrix nella lista:',len(m))
    print('item.matrix:', item.matrix)
    #item_matrix = str(item.matrix)
    found = False
    for i in m:
        print('i.matrix:', i.matrix, item_matrix, len(item_matrix))
        if i.matrix == item_matrix:
            print('sono uguali')
            print(i, i.id)
            i.counter += 1
            id_matrix = i.id
            print('id di matrix', id_matrix)
            self.datamodel.edit(i)
            item.matrix_id = id_matrix
            item.serial = item_serial + "-" + str(i.counter).zfill(5)
            self.datamodel.edit(item)
            message = 'Your code is ' + item.serial
            flash(message, category='info')
            print(found)
            found = True
            print(found)
    if found == False:
        print('notFound !!!! !!!! !!!')
        if str(item.unit) == '000':
            print('found unit 000')
            jv = {
                    'TTSJV': 50000,
                    'TPIT': 60000
                }
            print('counter', jv['TTSJV'], item.partner, jv[str(item.partner)])
            item.matrix = Matrix(counter=jv[str(item.partner)] + 1, matrix=item_matrix)
            print('------------')
            item.serial = item_serial + "-" + str(jv[str(item.partner)] + 1).zfill(5)
            print('-----2------')
            self.datamodel.add(item)
            
        else:
            item.matrix = Matrix(counter=1, matrix=item_matrix)
            item.serial = item_serial + "-" + "1".zfill(5)
            self.datamodel.add(item)
            


    
    #print('elementi filtrati')
    #u = self.datamodel.query_model_relation('unit')
    #print('elementi filtrati len:', len(u))
    return self, item

class BapcoForm(DynamicForm):
    datamodel = SQLAInterface(Unit)
    #units = datamodel.query_model_relation('unit')
    #print(units)
    #hoices=relationship('Unit')
    
    
    unit = SelectField(
        ('Unit'),
        coerce=int,
        choices=[(1,'001')]
        #
    )
    materialclass = StringField(
        ('Material Class'),
        description=('Select the Material Class code '),
        validators= [DataRequired()], 
        widget=BS3TextFieldWidget()
    )
    doctype = StringField(
        ('Document Type'),
        description=('Select the Document Type code '),
        validators= [DataRequired()], 
        widget=BS3TextFieldWidget()
    )
    partner = StringField(
        ('JV Partner'),
        description=('Select the JV\'s Partner source '),
        validators= [DataRequired()], 
        widget=BS3TextFieldWidget()
    )

class BapcoFormView(SimpleFormView):
    form = BapcoForm
    
    form_title = 'Bapco Document ID Request'
    message = 'The request has been submitted to Quasar DCC'
    
    datamodel = SQLAInterface(Unit)

    add_form_extra_fields = {
                    'other_unit': AJAXSelectField('unit',
                    description='This will be populated with AJAX',
                    datamodel=datamodel,
                    col_name='unit',
                    widget=Select2AJAXWidget(endpoint='/unitview/api/column/add/unit')),
    
    }

    def form_get(self, form):
        form.unit.data = '000'
    
    def form_post(self, form):
        flash(self.message, 'info')
"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""

"""
    Application wide 404 error handler
"""
def add_encod(self, unit, materialclass, docType, jv_partner):
    #self.datamodel = SQLAInterface(Encodings)
    new = Encodings()
    encodlist = self.datamodel.query()
    print('this is the endo list:', encodlist)
    new.unit = Unit(unit=unit)
    new.materialclass = Materialclass(materialclass=materialclass)
    new.doctype = Doctype(doctype=docType)
    new.partner = Partner(partner=jv_partner)
    matrix = str.join('', (unit, materialclass, docType))
    #session = db.session()
    m = self.datamodel.query_model_relation('matrix')
    #self.datamodel.add(m)
    #session.commit()
    if m:
        found = False
        for row in m:
            if row.matrix == matrix:
                matrix_id = row.id
                row.counter += 1
                self.datamodel.edit(row)
                found = True
                print('edited')
                print(row.matrix)
            
        
        if found:
            print('founded and addedd increment')
        else:
            print('added new')
            #new.matrix = Matrix(matrix=matrix, counter= ++1)
            #self.datamodel.add(new)

            
        print(len(m),'is the len')
    else:
        print('m is False')
        print('added new')

        #new.matrix = Matrix(matrix=matrix, counter= ++1)

    new.matrix = Matrix(matrix=matrix, counter=1)
    self.datamodel.add(new)
    return self
    #add_counter(unit,materialClass,docType,jv_partner)
    
'''
def add_counter(self, unit, materialClass, docType, jv_partner):    
    #datamodel = SQLAInterface(Matrix)
    key = str.join('', (unit, materialClass, docType))
    query = Matrix()
    query.code = key
    matrix = self.datamatrix.query()
    print(matrix)
'''

class Askbapco(BaseView):
    default_view = 'home'
    @expose('/askbapco/')
    @has_access
    def home(self):
        return self.render_template('askbapco.html')

class Bapcocode(BaseView):
    default_view = 'newcode'
    datamodel = SQLAInterface(Encodings)
    @expose('/newcode/', methods=["POST", "GET"])
    def newcode(self):
        unit = str(request.form['unit'])
        materialclass = str(request.form['materialclass'])
        doctype = str(request.form['doctype'])
        partner = str(request.form['partner'])
        add_encod(self, unit, materialclass, doctype, partner)
        
        
        return self.render_template('newcode.htm', unit=unit, materialclass=materialclass, doctype=doctype, partner=partner)
    

class EncodingView(ModelView):
    datamodel = SQLAInterface(Encodings)
    list_columns = ['serial_u', 'id', 'unit','materialclass','doctype','partner','serial', 'matrix']
    
    
    def pre_add(self, item):
        print('unit, materialclass, doctype: ', item.unit, item.materialclass, item.doctype)
        print('this is PRE ADD FUNCTION -| DOCTYPE before:', item.matrix)
        #item.doctype = Doctype(doctype='LAL')
        #matrix = str.join('', (item.unit.unit, item.materialclass.materialclass, item.doctype.doctype))
        #item.matrix = Matrix(matrix=matrix)
        #item.matrix = Matrix(counter=1)
        #item.matrix.matrix=matrix
        #item.matrix.counter += 2
        print('this is PRE ADD FUNCTION -| DOCTYPE after (LAL):', item.matrix)
        
        '''
        matrix = str.join('', (item.unit.unit, item.materialclass.materialclass, item.doctype.doctype))
        item.matrix = Matrix(matrix=matrix, counter=1)
        #item.matrix.matrix = matrix
        '''
    def post_add(self, item):
        
        matrix = str.join('', (item.unit.unit, item.materialclass.materialclass, item.doctype.doctype))

        #m = Matrix(matrix=matrix, counter= ++1)
        #item.matrix.counter += 1
        #self.datamodel.edit(m)
        #item.matrix.counter += 1
        
        print('this is POST ADD FUNCTION -| DOCTYPE before:', item.matrix)
        #item.doctype = Doctype(doctype='LAL')
        print('this is POST ADD FUNCTION -| DOCTYPE after (LAL):', item.matrix)
        #matrix = str.join('', (item.unit, item.materialclass, item.doctype))
        #print('unit, materialclass, doctype: ', item.unit, item.materialclass, item.doctype)
        #add_encod(self, item.unit.unit, item.materialclass.materialclass, item.doctype.doctype, item.partner.partner)

        '''
        matrix = str.join('', (item.unit.unit, item.materialclass.materialclass, item.doctype.doctype))
        if item.matrix:
            item.matrix.matrix = matrix
            item.matrix.counter += 1
        else:
            item.matrix = Matrix(matrix=matrix, counter=1)
        '''
        
        #item.matrix.counter += 1
        print('*****VVVVVV******')
        matrixenc(self,item)
   
   
    @has_access
    @expose('/encodingview/add', methods=["GET","POST"])
    def add(self):
        rx = request._get_current_object()
        #rx = self.request
        if rx.method == "POST":
            rx.form['serial']
            print('request form unit:', rx.form['unit'], rx.form['materialclass'], rx.form['doctype'])
            print('method POST')
            print(rx,'method POST')
        print('serial U added')
        return super().add()

class UnitView(ModelView):
    datamodel = SQLAInterface(Unit)
    list_columns = ['unit','description']

class MaterialclassView(ModelView):
    datamodel = SQLAInterface(Materialclass)
    list_columns = ['materialclass', 'description']

class DoctypeView(ModelView):
    datamodel = SQLAInterface(Doctype)
    list_columns = ['doctype', 'description']

class PartnerView(ModelView):
    datamodel = SQLAInterface(Partner)
    list_columns = ['partner', 'description']

class MatrixView(ModelView):
    datamodel = SQLAInterface(Matrix)
    list_columns = ['id', 'matrix', 'counter']

@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

db.create_all()
appbuilder.add_view(EncodingView, "Encodings", icon="fa-folder-open-o", category="Bapco Resources", category_icon='fa-envelope')
appbuilder.add_view(UnitView, "Unit", icon="fa-folder-open-o", category="Bapco Resources", category_icon='fa-envelope')
appbuilder.add_view(MaterialclassView, "Material Class", icon="fa-folder-open-o", category="Bapco Resources", category_icon='fa-envelope')
appbuilder.add_view(DoctypeView, "Doc Type", icon="fa-folder-open-o", category="Bapco Resources", category_icon='fa-envelope')
appbuilder.add_view(PartnerView, "Partner", icon="fa-folder-open-o", category="Bapco Resources", category_icon='fa-envelope')
appbuilder.add_view(Askbapco, "Ask Bapco", icon="fa-folder-open-o", category="Bapco Resources", category_icon='fa-envelope')
appbuilder.add_view(MatrixView, "Matrix View", icon="fa-folder-open-o", category="Bapco Resources", category_icon='fa-envelope')
appbuilder.add_view(BapcoFormView, "Bapco Form Request ", icon="fa-folder-open-o", category="Bapco Resources", category_icon='fa-envelope')

appbuilder.add_view_no_menu(Bapcocode)
