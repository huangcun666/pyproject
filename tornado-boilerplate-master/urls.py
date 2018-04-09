from handlers.foo import *

url_patterns = [
    (r"/", IndexHandler),
    (r"/todo/new", NewHandler),
    (r"/todo/(\d+)/edit", EditHandler),
    (r"/todo/(\d+)/delete", DeleteHandler),
    (r"/todo/(\d+)/finish", FinishHandler),
]
