import json
import uuid
from typing import Callable, Coroutine
from typing import Tuple, List

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aioredis import Redis

from application.config import logging
from application.db import Database
from application.enums import UserRoles
from application.models import Project, Tag, Role, UsersToProjects
from application.telegram.fsm import (
    CreateProjectData,
    JoinToProjectData,
    make_redis_joining_key,
    make_redis_creating_key,
)
from application.telegram.menu.main.renderers import return_button
from application.telegram.menu.main_settings.renderers import MainSettingsMenuRenderer
from application.telegram.menu.projects.renderers import ProjectsListRenderer
from application.telegram.menu.projects.shemas import ProjectInfo, ProjectsListRenderingInfo

logger = logging.get_app_logger()


async def projects_handler(query: CallbackQuery) -> None:
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])

    user_projects: List[Tuple[int, str]] = await Project.get_names_by_user_id(user_id)

    # empty projects projects reply
    if len(user_projects) == 0:
        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id)
        await query.answer("Looks like you don't have any projects.")
        await query.message.edit_reply_markup(reply_markup=return_markup)
        return

    projects_data = [
        ProjectsListRenderingInfo(
            button_title=project_data[1],
            callback_data=ProjectInfo(
                id=project_data[0],
                name=project_data[1],
            ),
        )
        for project_data in user_projects
    ]

    projects_markup = ProjectsListRenderer(user_id=user_id)(projects_data)
    await query.message.edit_text("Here are your projects.")
    await query.message.edit_reply_markup(reply_markup=projects_markup)


async def settings_handler(query: CallbackQuery) -> None:
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])

    settings_markup = MainSettingsMenuRenderer(user_id=user_id)()
    await query.message.edit_text("Main settings.")
    await query.message.edit_reply_markup(reply_markup=settings_markup)


def make_create_project_handler(redis: Redis) -> Callable[[CallbackQuery], Coroutine[None, None, None]]:
    async def set_create_project_state(query: CallbackQuery) -> None:
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])

        chat_id = int(query.message.chat.id)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id)
        await query.message.edit_text("Please, enter name of a project you want to create:")
        await query.message.edit_reply_markup(reply_markup=return_markup)

        # set fsm to join to project dialog and save user data to redis
        redis_data = CreateProjectData(user_id=user_id)
        await redis.set(make_redis_creating_key(chat_id), redis_data.json())

    return set_create_project_state


def make_create_project_callback(db: Database, redis: Redis) -> Callable[[Message], Coroutine[None, None, None]]:
    async def create_project(message: Message) -> None:
        project_name = message.text
        chat_id = message.chat.id

        redis_key = make_redis_creating_key(chat_id)

        user_data = await redis.get(redis_key)
        parsed_user_data = CreateProjectData(**json.loads(user_data))
        user_id = parsed_user_data.user_id

        token = str(uuid.uuid4())

        async with db.transaction():
            creator_role = await Role.query.where(Role.type == UserRoles.CREATOR.name.lower()).gino.first()

            # create project
            project = await Project(name=project_name, access_token=token).create()

            # set creator role in project
            association = UsersToProjects(user_id=user_id, project_id=project.id, role_id=creator_role.id)
            await association.create()

            # add default tag
            default_tag = Tag(name="Default", project_id=project.id)
            await default_tag.create()

        await redis.delete(redis_key)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id)
        await message.answer(
            f"Project {project_name} was successfully created!\n" f"You can now browse it in 'My projects'",
            reply_markup=return_markup,
        )
        logger.info("Created new project with additional info", extra={"project_name": project_name})

    return create_project


def make_join_to_project_handler(redis: Redis) -> Callable[[CallbackQuery], Coroutine[None, None, None]]:
    async def set_join_to_project_state(query: CallbackQuery) -> None:
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])

        chat_id = int(query.message.chat.id)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id)
        await query.message.edit_text("Please, enter token of a project you want join to:")
        await query.message.edit_reply_markup(reply_markup=return_markup)

        # set fsm to join to project dialog and save user data to redis
        redis_data = JoinToProjectData(user_id=user_id)
        await redis.set(make_redis_joining_key(chat_id), redis_data.json())

    return set_join_to_project_state


def make_join_to_project_callback(redis: Redis) -> Callable[[Message], Coroutine[None, None, None]]:
    async def join_to_project(message: Message) -> None:
        token = message.text
        chat_id = message.chat.id

        redis_key = make_redis_joining_key(chat_id)

        user_data = await redis.get(redis_key)
        parsed_user_data = JoinToProjectData(**json.loads(user_data))
        user_id = parsed_user_data.user_id

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id)

        project = await Project.query.where(Project.access_token == token).gino.first()
        # Project not found handling
        if project is None:
            await message.answer(f"Wrong access token. Try again:", reply_markup=return_markup)
            return

        user_role = await Role.query.where(Role.type == UserRoles.USER.name.lower()).gino.first()

        already_joined = await UsersToProjects.query.where(
            (UsersToProjects.project_id == project.id) & (UsersToProjects.user_id == user_id)
        ).gino.first()
        if already_joined:
            await message.answer(f"You are already joined to {project.name} project.", reply_markup=return_markup)
            return

        association = UsersToProjects(user_id=user_id, project_id=project.id, role_id=user_role.id)
        await association.create()

        await redis.delete(redis_key)
        await message.answer(f"You successfully joined to {project.name} project!", reply_markup=return_markup)
        logger.info(f"User {user_id} joined to project {project.id}")

    return join_to_project
