from flask import render_template, flash, redirect, url_for
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import (ModelView, CompactCRUDMixin, MasterDetailView,
                              MultipleView, GroupByChartView, IndexView)
from app import appbuilder, db
from .models import (DocRequests, Unit, Materialclass, Doctype,
                     Partner, Matrix, Document, Cdrlitem, Documentclass,
                     Vendor, Mr, Comments)
from flask_appbuilder.fieldwidgets import Select2AJAXWidget
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.models.group import aggregate_count, aggregate_sum
from flask_appbuilder.widgets import ListThumbnail, ListBlock
from flask_appbuilder.models.sqla.filters import (FilterStartsWith,
                                                  FilterEqualFunction,
                                                  FilterInFunction,
                                                  FilterEqual,
                                                  FilterNotStartsWith, FilterEqual
                                                  )
from flask_appbuilder.security.views import UserDBModelView
from flask import g, send_file
from flask_babel import gettext
from flask_appbuilder import BaseView, expose, has_access

from wtforms.validators import DataRequired, InputRequired
from .helpers import adddoc3, bapco, tocsv, toxlsx, codes_to_xlsx, update_from_xlsx, setting_update, old_codes_update, old_codes, gen_excel_byreq
import csv
from app import app
from flask_appbuilder.actions import action
from flask_appbuilder import filemanager
from flask import request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
import os
from flask_appbuilder.security.sqla.models import User
from .momentjs import momentjs
from flask import Markup

ALLOWED_EXTENSIONS = set(['xlsx'])



def get_user():
    return g.user

class CsvView(BaseView):
    
    @has_access
    @expose('/getcsv/<string:reqid>')
    def send_csv(reqid):
        print('SEND CSV')
        return send_file(filename) 

'''
def choice_unit(self,item):
    print('CHOICE UNIT')
    
    result = db.session.query(Unit).filter(Unit.unit == '000').first()
    #result = db.session.query(q)
    print('before printing result')
    print(result.name)
    print('lunghezza di result unit:')
    return self, item
'''

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
    
    base_permissions = ['can_list', 'can_show', 'can_edit'] 

    edit_title = 'Edit Code'
    show_title = 'Show Code'
    
    list_columns = ['code_type', 'bapco_code', 'oldcode_p', 'notes', 'created', 'status']
    edit_columns = ['oldcode', 'notes']
    
    label_columns = {
        'id': 'ID',
        'created': 'Created On',
        'modified': 'Modified On',
        'changed_by': 'Modified By',
        'status': 'Status',
        'oldcode': 'Contractor Code',
        'oldcode_p': 'Contractor Code',
        'code': 'Bapco Code',
        'code_type': 'Type',
    }
    
    @action("export", "Export","", "fa-table")
    def export(self, items):
        if isinstance(items, list):
            print('Export this LIST: ', items)
            codes_list = []
            for item in items:
                print('item', item.code)
                codes_list.append([item.code, item.oldcode])
            filename = codes_to_xlsx(codes_list)

            self.update_redirect()
            
        else:
            print('Export: is a single item', items)
            filename = codes_to_xlsx(items.code)
        
        print('Export: The Codes List populated ', codes_list)
        redirect(self.get_redirect())
        #self.update_redirect()
        return send_file('static/csv/' + filename, as_attachment=True)

class SuperDocumentView(CompactCRUDMixin, ModelView):
    datamodel = SQLAInterface(Document)
    list_title = 'Supervisor | Bapco Codes'
    
    base_order = ('id', 'desc')
    #base_filters = [['created_by', FilterEqualFunction, get_user]]
    base_permissions = ['can_list', 'can_show', 'can_edit', 'can_delete'] 

    edit_title = 'Edit Code'
    show_title = 'Show Code'
    show_exclude_columns = 'docrequests'

    list_columns = ['id', 'code_type', 'bapco_code', 'oldcode_p', 'created_by', 'created', 'status']
    edit_columns = ['oldcode', 'notes']
    
    label_columns = {
        'id': 'ID',
        'created': 'Created On',
        'modified': 'Modified On',
        'changed_by': 'Modified By',
        'status': 'Status',
        'oldcode': 'Contractor Code',
        'oldcode_p': 'Contractor Code',
        'code': 'Bapco Code',
        'code_type': 'Type',
    }
    '''
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())
    '''
    @action("export", "Export", "", "fa-table")
    def export(self, items):
        print('Export from DocumentView')
        if isinstance(items, list):
            codes_list = []
            for item in items:
                print('item', item.code)
                codes_list.append([item.code, item.oldcode])
            filename = codes_to_xlsx(codes_list)
            
            self.update_redirect()
            
        else:
            filename = codes_to_xlsx(items.code)
        
        #print(codes_list)
        #redirect(self.get_redirect())
        self.update_redirect()
        return send_file('static/csv/' + filename, as_attachment=True)

# Engineering Form Request


# Vendor Form Request
class VendorRequestsView(ModelView):
    datamodel = SQLAInterface(DocRequests)
    default_view = 'add'

    
    label_columns = {
        'id': 'ID',
        'unit': 'Unit',
        'materialclass': ' Mat Class',
        'doctype': 'Doc Type',
        'cdrlitem': 'CDRL Item',
        'documentclass': 'Doc Class',
        'partner': 'Partner',
        'quantity': 'Qty',
        'request_type': 'Type',
        'csv': 'XLS',
        'req_type': 'Type',
        'req_description': 'Description',
        'created': 'Created on'
    }
    
    #related_views = [DocumentView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    edit_template = 'appbuilder/general/model/edit_cascade.html'
    
    add_template = 'appbuilder/general/model/add_ven.html'
    
    base_order = ('id', 'desc')
    
    base_filters = [['created_by', FilterEqualFunction, get_user],
                    ['request_type', FilterEqual, 'vendor']
                    ]

    base_permissions = ['can_add','can_list','can_show'] 
    
    validators_columns = {'vendor': [DataRequired(message='NOT Released: Vendor is required')],
                          'mr': [DataRequired(message='NOT Released: MR is required')]
    }
    
    list_title = 'Vendor Code Request'
    add_title = 'Add Vendor Code Request'
    edit_title = 'Edit Vendor Code Request'
    show_title = 'Show Vendor Code Request'
    #related_views = [DocumentView] 
    # list_widget = ListThumbnail
    title = "Bapco Vendor Code Request"
    #search_columns = ['created_by']
    
    
    list_columns = ['req_type', 'quantity', 'req_description', 'created_by', 'created']
    
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
                                        'partner'], 'expanded':True}
                        ),
                     ]
    show_fieldsets = [
                        (
                            'Number of Bapco Codes',
                            {'fields': ['req_type', 'quantity']}
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
        #choice_unit(self, item)
        session_list = []
        for i in range(0, item.quantity):
            print('****** Vendor Code Released ******')

            code = bapco(self, item)
            session_list.append([code])
            print(code)
            print('SESSION LIST:', session_list)
        toxlsx(self, item, session_list)

    @expose('/add', methods=['GET', 'POST'])
    @has_access
    def add(self):

        widget = self._add()
        if not widget:
            return redirect(url_for('PendingView.list'))
        else:
            return self.render_template(self.add_template,
                                        title=self.add_title,
                                        widgets=widget)

class AskBapcoView(MultipleView):
    datamodel = SQLAInterface(DocRequests)
    #views = [DocRequestsView, VendorRequestsView]
   

class UnitView(CompactCRUDMixin, ModelView):
    datamodel = SQLAInterface(Unit)
    list_columns = ['unit', 'name', 'unit_type', 'description']

    add_columns = ['unit', 'name', 'unit_type', 'start', 'stop']
    edit_columns = ['unit', 'name', 'unit_type', 'start', 'stop']
    show_columns = ['unit', 'name', 'unit_type', 'start', 'stop', 'description']
    
    # list_widget = ListCarousel
    # label_columns = ['unit','description']
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class MaterialclassView(ModelView):
    datamodel = SQLAInterface(Materialclass)
    list_columns = ['materialclass', 'name', 'description']
    add_columns = ['materialclass', 'name', 'description']
    edit_columns = ['materialclass', 'name', 'description']
    show_columns = ['materialclass', 'name', 'description']
    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class DoctypeView(ModelView):
    datamodel = SQLAInterface(Doctype)
    list_columns = ['doctype', 'name', 'description']

    add_columns = ['doctype', 'name', 'description']
    edit_columns = ['doctype', 'name', 'description']
    show_columns = ['doctype', 'name', 'description']
    
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class PartnerView(ModelView):
    datamodel = SQLAInterface(Partner)
    list_columns = ['partner', 'common_start', 'common_stop', 'description']

    add_columns = ['partner', 'name', 'common_start', 'common_stop', 'description']
    edit_columns = ['partner', 'name', 'common_start', 'common_stop', 'description']
    show_columns = ['partner', 'name', 'common_start', 'common_stop', 'description']

    list_widget = ListThumbnail

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class CdrlitemView(ModelView):
    datamodel = SQLAInterface(Cdrlitem)
    list_columns = ['cdrlitem', 'name', 'description']

    add_columns = ['cdrlitem', 'name', 'description']
    edit_columns = ['cdrlitem', 'name', 'description']
    show_columns = ['cdrlitem', 'name', 'description']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class DocumentclassView(ModelView):
    datamodel = SQLAInterface(Documentclass)
    list_columns = ['documentclass','name', 'description']

    add_columns = ['documentclass', 'name', 'description']
    edit_columns = ['documentclass', 'name', 'description']
    show_columns = ['documentclass', 'name', 'description']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class VendorView(ModelView):
    datamodel = SQLAInterface(Vendor)
    list_columns = ['vendor', 'description']

    add_columns = ['vendor', 'name', 'description']
    edit_columns = ['vendor', 'name', 'description']
    show_columns = ['vendor', 'name', 'description']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class MrView(ModelView):
    datamodel = SQLAInterface(Mr)
    list_columns = ['mr', 'name', 'description']

    add_columns = ['mr', 'name', 'description']
    edit_columns = ['mr', 'name', 'description']
    show_columns = ['mr', 'name', 'description']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


class DocRequestsView(ModelView):
    datamodel = SQLAInterface(DocRequests)
    default_view = 'add'
    
    label_columns = {
        'id': 'ID',
        'unit': 'Unit',
        'materialclass': ' Mat Class',
        'doctype': 'Doc Type',
        'cdrlitem': 'CDRL Item',
        'documentclass': 'Doc Class',
        'partner': 'Partner',
        'quantity': 'Qty',
        
        'csv': 'XLS',
        'req_type': 'Type',
        'req_description': 'Description',
        'created': 'Created on',
        

    }
    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user],
                    ['request_type', FilterEqual, 'engineering']
                    ] 
    base_permissions = ['can_add','can_list','can_show'] 
    #related_views = [DocumentView]
    show_template = 'appbuilder/general/model/show_cascade.html'
    edit_template = 'appbuilder/general/model/edit_cascade.html'

    add_template = 'appbuilder/general/model/add_eng.html'

    list_title = 'Engineering Code Request'
    add_title = 'Add Engineering Code Request'
    edit_title = 'Edit Engineering Code Request'
    show_title = 'Show Engineering Code Request'
    #related_views = [DocumentView]
    # list_widget = ListThumbnail
    title = "Bapco Engineering Code Request"
    #
    
    list_columns = ['req_type', 'quantity', 'req_description', 'created_by', 'created']
    
    edit_columns = ['unit', 'materialclass', 'doctype', 'cdrlitem',
                    'documentclass', 'partner']
    
    search_columns = ['unit', 'materialclass', 'doctype', 'cdrlitem',
                      'documentclass', 'partner', 'quantity', 'created_on']
    search_columns = UnitView.search_columns
    
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
        #choice_unit(self, item)
        print('after cHoice')
        session_list = []
        
        for i in range(0, item.quantity):
            print('****** Engineering Code Released ******')

            code = bapco(self, item)
            session_list.append([code])
            print(code)
            print('SESSION LIST:', session_list)
        #toxlsx(self, item, session_list)
        #redirect(url_for(PendingView))
    
    @expose('/add', methods=['GET', 'POST'])
    @has_access
    def add(self):

        widget = self._add()
        if not widget:
            return redirect(url_for('PendingView.list'))
        else:
            return self.render_template(self.add_template,
                                        title=self.add_title,
                                        widgets=widget)

        





class MatrixView(ModelView):
    datamodel = SQLAInterface(Matrix)
    list_columns = ['id', 'matrix', 'counter']




class MultipleViewsExp(MultipleView):
    views = [UnitView, MaterialclassView, DoctypeView, PartnerView]
    list_widget = ListBlock


def pretty_month_year(value):
    return Markup(momentjs(value.created_on).format('MMM Y'))

class RequestChartView(GroupByChartView):
    datamodel = SQLAInterface(DocRequests)
    
    chart_title = 'Requests Chart'
    label_columns = UnitView.label_columns
    #chart_type = 'PieChart'
    chart_type = 'BarChart'

    definitions = [
        {
            'label': 'User',
            'group': 'user_create',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'Type',
            'group': 'request_type',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'Unit',
            'group': 'unit_c',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'Mat Class',
            'group': 'materialclass_c',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'Doc Type',
            'group': 'doctype_c',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'CDRL',
            'group': 'cdrlitem_c',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'Doc Class',
            'group': 'documentclass_c',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'Vendor',
            'group': 'vendor_c',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'MR',
            'group': 'mr_c',
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'Partner',
            'group': 'partner_c', 
            'series': [(aggregate_count, 'id')]
        },
        {
            'label': 'Matrix',
            'group': 'matrix_c',
            'series': [(aggregate_count, 'id')]
        }
        
    ]

class TimelineChart(GroupByChartView):
    datamodel = SQLAInterface(DocRequests)
    
    chart_title = 'Timeline Requests Chart'
    #label_columns = ['some','label']
    chart_type = 'BarChart'

    definitions = [
        {
            'label': 'Month',
            'group': 'pretty_month_year',
            'series': [(aggregate_count, 'id'),
                       (aggregate_sum, 'quantity')
            ]
        },
        {
            'label': 'by DocType',
            'group': 'doctype_c',
            'series': [(aggregate_count, 'doctype_c')]
        },
        {
            'label': 'by User',
            'group': 'user_create',
            'series': [(aggregate_count, 'request_type')]
        }
    ]




def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Setting_updateView(BaseView):
    default_view = 'upload_setting'

    @expose('/setting/', methods=['POST','GET'])
    @has_access
    def upload_setting(self):
        if request.method == 'POST':
            
            if 'file' not in request.files:
                flash('No file part')
                print('we have a problem with THE FORM !')
                return redirect(request.url)
       
            files = request.files
            print('file is type of:', type(files))
            
            if isinstance(files, ImmutableMultiDict):
                print('is an ImmutableMultiDICT ! ****')
                print('WE HAVE FILES !!', files)
                
                files = dict(files)
                filename_list = []
                reserved_list = []
                updated_list = []
                
                print('lunghezza files: ', len(files['file']))
                files = files['file']
                print('Files afteer DICT',files)
                
                for file in files:
                    #file = file[0]
                    print('type of row', type(file), file)
                    if file.filename == '':
                        flash('No selected file')
                        return redirect(request.url)
                    if file and allowed_file(file.filename):
                        print('IS ALLOWED FILE !!')
                        filename = secure_filename(file.filename)
                        filename_list.append(filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        res_list, upd_list = setting_update(file)
                        #for item in res_list:
                            #flash('WARNING: '+ str(item[1])+'is already reserved by '+ str(item[2]), category='warning')
                        reserved_list += res_list
                        updated_list += upd_list
                        
                        print('reserdev list:', reserved_list)
                        print('updated list:', updated_list)
                        self.update_redirect()
                
                flash('Update: '+ str(len(files)) +' files processed, '+ str(len(updated_list))+' total settings updated.', category='info')
                return self.render_template('setting_up.html',
                                            filename=filename_list,
                                            updated_list=updated_list,
                                            count_updated=len(updated_list),
                                            reserved_list=reserved_list,
                                            count_reserved=len(reserved_list))
            '''
                return redirect(url_for('Uploadcodes.upload',
                                        filename=filename_list,
                                        updated_list=updated_list,
                                        count_updated=len(updated_list),
                                        reserved_list=reserved_list,
                                        count_reserved=len(reserved_list)))
            '''
        return self.render_template('setting_up.html')

class Oldcodes(BaseView):
    default_view = 'oldcodes'
    @expose('/oldcodes/', methods=['POST', 'GET'])
    @has_access
    def oldcodes(self): 
        if request.method == 'POST':
            print('request FORM', request.form)
            print('we have it! POOOOST', request.files)
            # check if the post request has the file part
            
            if 'file' not in request.files:
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
                print('lunghezza files: ', len(files['file']))
                files = files['file']
                print('Files afteer DICT',files)
                for file in files:
                    #file = file[0]
                    #print('type of row', type(file), file)
                    if file.filename == '':
                        flash('No selected file')
                        return redirect(request.url)
                    
                    if file and allowed_file(file.filename):
                        print('IS ALLOWED FILE !!')
                        filename = secure_filename(file.filename)
                        filename_list.append(filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        res_list, upd_list, result_file = old_codes(self, file)
                        #for item in res_list:
                            #flash('WARNING: '+ str(item[1])+'is already reserved by '+ str(item[2]), category='warning')
                        reserved_list += res_list
                        updated_list += upd_list
                        
                        #print('reserdev list:', reserved_list)
                        #print('updated list:', updated_list)
                        self.update_redirect()
                
                #flash('Update: '+ str(len(files)) +' files processed, '+ str(len(updated_list))+' total codes updated.', category='info')
                return self.render_template('oldcodes.html',
                                            filename=filename_list,
                                            updated_list=updated_list,
                                            count_updated=len(updated_list),
                                            reserved_list=reserved_list,
                                            count_reserved=len(reserved_list),
                                            result_file=result_file
                                            )
            '''
                return redirect(url_for('Uploadcodes.upload',
                                        filename=filename_list,
                                        updated_list=updated_list,
                                        count_updated=len(updated_list),
                                        reserved_list=reserved_list,
                                        count_reserved=len(reserved_list)))
            '''
        return self.render_template('oldcodes.html')


class Uploadcodes(BaseView):
    
    default_view = 'upload_form'
    '''
    @expose('/excel/') 
    @has_access
    def upload(self):
        print('GET METHOD HERE')
        
        return self.render_template('upload.html', filename=["pippo","pappo"])
    '''
    @expose('/excel/', methods=['POST', 'GET'])
    @has_access
    def upload_form(self):
        if request.method == 'POST':
            print('request FORM', request.form)
            print('we have it! POOOOST', request.files)
            # check if the post request has the file part
            
            if 'file' not in request.files:
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
                print('lunghezza files: ', len(files['file']))
                files = files['file']
                print('Files afteer DICT',files)
                for file in files:
                    #file = file[0]
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
                        #for item in res_list:
                            #flash('WARNING: '+ str(item[1])+'is already reserved by '+ str(item[2]), category='warning')
                        reserved_list += res_list
                        updated_list += upd_list
                        
                        print('reserdev list:', reserved_list)
                        print('updated list:', updated_list)
                        self.update_redirect()
                
                flash('Update: '+ str(len(files)) +' files processed, '+ str(len(updated_list))+' total codes updated.', category='info')
                return self.render_template('upload_status.html',
                                            filename=filename_list,
                                            updated_list=updated_list,
                                            count_updated=len(updated_list),
                                            reserved_list=reserved_list,
                                            count_reserved=len(reserved_list))
            '''
                return redirect(url_for('Uploadcodes.upload',
                                        filename=filename_list,
                                        updated_list=updated_list,
                                        count_updated=len(updated_list),
                                        reserved_list=reserved_list,
                                        count_reserved=len(reserved_list)))
            '''
        return self.render_template('upload.html')

    @expose('/excel/ajax', methods=['POST', 'GET'])
    @has_access
    def ajax_upload_form(self):
        if request.method == 'POST':
            print('request FORM', request.form)
            print('we have it! POOOOST', request.files)
            # check if the post request has the file part
            
            if 'file[0]' not in request.files:
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
                print('lunghezza files: ',len(files))
                print('Files afteer DICT',files)
                for k, file in files.items():
                    file = file[0]
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
                        flash('here we are', category='warning')
                        print('reserdev list:', reserved_list)
                        print('updated list:', updated_list)
                        self.update_redirect()
                      
            return self.render_template('upload_status.html',
                                        filename=filename_list,
                                        updated_list=updated_list,
                                        count_updated=len(updated_list),
                                        reserved_list=reserved_list,
                                        count_reserved=len(reserved_list))
            '''
                return redirect(url_for('Uploadcodes.upload',
                                        filename=filename_list,
                                        updated_list=updated_list,
                                        count_updated=len(updated_list),
                                        reserved_list=reserved_list,
                                        count_reserved=len(reserved_list)))
            '''
        return self.render_template('upload_status.html')


class CommentsView(ModelView):
    datamodel = SQLAInterface(Comments)
    list_columns = ['doc','comment', 'created_by', 'created', 'changed_by', 'modified']
    add_columns = ['doc', 'comment']
    show_columns = ['doc', 'comment', 'created_by', 'created', 'changed_by', 'modified']
    edit_columns = ['comment']
    
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template,
                           appbuilder=appbuilder), 404

class DocumentView(CompactCRUDMixin, ModelView):
    datamodel = SQLAInterface(Document)
    list_title = 'Bapco Codes'
    related_views = [CommentsView]
    
    
    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user]]
    base_permissions = ['can_list', 'can_show', 'can_edit'] 

    edit_title = 'Edit Code'
    show_title = 'Show Code'

    
    #show_columns = ['id', 'code_type', 'bapco_code', 'oldcode', 'created_by', 'created', 'status']
    list_columns = ['code_type', 'bapco_code', 'oldcode_p','notes', 'created', 'status']
    edit_columns = ['oldcode', 'notes']

    #search_columns = DocRequestsView.search_columns

    label_columns = {
        'id': 'ID',
        'created': 'Created On',
        'modified': 'Modified On',
        'changed_by': 'Modified By',
        'status': 'Status',
        'oldcode': 'Contractor Code',
        'oldcode_p': 'Contractor Code',
        'code': 'Bapco Code',
        'code_type': 'Type',
        
    }
   
    @action("export", "Export", "", "fa-table")
    def export(self, items):
        print('Export from DocumentView')
        if isinstance(items, list):
            codes_list = []
            for item in items:
                print('item', item.code)
                codes_list.append([item.code, item.oldcode])
            filename = codes_to_xlsx(codes_list)
            
            self.update_redirect()
            
        else:
            filename = codes_to_xlsx(items.code)
        
        #print(codes_list)
        #redirect(self.get_redirect())
        self.update_redirect()
        return send_file('static/csv/' + filename, as_attachment=True)

class UserDocumentView(MasterDetailView):
    datamodel = SQLAInterface(User)
    related_views = [DocumentView]
    value_columns = ['username']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())

class ListRequest(ModelView):
    datamodel = SQLAInterface(DocRequests)
    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user]]
    base_permissions = ['can_list', 'can_show'] 

    list_title = 'All Requests'
    add_title = 'Add new Request'
    edit_title = 'Edit Code Request'
    show_title = 'View Code Request'
    related_views = [DocumentView]

    show_template = 'appbuilder/general/model/show_cascade.html'
    edit_template = 'appbuilder/general/model/edit_cascade.html'
    
    #list_widget = ListThumbnail

    title = "Bapco Document ID Generator"
    label_columns = {
        'csv': 'XLS',
        'req_type': 'Type',
        'req_description': 'Description',
        'created': 'Created on'

    }
    
    list_columns = ['req_type', 'req_description', 'created', 'csv']
    edit_columns = ['unit', 'materialclass', 'doctype', 'partner']


    add_exclude_columns = ['id', 'matrix']

    add_fieldsets = [
                        (
                            'Quantity',
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

class SuperListRequest(ModelView):
    datamodel = SQLAInterface(DocRequests)
    base_order = ('id', 'desc')
    #base_filters = [['created_by', FilterEqualFunction, get_user]]
    base_permissions = ['can_list', 'can_show'] 

    list_title = 'Supervisor - All Requests'
    add_title = 'Add new Request'
    edit_title = 'Edit Code Request'
    show_title = 'View Code Request' 
    related_views = [DocumentView]

    show_template = 'appbuilder/general/model/show_cascade.html'
    edit_template = 'appbuilder/general/model/edit_cascade.html'
    
    #list_widget = ListThumbnail

    title = "Bapco Document ID Generator"
    label_columns = {
        'csv': 'XLS',
        'req_type': 'Type',
        'req_description': 'Description',
        'created': 'Created on'

    }
    
    list_columns = ['req_type', 'req_description', 'created', 'csv']
    edit_columns = ['unit', 'materialclass', 'doctype', 'partner']


    add_exclude_columns = ['id', 'matrix']

    add_fieldsets = [
                        (
                            'Quantity',
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

class PartnerRequestView(MasterDetailView):
    datamodel = SQLAInterface(Partner)
    related_views = [SuperListRequest]
    value_columns = ['name']

    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket")
    def muldelete(self, items):
        if isinstance(items, list):
            self.datamodel.delete_all(items)
            self.update_redirect()
        else:
            self.datamodel.delete(items)
        return redirect(self.get_redirect())


## Flask migrate with Alembic instead of this
db.create_all()

# Risorse Bapco
'''
appbuilder.add_view(CommentsView, "Comments",
                    icon="fa-paper-plane", category="Admin",
                    category_icon='fa-bold')
'''
appbuilder.add_view(Oldcodes, "Old Codes Upload",
                    icon="fa-paper-plane", category="Supervisor",
                    category_icon='fa-bold')

appbuilder.add_view(CommentsView, "Comments",
                    icon="fa-paper-plane", category="Supervisor",
                    category_icon='fa-bold')


#appbuilder.add_view_no_menu(DocRequestsView)
appbuilder.add_view(DocRequestsView, "Engineering Code Request",
                    icon="fa-paper-plane", category="Requests",
                    category_icon='fa-bold')

appbuilder.add_view(VendorRequestsView, "Vendor Code Request",
                    icon="fa-paper-plane", category="Requests",
                    category_icon='fa-bold')

appbuilder.add_view(AskBapcoView, "N Request",
                    icon="fa-paper-plane", category="Requests",
                    category_icon='fa-bold')


appbuilder.add_separator(category='Requests')

appbuilder.add_view(ListRequest, "All Requests",
                    icon="fa-codepen", category="Requests")

appbuilder.add_view(DocumentView, "All Your Codes",
                    icon="fa-list", category="Your Codes")

appbuilder.add_view(PendingView, "Only Pending Codes",
                    icon="fa-folder-open", category="Your Codes",
                    category_icon='fa-bold')

appbuilder.add_separator(category="Your Codes")

appbuilder.add_view(Uploadcodes, "Update Codes (Excel)",
                    icon="fa-paper-plane", category="Your Codes",
                    category_icon='fa-bold')

# Bapco Setting
appbuilder.add_view(Setting_updateView, "Update Setting (Excel)",
                    icon="fa-cogs", category="Settings",
                    category_icon='fa-cubes')

appbuilder.add_view(MultipleViewsExp, "Smart Settings",
                    icon="fa-cogs", category="Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(UnitView, "Unit",
                    icon="fa-list", category="Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(MaterialclassView, "Material Class",
                    icon="fa-list", category="Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(DoctypeView, "DocType",
                    icon="fa-list", category="Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(PartnerView, "Partner",
                    icon="fa-list", category="Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(CdrlitemView, "CDRL Item",
                    icon="fa-list", category="Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(DocumentclassView, "Document Class",
                    icon="fa-list", category="Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(VendorView, "Vendor",
                    icon="fa-list", category="Settings",
                    category_icon='fa-cubes')
appbuilder.add_view(MrView, "MR",
                    icon="fa-list", category="Settings",
                    category_icon='fa-cubes')

appbuilder.add_view(MatrixView, "Matrix View",
                    icon="fa-folder-open-o", category="Settings",
                    category_icon='fa-bomb')

# Bapco Supervisor
# 
#       

appbuilder.add_view(SuperListRequest, "All Requests",
                    icon="fa-folder-open-o", category="Supervisor",
                    category_icon='fa-envelope')

appbuilder.add_view(SuperDocumentView, "All Codes",
                    icon="fa-folder-open-o", category="Supervisor",
                    category_icon='fa-envelope')

appbuilder.add_view(UserDocumentView, "Codes Generated by User",
                    icon="fa-folder-open-o", category="Supervisor")

appbuilder.add_view(PartnerRequestView, "Codes Generated by Partner",  
                    icon="fa-folder-open-o", category="Supervisor")

appbuilder.add_view(RequestChartView, "Naming Requests Chart",
                    icon="fa-folder-open-o", category="Supervisor",
                    category_icon='fa-envelope')

appbuilder.add_view(TimelineChart, "Timeline Request Chart",
                    icon="fa-folder-open-o", category="Supervisor",
                    category_icon='fa-envelope')
