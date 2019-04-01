

from flask_appbuilder import BaseView, expose
  

class someView(BaseView):
    """
        A simple view that implements the index for the site
    """    
    route_base = ''
    default_view = 'index'
    index_template = 'appbuilder/index.html'
  
    @expose('/')
    def index(self):
        from app import db
        from .models import Partner, Unit, Materialclass, Doctype

        session = db.session
        partner = session.query(Partner).count()
        unit = session.query(Unit).count()
        material = session.query(Materialclass).count()
        doctype = session.query(Doctype).count()
       
        
        self.update_redirect()
        return self.render_template(self.index_template,
                                    appbuilder=self.appbuilder,
                                    partner=partner,
                                    unit=unit,
                                    material=material,
                                    doctype=doctype)


class MyIndexView(someView):
    index_template = 'index.html'

