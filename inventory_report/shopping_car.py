#coding:utf-8
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from uuid import uuid4
import tornado.websocket

class ShoppingCart(object):
    totalInventory = 10
    callbacks = []
    carts = {}

    def register(self, callback):
        self.callbacks.append(callback)

    def unregister(self,callback):
        self.callbacks.remove(callback)

    def moveItemToCart(self, session):
        if session in self.carts:
            return

        self.carts[session] = True
        self.notifyCallbacks()

    def removeItemFromCart(self, session):
        if session not in self.carts:
            return

        del(self.carts[session])
        self.notifyCallbacks()

    def notifyCallbacks(self):
        for c in self.callbacks:
            self.callbackHelper(c)

    def callbackHelper(self, callback):
        callback(self.getInventoryCount())

    def getInventoryCount(self):
        return self.totalInventory - len(self.carts)

class DetailHandler(tornado.web.RequestHandler):
    def get(self):
        session = uuid4()
        count = self.application.shoppingCart.getInventoryCount()
        self.render("index.html", session=session, count=count)

class CartHandler(tornado.web.RequestHandler):
    def post(self):
        action = self.get_argument('action')
        session = self.get_argument('session')

        if not session:
            self.set_status(400)
            return

        if action == 'add':
            self.application.shoppingCart.moveItemToCart(session)
        elif action == 'remove':
            self.application.shoppingCart.removeItemFromCart(session)
        else:
            self.set_status(400)

class StatusHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        self.application.shoppingCart.register(self.callback)

    def on_close(self):
        self.application.shoppingCart.unregister(self.callback)

    def on_message(self, message):
        pass

    def callback(self, count):
        self.write_message('{"inventoryCount":"%d"}' % count)

class TwitterHandler(tornado.web.RequestHandler, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        oAuthToken = self.get_secure_cookie('oauth_token')
        oAuthSecret = self.get_secure_cookie('oauth_secret')
        userID = self.get_secure_cookie('user_id')

        if self.get_argument('oauth_token', None):
            self.get_authenticated_user(self.async_callback(self._twitter_on_auth))
            return

        elif oAuthToken and oAuthSecret:
            accessToken = {
                'key': oAuthToken,
                'secret': oAuthSecret
            }
            self.twitter_request('/users/show',
                access_token=accessToken,
                user_id=userID,
                callback=self.async_callback(self._twitter_on_user)
            )
            return

        self.authorize_redirect()

    def _twitter_on_auth(self, user):
        if not user:
            self.clear_all_cookies()
            raise tornado.web.HTTPError(500, 'Twitter authentication failed')

        self.set_secure_cookie('user_id', str(user['id']))
        self.set_secure_cookie('oauth_token', user['access_token']['key'])
        self.set_secure_cookie('oauth_secret', user['access_token']['secret'])

        self.redirect('/')

    def _twitter_on_user(self, user):
        if not user:
            self.clear_all_cookies()
            raise tornado.web.HTTPError(500, "Couldn't retrieve user information")

        self.render('home.html', user=user)

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_all_cookies()
        self.render('logout.html')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', TwitterHandler),
            (r'/logout', LogoutHandler)
        ]

        settings = {
            'twitter_consumer_key': 'cWc3 ... d3yg',
            'twitter_consumer_secret': 'nEoT ... cCXB4',
            'cookie_secret': 'NTliOTY5NzJkYTVlMTU0OTAwMTdlNjgzMTA5M2U3OGQ5NDIxZmU3Mg==',
            'template_path': 'templates',
        }

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()