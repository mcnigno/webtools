from flask import render_template, flash, redirect, url_for
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import (ModelView, CompactCRUDMixin, MasterDetailView,
                              MultipleView, GroupByChartView, IndexView)
from app import appbuilder, db
from .models import (DocRequests, Unit, Materialclass, Doctype,
                     Partner, Matrix, Document, Cdrlitem, Documentclass,
                     Vendor, Mr)
from flask_appbuilder.fieldwidgets import Select2AJAXWidget
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.widgets import ListThumbnail, ListBlock
from flask_appbuilder.models.sqla.filters import (FilterStartsWith,
                                                  FilterEqualFunction,
                                                  FilterInFunction,
                                                  FilterEqual,
                                                  FilterNotStartsWith, FilterEqual
                                                  )
from flask import g, send_file
from flask_babel import gettext
from flask_appbuilder import BaseView, expose, has_access

from wtforms.validators import DataRequired, InputRequired
from .helpers import adddoc3, bapco, tocsv, toxlsx, codes_to_xlsx, update_from_xlsx
import csv
from app import app
from flask_appbuilder.actions import action
from flask_appbuilder import filemanager
from flask import request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
import os

ALLOWED_EXTENSIONS = set(['xlsx'])



def get_user():
    return g.user

class CsvView(BaseView):
    
    @has_access
    @expose('/getcsv/<string:filename>')
    def send_csv(filename):
        print('SEND CSV')
        return send_file(filename) 


def choice_unit(self,item):
    print('CHOICE UNIT')
    
    result = db.session.query(Unit).filter(Unit.unit == '000').first()
    #result = db.session.query(q)
    print('before printing result')
    print(result.name)
    print('lunghezza di result unit:')
    return self, item


def matrixenc(self, item):

    print('matix ENC')
    adddoc2(self, item)

'''
def adddoc2(self, item):
    print('adddoc 2 +++++')
    print('doctype, sheet', item.doctype.doctype, item.sheet)
    session = db.session
    matrix = session.query(Matrix)
    if item.unit.unit == '000':
        item_matrix = str.join('-', (item.unit.unit,
                                     item.materialclass.materialclass,
                                     item.doctype.doctype,
                                     # item.sheet,
                                     item.partner.partner))
    else:
        item_matrix = str.join('-', (item.unit.unit,
                                     item.materialclass.materialclass,
                                     item.doctype.doctype,
                                     # item.sheet,
                                     ))

    item_serial = str.join('-', (item.unit.unit,
                                 item.materialclass.materialclass,
                                 item.doctype.doctype,
                                 # item.sheet,
                                 ))

    print('controllo item_ matrix', item_matrix)
    found = False
    for row in matrix:
        print('loop controllo matrix uguali',
              row.matrix, item_matrix,
              item.matrix)
        if row.matrix == item_matrix:
            print('trovate matrix uguali')
            print('row counter prima:', row.counter)
            row.counter += 1
            print('row counter dopo:', row.counter)
            datamodel = SQLAInterface(Matrix, session=session)
            datamodel.edit(row)

            item.matrix_id = row.id
            code = item_serial + "-" + str(row.counter).zfill(5) + "-" + item.sheet

            datamodel = SQLAInterface(Document, session=session)
            doc = Document(docrequests_id=item.id, code=code)
            datamodel.add(doc)

            message = 'Your code is ' + code
            flash(message, category='info')
            found = True
    
    # Matrix Not Found
    if found is False:
        print('Matrix NOT FOUND')

        if str(item.unit) == '000':
            print('found unit 000')
            jv = {
                    'TTSJV': 50000,
                    'TPIT': 60000
                }

            # Add New Matrix
            datamodel = SQLAInterface(Matrix, session=session)

            print('counter', jv['TTSJV'], item.partner, jv[str(item.partner)])
            print('item matrix:', item_matrix)

            matrix = Matrix(counter=jv[str(item.partner)] + 1,
                            matrix=item_matrix)

            print('-----2------')

            datamodel.add(matrix)

            # Add New Doc with quantity jv + 1
            datamodel = SQLAInterface(Document, session=session)
            code = item_serial + "-" + str(jv[str(item.partner)] + 1).zfill(5) + "-" + item.sheet
            doc = Document(docrequests_id=item.id, code=code)

            datamodel.add(doc)
            message = 'Your code is ' + code
            flash(message, category='info')

        else:
            # Add New Matrix
            datamodel = SQLAInterface(Matrix, session=session)
            print('item matrix:', item_matrix)

            print('item matrix after:', item_matrix)
            matrix = Matrix(matrix=item_matrix)
            datamodel.add(matrix)

            # Add New Doc with quantity 1
            datamodel = SQLAInterface(Document, session=session)
            code = item_serial + "-" + "1".zfill(5) + "-" + item.sheet
            doc = Document(docrequests_id=item.id, code=code)

            datamodel.add(doc)
            message = 'Your code is ' + code
            flash(message, category='info')

    db.session.flush()




def get_pending():
    return 'reserved'
'''


class PendingView(ModelView):
    datamodel = SQLAInterface(Document)
    list_title = 'Pending Codes'
    
    base_order = ('id', 'desc')
    base_filters = [['oldcode', FilterStartsWith, 'empty'],
                    ['created_by', FilterEqualFunction, get_user]]

    edit_title = 'Edit Code'
    show_title = 'Show Code'
    
    list_columns = ['id', 'created_by', 'status', 'oldcode', 'code']
    edit_columns = ['oldcode']
    
    label_columns = {
        'id': 'ID',
        'status': 'Status',
        'oldcode': 'Contractor Code',
        'code': 'Bapco Code',
    }
    


class DocumentView(CompactCRUDMixin, ModelView):
    datamodel = SQLAInterface(Document)
    list_title = 'All Bapco Codes'
    
    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user]]

    edit_title = 'Edit Code'
    show_title = 'Show Code'

    list_columns = ['id', 'created_by', 'status', 'oldcode', 'code']
    edit_columns = ['oldcode']
    
    label_columns = {
        'id': 'ID',
        'status': 'Status',
        'oldcode': 'Contractor Code',
        'code': 'Bapco Code',
    }
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
    
    @action("export", "Export", "Export all Really?", "fa-rocket")
    def export(self, items):
        if isinstance(items, list):
            codes_list = []
            for item in items:
                print('item', item.code)
                codes_list.append([item.code])
            filename = codes_to_xlsx(codes_list)
            

            self.update_redirect()
            
        else:
            filename = codes_to_xlsx(items.code)
        
        print(codes_list)
        redirect(self.get_redirect())
        #self.update_redirect()
        return send_file('static/csv/' + filename, as_attachment=True)


# Vendor Form Request
class VendorRequestsView(ModelView):
    datamodel = SQLAInterface(DocRequests)
    default_view = 'list'
    label_columns = {
        'id': 'ID',
        'unit': 'Unit',
        'materialclass': ' Mat Class',
        'doctype': 'Doc Type',
        'cdrlitem': 'CDRL Item',
        'documentclass': 'Doc Class',
        'partner': 'Partner',
        'quantity': 'Doc Qty',
        'request_type': 'Type'
    }

    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user],
                    ['request_type', FilterEqual, 'vendor']
                    ]
    
    validators_columns = {'vendor': [DataRequired(message='NOT Released: Vendor is required')],
                          'mr': [DataRequired(message='NOT Released: MR is required')]
    }
    
    list_title = 'Vendor Code Request'
    add_title = 'Add Vendor Code Request'
    edit_title = 'Edit Vendor Code Request'
    show_title = 'Show Vendor Code Request'
    related_views = [DocumentView, PendingView]
    # list_widget = ListThumbnail
    title = "Bapco Vendor Code Request"
    search_columns = ['created_by']
    
    list_columns = ['id', 'unit', 'materialclass', 'doctype', 'cdrlitem',
                    'documentclass', 'partner', 'quantity', 'vendor', 'mr', 
                    'created_by', 'request_type', 'created_on', 'csv']
    
    edit_columns = ['unit', 'materialclass', 'doctype', 'cdrlitem',
                    'documentclass', 'partner', 'vendor', 'mr', ]

    search_columns = ['unit', 'materialclass', 'doctype', 'cdrlitem',
                      'documentclass', 'partner', 'quantity', 'vendor', 'mr', ]

    add_exclude_columns = ['id', 'matrix']

    add_fieldsets = [
                        (
                            'Number of Codes',
                            {'fields': ['quantity']}
                        ),
                        (
                            'Bapco Code Setting',
                            {'fields': ['unit',
                                        'materialclass',
                                        'doctype',
                                        'cdrlitem',
                                        'documentclass',
                                        'vendor',
                                        'mr',
                                        'partner'], 'expanded':False}
                        ),
                     ]
    show_fieldsets = [
                        (
                            'Number of Bapco Codes',
                            {'fields': ['quantity']}
                        ),
                        (
                            'Bapco Code',
                            {'fields': ['unit',
                                        'materialclass',
                                        'doctype',
                                        'cdrlitem',
                                        'documentclass',
                                        'partner'], 'expanded':True}
                        ),
                     ]

    
    def post_add(self, item):
        choice_unit(self, item)
        session_list = []
        for i in range(0, item.quantity):
            print('****** Vendor Code Released ******')

            code = bapco(self, item)
            session_list.append([code])
            print(code)
            print('SESSION LIST:', session_list)
        toxlsx(self, item, session_list)
        



# Engineering Form Request
class DocRequestsView(ModelView):
    datamodel = SQLAInterface(DocRequests)
    label_columns = {
        'id': 'ID',
        'unit': 'Unit',
        'materialclass': ' Mat Class',
        'doctype': 'Doc Type',
        'cdrlitem': 'CDRL Item',
        'documentclass': 'Doc Class',
        'partner': 'Partner',
        'quantity': 'Doc Qty'

    }
    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user],
                    ['request_type', FilterEqual, 'engineering']
                    ]

    list_title = 'Engineering Code Request'
    add_title = 'Add Engineering Code Request'
    edit_title = 'Edit Engineering Code Request'
    show_title = 'Show Engineering Code Request'
    related_views = [DocumentView, PendingView]
    # list_widget = ListThumbnail
    title = "Bapco Engineering Code Request"
    search_columns = ['created_by']
    
    list_columns = ['id', 'unit', 'materialclass', 'doctype', 'cdrlitem',
                    'documentclass', 'partner', 'quantity', 'created_by',
                    'created_on']
    
    edit_columns = ['unit', 'materialclass', 'doctype', 'cdrlitem',
                    'documentclass', 'partner']

    search_columns = ['unit', 'materialclass', 'doctype', 'cdrlitem',
                      'documentclass', 'partner', 'quantity']

    add_exclude_columns = ['id', 'matrix']

    add_fieldsets = [
                        (
                            'Number of Bapco Codes',
                            {'fields': ['quantity']}
                        ),
                        (
                            'Bapco Code Setting',
                            {'fields': ['unit',
                                        'materialclass',
                                        'doctype',
                                        'cdrlitem',
                                        'documentclass',
                                        'partner'], 'expanded':True}
                        ),
                     ]
    show_fieldsets = [
                        (
                            'Number of Bapco Codes',
                            {'fields': ['quantity']}
                        ),
                        (
                            'Bapco Code',
                            {'fields': ['unit',
                                        'materialclass',
                                        'doctype',
                                        'cdrlitem',
                                        'documentclass',
                                        'partner'], 'expanded':True}
                        ),
                     ]
    add_form_extra_fields = {
                    'unit2': AJAXSelectField('unit2',
                                             description='This is by AJAX',
                                             datamodel=datamodel,
                                             col_name='unit',
                                             widget=Select2AJAXWidget(endpoint='/docrequestsview/api/column/add/unit')),
                                            }

    def post_add(self, item):
        choice_unit(self, item)
        session_list = []
        for i in range(0, item.quantity):
            print('****** Engineering Code Released ******')

            code = bapco(self, item)
            session_list.append([code])
            print(code)
            print('SESSION LIST:', session_list)
        toxlsx(self, item, session_list)


class AskBapcoView(MultipleView):
    datamodel = SQLAInterface(DocRequests)
    views = [DocRequestsView, PendingView]
    list_columns = ['id']
    

class UnitView(CompactCRUDMixin, ModelView):
    datamodel = SQLAInterface(Unit)
    list_columns = ['unit', 'unit_type', 'description']
    # list_widget = ListCarousel
    # label_columns = ['unit','description']


class MaterialclassView(ModelView):
    datamodel = SQLAInterface(Materialclass)
    list_columns = ['materialclass', 'description']


class DoctypeView(ModelView):
    datamodel = SQLAInterface(Doctype)
    list_columns = ['doctype', 'description', 'name']


class PartnerView(ModelView):
    datamodel = SQLAInterface(Partner)
    list_columns = ['partner', 'description']
    # list_widget = ListThumbnail


class CdrlitemView(ModelView):
    datamodel = SQLAInterface(Cdrlitem)
    list_columns = ['cdrlitem', 'description']


class DocumentclassView(ModelView):
    datamodel = SQLAInterface(Documentclass)
    list_columns = ['documentclass', 'description']


class VendorView(ModelView):
    datamodel = SQLAInterface(Vendor)
    list_columns = ['vendor', 'description']


class MrView(ModelView):
    datamodel = SQLAInterface(Mr)
    list_columns = ['mr', 'description']


class MatrixView(ModelView):
    datamodel = SQLAInterface(Matrix)
    list_columns = ['id', 'matrix', 'counter']


class GroupMasterView(MasterDetailView):
    datamodel = SQLAInterface(Doctype)
    related_views = [DocRequestsView]


class MultipleViewsExp(MultipleView):
    views = [UnitView, MaterialclassView, DoctypeView, PartnerView]
    list_widget = ListBlock


class EncodChartView(GroupByChartView):
    datamodel = SQLAInterface(DocRequests)
    chart_title = 'Grouped Encod'
    label_columns = UnitView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group': 'unit_id',
            'series': [(aggregate_count, 'unit_id')]
        }
    ]


class ListRequest(ModelView):
    datamodel = SQLAInterface(DocRequests)
    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user]]

    list_title = 'All Requests'
    add_title = 'Add new Request'
    edit_title = 'Modifica Richiesta Codifica'
    show_title = 'Vista Richiesta Codifica'
    related_views = [DocumentView, PendingView]
    # list_widget = ListThumbnail
    title = "Bapco Document ID Generator"
    search_columns = ['created_by']

    list_columns = ['id', 'unit', 'materialclass', 'doctype',
                    'partner', 'quantity', 'created_by', 'created_on', 'request_type']

    edit_columns = ['unit', 'materialclass', 'doctype', 'partner']

    search_columns = ['unit', 'materialclass', 'doctype', 'partner',
                      'quantity']

    add_exclude_columns = ['id', 'matrix']

    add_fieldsets = [
                        (
                            'Numero di Codifiche richiesto',
                            {'fields': ['quantity']}
                        ),
                        (
                            'Bapco Document Setting',
                            {'fields': ['unit',
                                        'materialclass',
                                        'doctype',
                                        'partner'], 'expanded':True}
                        ),
                     ]
    show_fieldsets = [
                        (
                            'Number of Bapco IDs',
                            {'fields': ['quantity']}
                        ),
                        (
                            'Bapco Document',
                            {'fields': ['unit',
                                        'materialclass',
                                        'doctype',
                                        'partner'], 'expanded':True}
                        ),
                     ]

def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Uploadcodes(BaseView):
    default_view = 'upload_form'
    
    @expose('/excel/', methods=['GET', 'POST'])
    @has_access
    def upload_form(self):
        if request.method == 'POST':
            print('we have it! POOOOST', request.files)
            # check if the post request has the file part
            
            if 'file[]' not in request.files:
                flash('No file part')
                print('we have a problem with THE FORM !')
                return redirect(request.url)
            
            
            #file = request.files['file[]']
            files = request.files
            print('file is type of:', type(files))
            if isinstance(files, ImmutableMultiDict):
                print('is an ImmutableMultiDICT ! ****')
                print('WE HAVE FILES !!', files)
                # if user does not select file, browser also
                # submit a empty part without filename
                filename_list = []
                files = dict(files)
                reserved_list = []
                updated_list = []
                for file in files['file[]']:
                    print('type of row', type(file), file)
                    if file.filename == '':
                        flash('No selected file')
                        return redirect(request.url)
                    if file and allowed_file(file.filename):
                        print('IS ALLOWED FILE !!')
                        filename = secure_filename(file.filename)
                        filename_list.append(filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        res_list, upd_list = update_from_xlsx(file)
                        reserved_list += res_list
                        updated_list += upd_list
                        
                return self.render_template('upload.html',
                                            filename=filename_list,
                                            updated_list=updated_list,
                                            count_updated=len(updated_list),
                                            reserved_list=reserved_list,
                                            count_reserved=len(reserved_list))
            
        return self.render_template('upload.html')


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template,
                           appbuilder=appbuilder), 404


db.create_all()

# Risorse Bapco
appbuilder.add_view(AskBapcoView, "Richiesta Codifica",
                    icon="fa-paper-plane", category="Ask Bapco",
                    category_icon='fa-bold')
appbuilder.add_view(Uploadcodes, "Update from XLSX",
                    icon="fa-paper-plane", category="Ask Bapco",
                    category_icon='fa-bold')
#appbuilder.add_view_no_menu(DocRequestsView)
appbuilder.add_view(DocRequestsView, "Engineering Code Request",
                    icon="fa-paper-plane", category="Ask Bapco",
                    category_icon='fa-bold')

appbuilder.add_view(VendorRequestsView, "Vendor Code Request",
                    icon="fa-paper-plane", category="Ask Bapco",
                    category_icon='fa-bold')

appbuilder.add_view(ListRequest, "Elenco Richieste",
                    icon="fa-codepen", category="Ask Bapco")

appbuilder.add_separator(category='Ask Bapco')
appbuilder.add_view(DocumentView, "Elenco Codifiche",
                    icon="fa-list", category="Ask Bapco")

appbuilder.add_view(PendingView, "Elenco Codifiche in Pending",
                    icon="fa-folder-open", category="Ask Bapco",
                    category_icon='fa-bold')

# Bapco Setting

appbuilder.add_view(MultipleViewsExp, "Smart Settings",
                    icon="fa-cogs", category="Bapco Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(UnitView, "Lista Unit",
                    icon="fa-list", category="Bapco Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(MaterialclassView, "Lista Material Class",
                    icon="fa-list", category="Bapco Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(DoctypeView, "Lista DocType",
                    icon="fa-list", category="Bapco Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(PartnerView, "Lista Partner",
                    icon="fa-list", category="Bapco Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(CdrlitemView, "Lista CDRL Item",
                    icon="fa-list", category="Bapco Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(DocumentclassView, "Lista Document Class",
                    icon="fa-list", category="Bapco Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(VendorView, "Lista Vendor",
                    icon="fa-list", category="Bapco Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(MrView, "Lista MR",
                    icon="fa-list", category="Bapco Settings",
                    category_icon='fa-cubes')

# Bapco Backend
appbuilder.add_view(MatrixView, "Matrix View",
                    icon="fa-folder-open-o", category="Bapco Backend",
                    category_icon='fa-bomb')

'''
appbuilder.add_view(GroupMasterView, "GroupMasterView ",
                    icon="fa-folder-open-o", category="Ask Bapco",
                    category_icon='fa-envelope')
appbuilder.add_view(EncodChartView, "EncodChartView ",
                    icon="fa-folder-open-o", category="Bapco Resources",
                    category_icon='fa-envelope')

'''