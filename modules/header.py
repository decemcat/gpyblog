__author__ = 'gavin'
import tornado.web


class HeaderModule(tornado.web.UIModule):
    def render(self, menus):
        return self.render_string('module/header.html', menus=menus)