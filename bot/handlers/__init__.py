from aiogram import Router

from . import cmds, new_order

router = Router()

router.include_routers(cmds.router)
router.include_router(new_order.router)
