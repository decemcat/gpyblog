__author__ = 'gavin'
import tornado.web
import datetime
from bson.objectid import ObjectId

import dao.dbase


class CommentModule(tornado.web.UIModule):
    def __init__(self, handler):
        super(CommentModule, self).__init__(handler)
        self._comment = dao.dbase.BaseDBSupport().db["comment"]

    def render(self, article_id):
        dbcomments = self._comment.find({"article_id": str(article_id)})
        comments = []
        for dbcomment in dbcomments:
            comments.append(dbcomment)

        com2del = []
        for comment in comments:
            if comment.has_key("parent_id") and comment["parent_id"] is not None:
                com2del.append(comment)
                cm = self._find_byid(comments, comment["parent_id"])
                if not cm.has_key("subcomment"):
                    cm["subcomment"] = []
                cm["subcomment"].append(comment)

        for com in com2del:
            comments.remove(com)

        return self.render_string('module/comment.html', comments=comments, article_id=article_id)

    def _find_byid(self, comments, id):
        for comment in comments:
            if ObjectId(id) == comment["_id"]:
                return comment
        return None


class CommentHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(CommentHandler, self).__init__(application, request, **kwargs)
        self._comment = dao.dbase.BaseDBSupport().db["comment"]

    def post(self, *args, **kwargs):
        article_id = self.get_body_argument("article_id")
        user = self.get_body_argument("user")
        email = self.get_body_argument("email")
        content = self.get_body_argument("content")
        if not article_id or not user or not email or not content:
            return

        parent_id = None
        comment_id = None
        try:
            parent_id = self.get_body_argument("parent_id")
        except tornado.web.MissingArgumentError:
            parent_id = None

        try:
            comment_id = self.get_body_argument("comment_id")
        except tornado.web.MissingArgumentError:
            comment_id = None

        comment = {"article_id": article_id, "user": user, "email": email, "content": content, "isauthor": "0", "time": datetime.datetime.now()}
        if parent_id is not None:
            comment["parent_id"] = parent_id

        if comment_id is not None:
            comment["comment_id"] = comment_id

        self._comment.insert(comment)
        self.redirect("/post/" + article_id + ".html")
