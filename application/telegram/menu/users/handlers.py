from aiogram.types import CallbackQuery

from application.models import Project, UsersToProjects
from application.telegram.menu.project.handlers import users_handler
from application.telegram.menu.user.renderers import UserMenuRenderer


async def return_handler(query: CallbackQuery):
    await users_handler(query)


async def user_menu_handler(query: CallbackQuery):
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])
    user_role_id = int(parsed_query_data[2])
    project_id = int(parsed_query_data[3])
    project_name = parsed_query_data[4]
    target_user_id = int(parsed_query_data[5])
    target_user_name = parsed_query_data[6]

    target_user_role_id = await UsersToProjects.get_user_role_id_in_project(target_user_id, project_id)

    project_menu_markup = UserMenuRenderer(user_id, user_role_id, project_id, project_name,
                                           target_user_id, target_user_role_id, target_user_name)()
    await query.message.edit_text(f"{target_user_name} menu.")
    await query.message.edit_reply_markup(reply_markup=project_menu_markup)
