import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import torndb
import tornado.websocket
import os
from datetime import datetime

from tornado.options import define,options
define("port", default=8888, help="run port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="db host")
define("mysql_database", default="TODO", help="db name")
define("mysql_user", default="root", help="db user")
define("mysql_password", default="123", help="db password")

TEMPLATE_PATH=os.path.join(os.path.dirname(__file__),'templates')
STATIC_PATH=os.path.join(os.path.dirname(__file__),'static')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/todo/new", NewHandler),
            (r"/todo/(\d+)/edit", EditHandler),
            (r"/todo/(\d+)/delete", DeleteHandler),
            (r"/todo/(\d+)/finish", FinishHandler),
        ]
        settings = dict(
            template_path=TEMPLATE_PATH,
            static_path=STATIC_PATH,
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = torndb.Connection(
            host=options.mysql_host,
            database=options.mysql_database,
            user=options.mysql_user,
            password=options.mysql_password
        )

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        title="todo"
        db=self.application.db
        todos=db.query("select * from todo order by post_date desc ")
        self.render("index.html",todos=todos,title=title)


class NewHandler(tornado.web.RequestHandler):
    def post(self):
        title=self.get_argument('title')
        if not title:
            return None
        db=self.application.db
        db.execute("insert into todo(title, post_date) values(%s,UTC_TIMESTAMP())",
                   title)
        self.redirect('/')

class EditHandler(tornado.web.RequestHandler):
    def get(self,id):
        db=self.application.db
        todos=db.query("select * from todo where todo_id=%s",int(id))
        todo=todos[0]
        if not todo:
            return None
        return self.render('edit.html',todo=todo)

    def post(self,id):
        db=self.application.db
        todos=db.query("select * from todo where todo_id=%s",int(id))
        todo=todos[0]
        if not todo:
            return None
        title=self.get_argument('title')
        db.execute('update todo set title=%s,post_date=UTC_TIMESTAMP() where todo_id=%s',title,int(id))
        self.redirect('/')

class DeleteHandler(tornado.web.RequestHandler):
    def get(self,id):
        db=self.application.db
        todo=db.query("select * from todo where todo_id=%s",int(id))
        if not todo:
            return None
        db.execute("delete from todo where todo_id=%s",int(id))
        self.redirect('/')

class FinishHandler(tornado.web.RequestHandler):
    def get(self,id):
        db=self.application.db
        todo=db.query("select * from todo where todo_id=%s",int(id))
        if not todo:
            return None
        status=self.get_argument('status',"yes")
        if status=="yes":
            finished=1
        elif status=='no':
            finished=0
        else:
            return None
        db.execute("update todo set finished=%s where todo_id=%s",finished,int(id))
        self.redirect('/')

if __name__=='__main__':
    tornado.options.parse_command_line()
    app=Application()
    server=tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()




