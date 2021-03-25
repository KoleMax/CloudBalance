from sqlalchemy.orm import relationship

from application import db


class TransactionType(db.Model):

    __tablename__: str = "transaction_types"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    type = db.Column(db.String(128))


class Transaction(db.Model):

    __tablename__: str = "transactions"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    amount = db.Column(db.BigInteger)
    description = db.Column(db.String(128))

    project_id = db.Column(db.BigInteger, db.ForeignKey("projects.id"))
    tag_id = db.Column(db.BigInteger, db.ForeignKey("tags.id"))
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    type_id = db.Column(db.BigInteger, db.ForeignKey("transaction_types.id"))

    timestamp = db.Column(db.TIMESTAMP(timezone=True))

    project = relationship("Project", backref="transactions")
    user = relationship("User", backref="transactions")
    tag = relationship("Tag", backref="transactions")
