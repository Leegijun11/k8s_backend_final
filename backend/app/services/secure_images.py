import os
import re
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.access import get_authorized_baby, shares_care_group
from app.db.models.babyimages import BabyImage
from app.db.models.users import User

# main.py에서 쓰던 것과 동일한 기준 경로.
# 이 파일 위치(app/services) 기준 세 단계 위 = main.py가 있는 backend/backend 폴더
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARENT_DIR = os.path.dirname(BASE_DIR)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
IMAGES_DIR = os.path.join(PARENT_DIR, "images")

# "images/{b_id}/{date}/{filename}" 형태만 허용 (b_id는 숫자만)
IMAGES_PATH_PATTERN = re.compile(r'^images/(\d+)/[^/]+/[^/]+$')


def resolve_upload_path(web_style_path: str) -> str:
    """
    DB에 저장된 "/uploads/xxx/파일명.png" 형태의 웹 경로 문자열을
    실제 파일시스템 절대경로로 변환한다. 폴더 구조가 뭐든(baby_images,
    user_images 등) 공통으로 재사용 가능하다.
    """
    web_path = web_style_path.replace("\\", "/")
    web_path = web_path.lstrip("/")  # 맨 앞 슬래시 제거

    if web_path.lower().startswith("uploads/"):
        relative_path = web_path[len("uploads/"):]
    else:
        relative_path = web_path

    filepath = os.path.join(UPLOAD_DIR, relative_path)

    # 방어적 체크: 계산된 경로가 uploads 폴더를 벗어나지 않는지 확인
    safe_base = os.path.realpath(UPLOAD_DIR)
    safe_target = os.path.realpath(filepath)
    if not safe_target.startswith(safe_base):
        raise HTTPException(status_code=400, detail="잘못된 파일 경로입니다")

    return filepath


class SecureImage_Service:

    @staticmethod
    async def get_growth_photo(
        db: AsyncSession,
        u_id: int,
        i_id: int,
    ) -> FileResponse:
        """
        성장 일기 사진 (BabyImage 테이블, images/{b_id}/{date}/ 아래 저장분) 을
        권한 확인 후 반환한다.
        """
        image = await db.get(BabyImage, i_id)
        if image is None:
            raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다")

        baby = await get_authorized_baby(db, u_id, image.b_id)
        if baby is None:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

        # i_image는 업로드 시점에 "../images/{b_id}/{date}/{uuid}.ext" 형태로
        # 저장된 값이다. 저장 당시와 동일한 작업 디렉터리 기준으로 그대로 사용한다.
        if not os.path.exists(image.i_image):
            raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다")

        return FileResponse(image.i_image)

    @staticmethod
    async def get_baby_profile_photo(
        db: AsyncSession,
        u_id: int,
        b_id: int,
    ) -> FileResponse:
        """
        아이 프로필 사진 (Baby.b_image, uploads/baby_images/ 아래 저장분) 을
        권한 확인 후 반환한다.
        """
        baby = await get_authorized_baby(db, u_id, b_id)
        if baby is None:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

        if not baby.b_image:
            raise HTTPException(status_code=404, detail="등록된 프로필 사진이 없습니다")

        filepath = resolve_upload_path(baby.b_image)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다")

        return FileResponse(filepath)

    @staticmethod
    async def get_my_profile_photo(
        db: AsyncSession,
        u_id: int,
    ) -> FileResponse:
        """
        로그인한 본인의 프로필 사진 (User.u_image, uploads/user_images/ 아래 저장분)
        을 반환한다. 본인 것만 조회 가능하도록 u_id를 파라미터로 받지 않고
        인증된 사용자 자신의 정보만 사용한다.
        """
        user = await db.get(User, u_id)
        if user is None:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

        if not user.u_image:
            raise HTTPException(status_code=404, detail="등록된 프로필 사진이 없습니다")

        filepath = resolve_upload_path(user.u_image)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다")

        return FileResponse(filepath)

    @staticmethod
    async def get_partner_profile_photo(
        db: AsyncSession,
        u_id: int,
        target_u_id: int,
    ) -> FileResponse:
        """
        공동 양육자(같은 케어그룹 멤버)의 프로필 사진을 반환한다.
        본인 자신을 조회하는 경우도 허용된다 (shares_care_group에서 처리).
        """
        allowed = await shares_care_group(db, u_id, target_u_id)
        if not allowed:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

        user = await db.get(User, target_u_id)
        if user is None:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

        if not user.u_image:
            raise HTTPException(status_code=404, detail="등록된 프로필 사진이 없습니다")

        filepath = resolve_upload_path(user.u_image)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다")

        return FileResponse(filepath)

    @staticmethod
    async def get_image_by_path(
        db: AsyncSession,
        u_id: int,
        relative_path: str,
    ) -> FileResponse:
        """
        Diary.d_image 처럼 "images/{b_id}/{date}/{filename}" 형태의
        경로 문자열이 통째로 저장되어 있는 경우를 위한 조회.

        경로 자체가 클라이언트에서 넘어오는 값이라, i_id/b_id를 직접 받는
        다른 엔드포인트보다 입력 검증을 엄격하게 한다:
        - 정규식으로 "images/{숫자}/.../..." 형식만 허용 (그 외 전부 거부)
        - b_id를 경로에서 뽑아내 케어그룹 소속 확인
        - 최종 절대경로가 IMAGES_DIR 밖으로 벗어나지 않는지 재확인
        """
        if not relative_path:
            raise HTTPException(status_code=400, detail="잘못된 경로입니다")

        normalized = relative_path.replace("\\", "/")

        # 절대경로(C:/Users/.../images/...)로 들어온 경우, "images/" 부분부터만 취한다
        if "/images/" in normalized:
            normalized = "images/" + normalized.split("/images/", 1)[1]
        else:
            normalized = normalized.lstrip("/")

        match = IMAGES_PATH_PATTERN.match(normalized)
        if not match:
            raise HTTPException(status_code=400, detail="잘못된 경로 형식입니다")

        b_id = int(match.group(1))

        baby = await get_authorized_baby(db, u_id, b_id)
        if baby is None:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다")

        filepath = os.path.join(PARENT_DIR, normalized)

        safe_base = os.path.realpath(IMAGES_DIR)
        safe_target = os.path.realpath(filepath)
        if not safe_target.startswith(safe_base):
            raise HTTPException(status_code=400, detail="잘못된 파일 경로입니다")

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다")

        return FileResponse(filepath)