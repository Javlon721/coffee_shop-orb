from fastapi import FastAPI


from roles.repository import RolesRepository
from users.repository import UsersRepository
from users.router import users_router
from auth.router import auth_router
from users_roles.repository import UsersRolesRepository
from users_roles.router import users_roles_router
from roles.router import roles_router
from db.connection import AsyncSessionDepends, create_db_tables
from auto_deletions.router import celery_router


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

    await RolesRepository.insert_default_roles(session)

    resp = await UsersRepository.add_main_admin(session)

    assert resp is not None

    await UsersRolesRepository.add_main_admin_roles(session, resp.user_id)
    
    return "API ready for use"

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(users_roles_router)
app.include_router(roles_router)
app.include_router(celery_router)