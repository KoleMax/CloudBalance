from typing import List, Tuple, Optional

from sqlalchemy.orm import relationship

from application import db


class UsersToProjects(db.Model):
    __tablename__: str = "users_to_projects"

    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), primary_key=True)
    role_id = db.Column(db.BigInteger, db.ForeignKey("roles.id"))

    project = relationship("Project", backref="users")
    user = relationship("User", backref="projects")

    @classmethod
    async def get_user_role_id_in_project(cls, user_id: int, project_id: int) -> Optional[int]:
        result: UsersToProjects = await cls.query.where(
            (cls.project_id == project_id) & (cls.user_id == user_id)
        ).gino.first()
        if result:
            return result.role_id


class Project(db.Model):
    __tablename__: str = "projects"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    users = relationship("UsersToProjects", back_populates="project")
    access_token = db.Column(db.String(128))  # TODO: index

    @classmethod
    async def get_names_by_user_id(cls, user_id: int) -> List[Tuple[int, str]]:
        return (
            await cls.join(UsersToProjects, cls.id == UsersToProjects.project_id)
            .join(User, User.id == UsersToProjects.user_id)
            .select()
            .where(User.id == user_id)
            .with_only_columns((cls.id, cls.name))
            .gino.all()
        )

    @classmethod
    async def get_token(cls, project_id: int) -> str:
        result: Tuple[str] = (
            await cls.query.select()
            .where(cls.id == project_id)
            .with_only_columns((cls.access_token,))
            .gino.first()
        )

        return result[0]


class User(db.Model):
    __tablename__: str = "users"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    telegram_id = db.Column(db.BigInteger)  # TODO: index
    name = db.Column(db.String(128))
    projects = relationship("UsersToProjects", back_populates="user")

    @classmethod
    async def get_by_project_id(cls, project_id: int) -> List[Tuple[int, int, str]]:
        return (
            await cls.join(UsersToProjects, UsersToProjects.user_id == cls.id)
            .select()
            .where(UsersToProjects.project_id == project_id)
            .with_only_columns((cls.id, UsersToProjects.role_id, cls.name))
            .gino.all()
        )


class Role(db.Model):
    __tablename__: str = "roles"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    type = db.Column(db.String(128))
