from celery_app import celery_app,get_setup_utils

from helpers.config import get_settings
import asyncio
from controllers.NLPController import NLPController
from controllers import ProcessController

from models import ResponseSignal
import logging

from utils.idempotency_manager import IdempotencyManager
logger = logging.getLogger('__name__')


@celery_app.task(bind=True,name="tasks.maintenance.clean_celery_execution_table",
                 auto_retry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60}
                )

def clean_celery_execution_table(self):

    return asyncio.run(
        _clean_celery_execution_table(self)
    )


async def _clean_celery_execution_table(task_instance):
    db_engine,vectordb_client = None, None
    
    try:
        (db_engine,
            db_client,
            llm_provider_factory,
            vectordb_provider_factory,
            generation_client,
            embedding_client,
            vectordb_client,
            template_parser)= await get_setup_utils()
        
        idempotency_manager = IdempotencyManager(db_client,db_engine)

        _=await idempotency_manager.cleanup_old_tasks()

        return True
        
    except Exception as e:
        logger.error(f"Error cleaning celery execution table: {str(e)}")
        raise e

    finally:
        if db_engine:
            await db_engine.dispose()