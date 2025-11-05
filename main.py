from fastapi import FastAPI


from src.roles.service import RolesService
from src.users.router import users_router
from src.auth.router import auth_router
from src.users.service import UsersService
from src.users_roles.router import users_roles_router
from src.roles.router import roles_router
from src.db.connection import AsyncSessionDepends, create_db_tables
from tasks.router import celery_router
from src.users_roles.service import UsersRolesService


app = FastAPI()


@app.get('/refresh', tags=["danger"], summary="Rebuilds database with one admin user")
async def refresh_db(session: AsyncSessionDepends):
    """
    Rebuilds database with one admin user. 

    Be aware of using it. This endpoint deletes all data

    This is `костыль` for creating project. 
    I agree that project startup is nasty.
    """
    await create_db_tables()

    await RolesService.insert_default_roles(session)

    resp = await UsersService.add_main_admin(session)

    assert resp is not None

    await UsersRolesService.add_main_admin_roles(session, resp.user_id)

    await session.commit()

    return "API ready for use"


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(users_roles_router)
app.include_router(roles_router)
app.include_router(celery_router)