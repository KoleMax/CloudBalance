from aiogram.types import CallbackQuery

from application.models import Project, UsersToProjects
from application.telegram.menu.main.handlers import projects_handler
from application.telegram.menu.project.renderers import ProjectMenuRenderer


async def return_handler(query: CallbackQuery):
    await projects_handler(query)


async def project_menu_handler(query: CallbackQuery):
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])
    project_id = int(parsed_query_data[2])

    project = await Project.query.where(Project.id == project_id).gino.first()
    user_role_id = await UsersToProjects.get_user_role_id_in_project(user_id, project_id)

    project_menu_markup = ProjectMenuRenderer(user_id, user_role_id, project_id, project.name)()
    await query.message.edit_text(f"{project.name} menu.")
    await query.message.edit_reply_markup(reply_markup=project_menu_markup)
