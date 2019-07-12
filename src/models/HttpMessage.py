from app import db


class HttpMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request = db.Column(db.String())
    response = db.Column(db.String())

    def __repr__(self):
        return self.as_json()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def as_json(self):
        d = self.as_dict()
        return json.dumps(d, indent=4)
