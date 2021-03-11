from sqlalchemy.orm import relationship

from application import db

from typing import List, Tuple


class Tag(db.Model):

    __tablename__: str = 'tags'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    project_id = db.Column(db.BigInteger, db.ForeignKey('projects.id'))

    project = relationship("Project", backref="tags")

    @classmethod
    async def get_by_project_id(cls, project_id: int) -> List[Tuple[int, str]]:
        return await cls.query.select().where(cls.project_id == project_id).with_only_columns((cls.id, cls.name)).gino.all()
