import asyncio
import csv
import datetime
import itertools
import uuid
from decimal import Decimal
from io import FileIO
from typing import List, Tuple, Coroutine, Callable
from application.telegram.menu.utils import UNHANDLED_PROBLEM_MESSAGE
import pytz
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from fbprophet import Prophet
from pandas import DataFrame
from sqlalchemy.sql import func

from application.config.logging import get_app_logger
from application.db import Database
from application.models import Project, User, UsersToProjects
from application.models import Transaction
from application.telegram.menu.project.renderers import return_button
from application.telegram.menu.tags.renderers import TagsListRenderer
from application.telegram.menu.transactions.renderers import TransactionsMenuRenderer
from application.telegram.menu.users.renderers import UsersListRenderer
from application.telegram.menu.users.shemas import UserInfo, UsersListRenderingInfo
from application.telegram.menu.utils import get_tags_rendering_info

local_tz = pytz.timezone("Europe/Moscow")

logger = get_app_logger()


async def users_handler(query: CallbackQuery) -> None:
    user_id, project_id, project_name = __query_parser(query)

    user_role_id = await UsersToProjects.get_user_role_id_in_project(user_id, project_id)
    if user_role_id is None:
        await query.message.edit_text(UNHANDLED_PROBLEM_MESSAGE)
        return

    project_users: List[Tuple[int, int, str]] = await User.get_by_project_id(project_id)

    users_data = [
        UsersListRenderingInfo(
            button_title=user_data[2],
            callback_data=UserInfo(id=user_data[0], role_id=user_data[1], name=user_data[2]),
        )
        for user_data in project_users
    ]

    projects_markup = UsersListRenderer(
        user_id=user_id, user_role_id=user_role_id, project_id=project_id, project_name=project_name
    )(users_data)
    await query.message.edit_text(f"Here are users of {project_name}.")
    await query.message.edit_reply_markup(reply_markup=projects_markup)


async def tags_handler(query: CallbackQuery) -> None:
    user_id, project_id, project_name = __query_parser(query)

    user_role_id = await UsersToProjects.get_user_role_id_in_project(user_id, project_id)
    if user_role_id is None:
        await query.message.edit_text(UNHANDLED_PROBLEM_MESSAGE)
        return

    tags_data = await get_tags_rendering_info(project_id)

    projects_markup = TagsListRenderer(
        user_id=user_id, user_role_id=user_role_id, project_id=project_id, project_name=project_name
    )(tags_data)
    await query.message.edit_text(f"Here are tags of {project_name}.")
    await query.message.edit_reply_markup(reply_markup=projects_markup)


async def get_token_handler(query: CallbackQuery) -> None:
    user_id, project_id, project_name = __query_parser(query)

    project_token = await Project.get_token(project_id)

    back_to_project_menu_markup = return_button(
        InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name
    )

    await query.message.answer(project_token)
    await query.message.answer("Here is project token", reply_markup=back_to_project_menu_markup)


async def revoke_token_handler(query: CallbackQuery) -> None:
    user_id, project_id, project_name = __query_parser(query)

    new_token = str(uuid.uuid4())

    await Project.update.values(access_token=new_token).where(Project.id == project_id).gino.status()

    back_to_project_menu_markup = return_button(
        InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name
    )

    await query.message.edit_text("Token was successfully updated.")
    await query.message.edit_reply_markup(reply_markup=back_to_project_menu_markup)


async def transactions_handler(query: CallbackQuery) -> None:
    user_id, project_id, project_name = __query_parser(query)

    user_role_id = await UsersToProjects.get_user_role_id_in_project(user_id, project_id)

    if user_role_id is None:
        await query.message.edit_text(UNHANDLED_PROBLEM_MESSAGE)
        return

    markup = TransactionsMenuRenderer(
        user_id=user_id, user_role_id=user_role_id, project_id=project_id, project_name=project_name
    )()

    await query.message.edit_text(f"{project_name} transactions menu")
    await query.message.edit_reply_markup(markup)


def make_quick_report_handler(db: Database) -> Callable[[CallbackQuery], Coroutine[None, None, None]]:
    async def quick_report_handler(query: CallbackQuery) -> None:
        user_id, project_id, project_name = __query_parser(query)

        total_amounts = (
            await db.select([func.sum(Transaction.amount).label("total_amount"), Transaction.type_id])
            .where(Transaction.project_id == project_id)
            .group_by(Transaction.type_id)
            .gino.all()
        )

        total_expense = 0
        total_income = 0

        for amount in total_amounts:
            if amount[1] == 1:
                total_income = amount[0]
            else:
                total_expense = amount[0]

        week_amounts = (
            await db.select([func.sum(Transaction.amount).label("total_amount"), Transaction.type_id])
            .where(
                (Transaction.project_id == project_id)
                & (Transaction.timestamp > datetime.datetime.now() - datetime.timedelta(days=7))
            )
            .group_by(Transaction.type_id)
            .gino.all()
        )

        week_expense = 0
        week_income = 0

        for amount in week_amounts:
            if amount[1] == 1:
                week_income = amount[0]
            else:
                week_expense = amount[0]

        month_amounts = (
            await db.select([func.sum(Transaction.amount).label("total_amount"), Transaction.type_id])
            .where(
                (Transaction.project_id == project_id)
                & (Transaction.timestamp > datetime.datetime.now() - datetime.timedelta(days=30))
            )
            .group_by(Transaction.type_id)
            .gino.all()
        )

        month_expense = 0
        month_income = 0

        for amount in month_amounts:
            if amount[1] == 1:
                month_income = amount[0]
            else:
                month_expense = amount[0]

        back_to_project_menu_markup = return_button(
            InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name
        )

        await query.message.edit_text(
            f"Quick report.\n\n"
            f"Total:\n\tIncomes - {total_income:.2f}\n\tExpenses - {total_expense:.2f}\n\tEarning - {(total_income - total_expense):.2f}\n\n"
            f"Last 7 days:\n\tIncomes - {week_income:.2f}\n\tExpenses - {week_expense:.2f}\n\tEarning - {(week_income - week_expense):.2f}\n\n"
            f"Last 30 days:\n\tIncomes - {month_income:.2f}\n\tExpenses - {month_expense:.2f}\n\tEarning - {(month_income - month_expense):.2f}\n\n"
        )
        await query.message.edit_reply_markup(reply_markup=back_to_project_menu_markup)

    return quick_report_handler


# TODO: refactor
def make_detailed_report_handler(db: Database) -> Callable[[CallbackQuery], Coroutine[None, None, None]]:
    async def quick_report_handler(query: CallbackQuery) -> None:
        user_id, project_id, project_name = __query_parser(query)

        # We do not take current day transactions because day is not over and prediction will not be stable
        statement = db.text(
            f"SELECT date_trunc('day', transactions.timestamp) AS day, sum(transactions.amount) AS per_day_amount, transactions.type_id "
            f"FROM transactions "
            f"WHERE transactions.project_id = {project_id} and date_trunc('day', transactions.timestamp) < date_trunc('day', now()) and date_trunc('day', transactions.timestamp) >= date_trunc('day', now() - interval '30 days') GROUP BY date_trunc('day', transactions.timestamp), transactions.type_id ORDER BY date_trunc('day', transactions.timestamp)"
        )

        transactions_sum: List[Tuple[datetime.datetime, Decimal, int]] = await db.all(statement)

        weekly_income_forecast = 0
        weekly_expense_forecast = 0
        monthly_income_forecast = 0
        monthly_expense_forecast = 0

        if len(transactions_sum) > 14:
            await query.message.answer("Making prediction - it will take some time...")

            loop = asyncio.get_event_loop()
            try:
                income_forecast, expense_forecast = await loop.run_in_executor(
                    None, __make_prediction, transactions_sum
                )
                weekly_income_forecast, monthly_income_forecast = __count_monthly_and_weekly_forecast(
                    income_forecast
                )
                weekly_expense_forecast, monthly_expense_forecast = __count_monthly_and_weekly_forecast(
                    expense_forecast
                )
            # TODO: find out exceptions to catch
            except Exception as e:
                logger.error(f"Error during prediction: {e}")
                await query.message.answer("Making prediction failed.")

        else:
            await query.message.answer("Prediction is not available, because transactions number is too small")

        back_to_project_menu_markup = return_button(
            InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name
        )

        income_transactions_statement = db.text(
            f"SELECT transactions.timestamp as timestamp, transactions.amount as amount, transactions.description as description, tags.name as tag_name FROM transactions JOIN tags on transactions.tag_id = tags.id WHERE transactions.project_id = {project_id} and date_trunc('day', transactions.timestamp) <= date_trunc('day', now()) and date_trunc('day', transactions.timestamp) >= date_trunc('day', now() - interval '30 days') and transactions.type_id = 1 ORDER BY date_trunc('day', transactions.timestamp)"
        )
        income_transactions = await db.all(income_transactions_statement)

        expense_transactions_statement = db.text(
            f"SELECT transactions.timestamp as timestamp, transactions.amount as amount, transactions.description as description, tags.name as tag_name FROM transactions JOIN tags on transactions.tag_id = tags.id WHERE transactions.project_id = {project_id} and date_trunc('day', transactions.timestamp) <= date_trunc('day', now()) and date_trunc('day', transactions.timestamp) >= date_trunc('day', now() - interval '30 days') and transactions.type_id = 2 ORDER BY date_trunc('day', transactions.timestamp)"
        )
        expense_transactions = await db.all(expense_transactions_statement)

        with open("details.csv", "w+", newline="") as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(["Summary", "", "", "", "", "", "Prediction"])
            spamwriter.writerow(["", "Income", "Expense", "Earnings", "", "", "", "Income", "Expense", "Earnings"])

            total_amounts = (
                await db.select([func.sum(Transaction.amount).label("total_amount"), Transaction.type_id])
                .where(Transaction.project_id == project_id)
                .group_by(Transaction.type_id)
                .gino.all()
            )

            total_expense = 0
            total_income = 0

            for amount in total_amounts:
                if amount[1] == 1:
                    total_income = amount[0]
                else:
                    total_expense = amount[0]

            week_amounts = (
                await db.select([func.sum(Transaction.amount).label("total_amount"), Transaction.type_id])
                .where(
                    (Transaction.project_id == project_id)
                    & (Transaction.timestamp > datetime.datetime.now() - datetime.timedelta(days=7))
                )
                .group_by(Transaction.type_id)
                .gino.all()
            )

            week_expense = 0
            week_income = 0

            for amount in week_amounts:
                if amount[1] == 1:
                    week_income = amount[0]
                else:
                    week_expense = amount[0]

            month_amounts = (
                await db.select([func.sum(Transaction.amount).label("total_amount"), Transaction.type_id])
                .where(
                    (Transaction.project_id == project_id)
                    & (Transaction.timestamp > datetime.datetime.now() - datetime.timedelta(days=30))
                )
                .group_by(Transaction.type_id)
                .gino.all()
            )

            month_expense = 0
            month_income = 0

            for amount in month_amounts:
                if amount[1] == 1:
                    month_income = amount[0]
                else:
                    month_expense = amount[0]

            spamwriter.writerow(
                [
                    "Последние 7 дней",
                    f"{week_income:.2f}",
                    f"{week_expense:.2f}",
                    f"{(week_income - week_expense):.2f}",
                    "",
                    "",
                    "Следующие 7 дней",
                    f"{weekly_income_forecast:.2f}",
                    f"{weekly_expense_forecast:.2f}",
                    f"{(weekly_income_forecast - weekly_expense_forecast):.2f}",
                ]
            )
            spamwriter.writerow(
                [
                    "Последние 30 дней",
                    f"{month_income:.2f}",
                    f"{month_expense:.2f}",
                    f"{(month_income - month_expense):.2f}",
                    "",
                    "",
                    "Следующие 30 дней",
                    f"{monthly_income_forecast:.2f}",
                    f"{monthly_expense_forecast:.2f}",
                    f"{(monthly_income_forecast - monthly_expense_forecast):.2f}",
                ]
            )
            spamwriter.writerow(["За все время", f"{total_income:.2f}", f"{total_expense:.2f}", f"{(total_income - total_expense):.2f}"])
            spamwriter.writerow([])

            spamwriter.writerow(["Income", "", "", "", "", "", "Expense"])
            spamwriter.writerow(
                ["Timestamp", "Tag", "Description", "Amount", "", "", "Timestamp", "Tag", "Description", "Amount"]
            )

            for income, expense in itertools.zip_longest(
                income_transactions, expense_transactions, fillvalue=None
            ):
                row = []
                if income:
                    row.append(
                        income[0].replace(tzinfo=pytz.utc).astimezone(local_tz).strftime("%d.%m.%Y %H:%M:%S")
                    )
                    row.append(income[3])
                    row.append(income[2])
                    row.append(f"{income[1]:.2f}")
                else:
                    for _ in range(4):
                        row.append("")
                row.append("")
                row.append("")
                row.append("")
                if expense:
                    row.append(
                        expense[0].replace(tzinfo=pytz.utc).astimezone(local_tz).strftime("%d.%m.%Y %H:%M:%S")
                    )
                    row.append(expense[3])
                    row.append(expense[2])
                    row.append(f"{expense[1]:.2f}")
                spamwriter.writerow(row)
        await query.message.answer_document(FileIO("details.csv", mode="r"))
        await query.message.answer("Detailed report", reply_markup=back_to_project_menu_markup)

    return quick_report_handler


def __make_prediction(
    transactions_sum: List[Tuple[datetime.datetime, Decimal, int]]
) -> Tuple[DataFrame, DataFrame]:

    # TODO: enums
    expense_frame = DataFrame(
        [(t[0].replace(tzinfo=None), t[1]) for t in transactions_sum if t[2] == 2], columns=["ds", "y"]
    )
    income_frame = DataFrame(
        [(t[0].replace(tzinfo=None), t[1]) for t in transactions_sum if t[2] == 1], columns=["ds", "y"]
    )
    m = Prophet()
    m.fit(expense_frame)
    future = m.make_future_dataframe(periods=30)
    expense_forecast = m.predict(future)

    m = Prophet()
    m.fit(income_frame)
    future = m.make_future_dataframe(periods=30)
    income_forecast = m.predict(future)

    return income_forecast, expense_forecast


def __count_monthly_and_weekly_forecast(forecast: DataFrame) -> Tuple[int, int]:
    weekly_forecast = 0
    monthly_forecast = 0
    day = 1
    for _, row in forecast[len(forecast) - 1 : len(forecast) - 31 : -1].iterrows():
        predicted_value = row["yhat"]
        if predicted_value > 0:
            if day <= 7:
                weekly_forecast += predicted_value
            monthly_forecast += predicted_value
        day += 1
    weekly_forecast = int(weekly_forecast)
    monthly_forecast = int(monthly_forecast)
    return weekly_forecast, monthly_forecast


def __query_parser(query: CallbackQuery) -> Tuple[int, int, str]:
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])
    project_id = int(query.data.split(":")[2])
    project_name = query.data.split(":")[3]
    return user_id, project_id, project_name
