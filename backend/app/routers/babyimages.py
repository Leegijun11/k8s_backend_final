from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from datetime import datetime
import uuid
import os

from app.ai.predict import load_inference_model, predict_image

from app.db.scheme.babyimages import BabyImage_Create, BabyImage_Update, BabyImage_Read, BabyImage_Multi_del
from app.services.babyimages import BabyImage_Service

AI_MODEL = load_inference_model()

router=APIRouter(prefix='/babyimages', tags=['BabyImage'])


async def run_ai_and_update_db(i_id: int, imagepath: str):
    try:
        ai_result = await run_in_threadpool(predict_image, AI_MODEL, imagepath)
        
        async for db_session in get_db():
            try:
                update_data = BabyImage_Update(i_label=ai_result)
                
                await BabyImage_Service.services_babyimages_update(
                    db=db_session, 
                    i_id=i_id, 
                    babyimage=update_data
                )
                break
            except Exception:
                await db_session.rollback()
    except Exception:
        pass


@router.post('/multi_create', response_model=list[BabyImage_Read])
async def router_babyimages_multi_create(background_tasks: BackgroundTasks,
                                   b_id: int,
                                   files: list[UploadFile] = File(...),
                                   db: AsyncSession = Depends(get_db)):
    
    today_str = datetime.now().strftime("%Y%m%d")
    imagefolder = f"../images/{b_id}/{today_str}"
    os.makedirs(imagefolder, exist_ok=True)

    image_create_list = []
    saved_file_paths = []

    for file in files:
        origin = os.path.splitext(file.filename)[1]
        save = f"{uuid.uuid4()}{origin}"
        imagepath = f"{imagefolder}/{save}"
        
        contents = await file.read()
        with open(imagepath, "wb") as f:
            f.write(contents)

        data = BabyImage_Create(i_save=save,
                                i_origin=file.filename,
                                i_label="분석 중...",
                                b_id=b_id,
                                i_image=imagepath)
        image_create_list.append(data)
        saved_file_paths.append(imagepath)

    image_data_list = await BabyImage_Service.services_babyimages_multi_create(db, image_create_list)

    for image_data, imagepath in zip(image_data_list, saved_file_paths):
        background_tasks.add_task(
            run_ai_and_update_db, 
            i_id=image_data.i_id,  
            imagepath=imagepath
        )

    return image_data_list


# POST 이미지 등록
@router.post('/create', response_model=BabyImage_Read)
async def router_babyimages_create(background_tasks: BackgroundTasks,
                                   b_id: int,
                                   file: UploadFile = File(...),
                                   db: AsyncSession = Depends(get_db)):
    
    origin = os.path.splitext(file.filename)[1]
    save = f"{uuid.uuid4()}{origin}"
    
    today_str = datetime.now().strftime("%Y%m%d")

    imagefolder=f"../images/{b_id}/{today_str}"
    imagepath=f"{imagefolder}/{save}"
    
    os.makedirs(imagefolder, exist_ok=True)

    contents = await file.read()
    with open(imagepath, "wb") as f:
        f.write(contents)


    data = BabyImage_Create(i_save=save,
                            i_origin=file.filename,
                            i_label="분석 중...",
                            b_id=b_id,
                            i_image=imagepath)
    
    image_data = await BabyImage_Service.services_babyimages_create(db, data)

    background_tasks.add_task(
        run_ai_and_update_db, 
        i_id=image_data.i_id,  
        imagepath=imagepath
    )

    return image_data


# GET 이미지 목록
@router.get('/list', response_model=list[BabyImage_Read])
async def router_babyimages_list(b_id:int, 
                                 i_date:datetime, 
                                 db: AsyncSession=Depends(get_db)):
    return await BabyImage_Service.services_babyimages_list(db, b_id, i_date)


# PUT 이미지 수정
@router.put("/edit", response_model=BabyImage_Read)
async def router_user_update_u_id(update: BabyImage_Update,
                                  i_id:int,
                                  db: AsyncSession = Depends(get_db)):
    return await BabyImage_Service.services_babyimages_update(db, i_id, update)


# DELETE 이미지 삭제
@router.delete("/del")
async def router_babyimages_del(i_id:int,
                                db: AsyncSession = Depends(get_db)):
    return await BabyImage_Service.services_babyimages_del(db, i_id)


# DELETE 다중 이미지 삭제
@router.delete("/multi_del")
async def router_babyimages_multi_del(request: BabyImage_Multi_del,
                                      db: AsyncSession = Depends(get_db)):
    return await BabyImage_Service.services_babyimages_multi_del(db, request.i_ids)