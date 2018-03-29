from app import db
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import flash, send_file, make_response, redirect, url_for

from .models import Matrix, Document, Unit, Partner
#from .views import send_csv
import csv, xlsxwriter
from werkzeug.utils import secure_filename
import uuid



def adddoc3(self, item):
    # Set the Request type
    if item.vendor and item.mr:
        item.request_type = 'vendor'
    
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

def bapco(self, item):
    # Set the DB session
    session = db.session
    
    # Set the Request type
    if item.vendor and item.mr:
        item.request_type = 'vendor'
    else:
        item.request_type = 'engineering'
    
    # Set item_matrix based on unit type
    result = db.session.query(Unit).filter(Unit.unit == str(item.unit)).first()
    
    if str(result.unit_type) == 'common':
        print('Match unit type common Found')

        # Add the partner id to the matrix
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
    # Set the bapco base code
    item_serial = str.join('-', (item.unit.unit,
                                    item.materialclass.materialclass,
                                    item.doctype.doctype,
                                    # item.sheet,
                                    ))
    
    # Increment the Matrix counter or create a new one
    matrix = db.session.query(Matrix).filter(Matrix.matrix == item_matrix).first()
    if matrix:
        matrix.counter += 1
        datamodel = SQLAInterface(Matrix, session=session)
        datamodel.edit(matrix)

        item.matrix_id = matrix.id
        code = item_serial + "-" + str(matrix.counter).zfill(5) + "-" + item.sheet

        datamodel = SQLAInterface(Document, session=session)
        doc = Document(docrequests_id=item.id, code=code)
        datamodel.add(doc)

        message = 'Your code is ' + code
        flash(message, category='info')
    else:
        # Create a New Matrix for common units
        if result.unit_type == 'common':
            
            partner = db.session.query(Partner).filter(Partner.partner == str(item.partner)).first()
           
            matrix = Matrix(counter=partner.common_start + 1, matrix=str(item_matrix))
            datamodel = SQLAInterface(Matrix, session=session)
            datamodel.add(matrix)
        

            # Add new Doc with quantity partner common start + 1
            datamodel = SQLAInterface(Document, session=session)
            code = item_serial + "-" + str(partner.common_start + 1).zfill(5) + "-" + item.sheet
            doc = Document(docrequests_id=item.id, code=code)
            datamodel.add(doc)
            message = 'Your code is ' + code
            flash(message, category='info')
        else:
            # Create a new Matrix for standard units
            datamodel = SQLAInterface(Matrix, session=session)
            matrix = Matrix(matrix=item_matrix)
            datamodel.add(matrix)

            # Add new Doc with quantity 1
            datamodel = SQLAInterface(Document, session=session)
            code = item_serial + "-" + "1".zfill(5) + "-" + item.sheet
            doc = Document(docrequests_id=item.id, code=code)

            datamodel.add(doc)
            message = 'Your code is ' + code
            flash(message, category='info')

    db.session.flush()
    return code


def tocsv(self, item,  codes_list):
    print('tocsv FUNCTION')
    print(codes_list)
    filename = 'app/static/csv/bapco_request_'+ str(item.id) + '.csv'
    with open(filename, 'w') as csv_file:
        # writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        writer = csv.writer(csv_file, dialect='excel')
        head = [['Id Code', 'Bapco Code', 'Contractor Code']] 
        writer.writerows(head)
        writer.writerows(codes_list)
        print('inside the with file for CV rendering')
        #print(csv_file)
    
    print('BEFORE file SEND')
    #send_file(filename, as_attachment=True)
    print('file SEND')
    '''
    response = make_response(filename)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'
    return response
    '''
def toxlsx(self, item,  codes_list):
    print('toXLSX FUNCTION')
    print(codes_list)
    #filename = 'app/static/csv/bapco_request_'+ str(item.id) + '.xlsx'

    workbook = xlsxwriter.Workbook('app/static/csv/bapco_request_'+ str(item.id) + '.xlsx')
    workbook.set_properties({
                            'title':    'Bapco Request spreadsheet',
                            'subject':  'With document properties',
                            'author':   'Quasar DCC Team',
                            'manager':  'Danilo Pacifico',
                            'company':  'Quasar',
                            'category': 'Bapco spreadsheets',
                            'keywords': 'Bapco, Bapco Codes, Properties',
                            'comments': 'Created by webtools.quasarPM.com'})

    worksheet = workbook.add_worksheet(name='Bapco Request List')

    bold = workbook.add_format({'bold': True})
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 25)
    worksheet.write('A1', 'Bapco Code', bold)
    worksheet.write('B1', 'Contractor Code', bold)
    # start after the header
    row = 1
    col = 0
    print(tuple(codes_list))
    #worksheet.write(0,0,'something')
    t_list = tuple(codes_list)
    for code in (t_list):
        #print('Looping colist', code, row)
        worksheet.write(row, col, str(code[0]))
        row += 1
    workbook.close()

def codes_to_xlsx(codes_list):
    print('CODEStoXLSX FUNCTION')
    print(codes_list)
    #filename = 'app/static/csv/bapco_request_'+ str(item.id) + '.xlsx'
    filename =  str(uuid.uuid4()) + '.xlsx'
    workbook = xlsxwriter.Workbook('app/static/csv/' + filename)
    workbook.set_properties({
                            'title':    'Bapco Request spreadsheet',
                            'subject':  'With document properties',
                            'author':   'Quasar DCC Team',
                            'manager':  'Danilo Pacifico',
                            'company':  'Quasar',
                            'category': 'Bapco spreadsheets',
                            'keywords': 'Bapco, Bapco Codes, Properties',
                            'comments': 'Created by webtools.quasarPM.com'})

    worksheet = workbook.add_worksheet(name='Bapco Request List')

    bold = workbook.add_format({'bold': True})
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 25)
    worksheet.write('A1', 'Bapco Code', bold)
    worksheet.write('B1', 'Contractor Code', bold)
    # start after the header
    row = 1
    col = 0
    print(tuple(codes_list))
    #worksheet.write(0,0,'something')
    t_list = tuple(codes_list)
    for code in (t_list):
        #print('Looping colist', code, row)
        worksheet.write(row, col, str(code[0]))
        row += 1
    workbook.close()
    return filename
    
    
                


