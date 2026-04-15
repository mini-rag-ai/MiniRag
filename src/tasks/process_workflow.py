import asyncio

from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from celery_app import celery_app,get_setup_utils
from controllers.NLPController import NLPController
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseSignal
import logging
from celery import chain

from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum
from routes.schemas.data import ProcessRequest
from tasks.data_indexing import _index_data_content
from tasks.file_processing import process_project_files

logger = logging.getLogger('__name__')

@celery_app.task(bind=True,name = "tasks.process_workflow.push_after_process_task",
                 auto_retry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def push_after_process_task(self,prev_task_result):
    project_id = prev_task_result.get('project_id')
    do_reset = prev_task_result.get('do_reset')
    task_result = asyncio.run(
        _index_data_content(self,project_id ,do_reset)
    )

    return {
        "signal": ResponseSignal.INDEXING_TASK_TRIGGERED.value,
        "indexing_task_id": task_result,
        "project_id": project_id,
        "do_reset": do_reset
    }



@celery_app.task(bind=True,name = "tasks.process_workflow.process_and_push",
                 auto_retry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})


def process_and_push_workflow(self,project_id: int, file_id: int,
                               chunk_size: int, overlap_size: int, do_reset: bool):
    workflow = chain(
        process_project_files.s(project_id, file_id, chunk_size, overlap_size, do_reset),
        push_after_process_task.s()
        
        )
    result = workflow.apply_async()
    
    return {
        "signal": ResponseSignal.PROCESSING_TASK_TRIGGERED.value,
        "workflow_id": result.id,
        "tasks":[
            "tasks.file_processing.process_project_files",
            "tasks.data_indexing.index_data_content"
        ]
    }