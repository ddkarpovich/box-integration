from box.app import db


class BoxIntegration(db.Model):
    """Box API integration settings."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates='box_integration')
    access_token = db.Column(db.String(255))
    refresh_token = db.Column(db.String(255))
    webhooks = db.relationship('BoxWebHook', uselist=False, back_populates='integration')

    def __str__(self) -> str:
        return self.id


class BoxWebHook(db.Model):
    """Box API WebHook storage."""
    id = db.Column(db.Integer, primary_key=True)
    integration_id = db.Column(db.Integer, db.ForeignKey('box_integration.id'))
    integration = db.relationship("BoxIntegration", back_populates='webhooks')
    webhook_id = db.Column(db.String(16))
    resource_id = db.Column(db.String(256))
    events = db.Column(db.String(256))

    def __str__(self):
        return f'{self.id} for {self.events}'
