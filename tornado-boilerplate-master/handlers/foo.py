from handlers.base import BaseHandler
from tornado import web,gen
from tornado.httpclient import AsyncHTTPClient
import logging
logger = logging.getLogger('boilerplate.' + __name__)

class IndexHandler(BaseHandler):
    def get(self):
        title="todo"
        db=self.application.db
        todos=db.query("select * from todo order by post_date desc ")
        self.render("index.html",todos=todos,title=title)

class NewHandler(BaseHandler):
    def post(self):
        title=self.get_argument('title')
        if not title:
            return None
        db=self.application.db
        db.execute("insert into todo(title,post_date) "
                   "value (%s,UTC_TIMESTAMP())",title)
        self.write('{"id":"%d"}'%id)

class EditHandler(BaseHandler):
    def get(self,id):
        db=self.application.db
        todos=db.query("select * from todo where id=%s",int(id))
        todo=todos[0]
        if not todo:
            return None
        return self.render('edit.html',todo=todo)

    def post(self,id):
        db=self.application.db
        todos=db.query("select * from todo where id=%s",int(id))
        todo=todos[0]
        if not todo:
            return None
        title=self.get_argument('title')
        db.execute('update todo set title=%s,post_date=UTC_TIMESTAMP() where id=%s',title,int(id))
        self.redirect('/')

class DeleteHandler(BaseHandler):
    def get(self,id):
        db=self.application.db
        todo=db.query("select * from todo where id=%s",int(id))
        if not todo:
            return None
        db.execute("delete from todo where id=%s",int(id))
        self.redirect('/')

class FinishHandler(BaseHandler):
    def get(self,id):
        db=self.application.db
        todo=db.query("select * from todo where id=%s",int(id))
        if not todo:
            return None
        status=self.get_argument('status',"yes")
        if status=="yes":
            finished=1
        elif status=='no':
            finished=0
        else:
            return None
        db.execute("update todo set finished=%s where id=%s",finished,int(id))