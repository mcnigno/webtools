from flask import render_template, flash
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import (ModelView, CompactCRUDMixin, MasterDetailView,
                              MultipleView, GroupByChartView, IndexView)
from app import appbuilder, db
from .models import (DocRequests, Unit, Materialclass, Doctype,
                     Partner, Matrix, Document)
from flask_appbuilder.fieldwidgets import Select2AJAXWidget
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.widgets import ListThumbnail, ListBlock
from flask_appbuilder.models.sqla.filters import (FilterStartsWith,
                                                  FilterEqualFunction,
                                                  FilterInFunction,
                                                  FilterEqual,
                                                  FilterNotStartsWith
                                                  )
from flask import g


# from app import bapco2 as bapco
# from wtforms import Form, StringField, SelectField
# from wtforms_sqlalchemy.fields import QuerySelectField
# from wtforms.validators import DataRequired
# from flask_appbuilder.forms import DynamicForm, FlaskForm
# from flask_appbuilder import SimpleFormView
# from flask_babel import lazy_gettext as _
# from sqlalchemy.orm import relationship

def get_user():
    return g.user

def choice_unit():
    return db.session.query(Unit)


def matrixenc(self, item):

    print('matix ENC')
    adddoc2(self, item)


def adddoc2(self, item):
    print('adddoc 2 +++++')
    print('doctype, sheet', item.doctype.doctype, item.sheet)
    session = db.session
    matrix = session.query(Matrix)
    if item.unit.unit == '000':
        item_matrix = str.join('-', (item.unit.unit,
                                     item.materialclass.materialclass,
                                     item.doctype.doctype,
                                     item.sheet,
                                     item.partner.partner))
    else:
        item_matrix = str.join('-', (item.unit.unit,
                                     item.materialclass.materialclass,
                                     item.doctype.doctype,
                                     item.sheet))

    item_serial = str.join('-', (item.unit.unit,
                                 item.materialclass.materialclass,
                                 item.doctype.doctype,
                                 item.sheet))

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
            code = item_serial + "-" + str(row.counter).zfill(5)

            datamodel = SQLAInterface(Document, session=session)
            doc = Document(docrequests_id=item.id, code=code)
            datamodel.add(doc)

            message = 'Your code is ' + code
            flash(message, category='info')
            found = True

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
            code = item_serial + "-" + str(jv[str(item.partner)] + 1).zfill(5)
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
            code = item_serial + "-" + "1".zfill(5)
            doc = Document(docrequests_id=item.id, code=code)

            datamodel.add(doc)
            message = 'Your code is ' + code
            flash(message, category='info')

    db.session.flush()


def get_pending():
    return 'reserved'


class PendingView(ModelView):
    datamodel = SQLAInterface(Document)
    #base_filters = [['oldcode', FilterStartsWith, '']]
    base_filters = [['oldcode', FilterStartsWith, 'empty'],
                    ['created_by', FilterEqualFunction, get_user]]
    
    list_columns = ['id', 'created_by', 'status', 'oldcode', 'code']
    base_order = ('id', 'desc')
    list_title = 'Elenco Codifiche Bapco in stato "Pending"'
    edit_title = 'Modifica Codifica'
    edit_columns = ['oldcode']
    


class DocumentView(CompactCRUDMixin, ModelView):
    datamodel = SQLAInterface(Document)
    
    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user]]
    list_title = 'Elenco Codifiche Bapco'
    #add_title = 'Nuova Richiesta Codifiche'
    edit_title = 'Modifica Codifica'
    show_title = 'Vista Codifica'

    list_columns = ['id', 'created_by', 'status', 'oldcode', 'code']
    edit_columns = ['oldcode']





class DocRequestsView(CompactCRUDMixin):
    datamodel = SQLAInterface(DocRequests)
    base_order = ('id', 'desc')
    base_filters = [['created_by', FilterEqualFunction, get_user]]

    list_title = 'Richiesta Codifiche Bapco'
    add_title = 'Nuova Richiesta Codifiche'
    edit_title = 'Modifica Richiesta Codifica'
    show_title = 'Vista Richiesta Codifica'
    related_views = [DocumentView, PendingView]
    # list_widget = ListThumbnail
    title = "Bapco Document ID Generator"
    search_columns = ['created_by']

    list_columns = ['id', 'unit', 'materialclass', 'doctype',
                    'partner', 'quantity', 'created_by', 'created_on']

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
    add_form_extra_fields = {
                    'unit2': AJAXSelectField('unit2',
                                             description='This is by AJAX',
                                             datamodel=datamodel,
                                             col_name='unit',
                                             widget=Select2AJAXWidget(endpoint='/docrequestsview/api/column/add/unit')),
                                            }

    def post_add(self, item):

        for i in range(0, item.quantity):
            print('*****VVVVVV******')

            adddoc2(self, item)


class AskBapcoView(MultipleView):
    datamodel = SQLAInterface(DocRequests)
    views = [DocRequestsView, PendingView]
    list_columns = ['id']
    

class UnitView(CompactCRUDMixin, ModelView):
    datamodel = SQLAInterface(Unit)
    list_columns = ['unit', 'description']
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

    list_title = 'Richiesta Codifiche Bapco'
    add_title = 'Nuova Richiesta Codifiche'
    edit_title = 'Modifica Richiesta Codifica'
    show_title = 'Vista Richiesta Codifica'
    related_views = [DocumentView, PendingView]
    # list_widget = ListThumbnail
    title = "Bapco Document ID Generator"
    search_columns = ['created_by']

    list_columns = ['id', 'unit', 'materialclass', 'doctype',
                    'partner', 'quantity', 'created_by', 'created_on']

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




@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template,
                           appbuilder=appbuilder), 404


db.create_all()

# Risorse Bapco
appbuilder.add_view(AskBapcoView, "Richiesta Codifica",
                    icon="fa-paper-plane", category="Ask Bapco",
                    category_icon='fa-bold')

appbuilder.add_view_no_menu(DocRequestsView)

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