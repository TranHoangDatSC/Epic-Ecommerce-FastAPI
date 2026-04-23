from app.core.dependencies import check_admin
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, models
from app.database import get_db
from app.core.dependencies import get_current_admin
from app.crud import admin as crud_admin
from app.crud.moderator import moderator as crud_moderator

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats", response_model=schemas.AdminDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """Get dashboard stats (Admin only)"""
    return crud_admin.get_admin_stats(db)

@router.get("/feedbacks", response_model=List[schemas.SystemFeedbackResponse])
def list_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """List system feedbacks (Admin only)"""
    return crud_admin.get_feedbacks(db, skip=skip, limit=limit)

@router.patch("/feedbacks/{feedback_id}", response_model=schemas.SystemFeedbackResponse)
def update_feedback(
    feedback_id: int,
    status_update: int = Query(..., ge=0, le=2),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """Update feedback status (Admin only)"""
    db_feedback = crud_admin.update_feedback_status(db, feedback_id, status_update)
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback

@router.get("/users", response_model=List[schemas.UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """List users (Admin only)"""
    # Assuming crud_user logic or simple query
    return crud_admin.get_users_list(db, skip=skip, limit=limit)


# ==================== Moderator Management ====================

@router.get("/moderators", response_model=List[schemas.UserResponse])
def list_moderators(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """List all moderators (Admin only)"""
    return crud_moderator.get_moderators(db, include_deleted=include_deleted)

@router.post("/moderators", response_model=schemas.UserResponse)
def create_moderator(
    moderator_data: schemas.UserCreate, 
    db: Session = Depends(get_db), 
    admin: models.User = Depends(get_current_admin)
):
    # Log cho biết ai đang làm gì
    # Sửa thành:
    print(f"DEBUG: Admin ID {admin.user_id} creating moderator: {moderator_data.username}")
    print(f"Admin {admin.email} creating moderator: {moderator_data.username}")
    
    # Kiểm tra quyền Admin (nên nằm ở Middleware nhưng check đây cho an toàn)
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản admin không hoạt động")
        
    try:
        # Chuyển Pydantic sang dict
        mod_dict = moderator_data.model_dump()
        # Đảm bảo role_id = 2
        mod_dict['role_id'] = 2 
        
        # Gọi CRUD
        new_mod = crud_admin.create_moderator(db, mod_dict, admin.user_id)
        
        return new_mod
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")


@router.patch("/moderators/{user_id}/status", response_model=schemas.UserResponse)
def toggle_moderator_status(
    user_id: int, 
    status_update: schemas.UserLockRequest, 
    db: Session = Depends(get_db), 
    admin: models.User = Depends(get_current_admin)
):
    """Lock or unlock a moderator account (Admin only)"""
    try:
        # XÓA HOÀN TOÀN đoạn models.ViolationLog(...) và db.add(new_log) ở đây
        # Vì nó đang gây ra loop nếu bên trong crud_moderator cũng ghi log
        
        is_active = (status_update.action == "unlock")
        
        # Gọi hàm CRUD - Đảm bảo bên trong hàm này chỉ ghi log 1 lần
        updated_moderator = crud_moderator.toggle_moderator_status(
            db, 
            user_id=user_id, 
            is_active=is_active, 
            reason=status_update.reason, 
            admin_id=admin.user_id
        )
        
        db.commit()
        return updated_moderator
    except Exception as e:
        db.rollback()
        print(f"Error toggling status: {str(e)}")
        raise HTTPException(status_code=400, detail="Không thể cập nhật trạng thái.")
        
@router.get("/violation-logs", response_model=list[schemas.ViolationLogResponse])
async def get_violation_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(check_admin)
):
    # Thực hiện JOIN để lấy username của người bị xử lý
    logs = db.query(
        models.ViolationLog.log_id,
        models.ViolationLog.user_id,
        models.ViolationLog.reason,
        models.ViolationLog.action_taken,
        models.ViolationLog.created_at,
        models.User.username.label("username") # Lấy username gán vào label
    ).join(
        models.User, models.ViolationLog.user_id == models.User.user_id
    ).order_by(
        models.ViolationLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return logs
