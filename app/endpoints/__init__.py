from fastapi.routing import APIRouter

from app.endpoints.tasks import delete_task_router, get_task_router, post_task_router
from app.endpoints.users import post_user_router, get_user_router

main_router = APIRouter(prefix="/api")

main_router.include_router(delete_task_router)
main_router.include_router(get_task_router)
main_router.include_router(post_task_router)
main_router.include_router(post_user_router)
main_router.include_router(get_user_router)
