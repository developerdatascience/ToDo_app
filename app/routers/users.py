# Debug endpoint to print all cookies received by the server
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi import Response
from fastapi import status
from app.models.models import User, UserLoginLog
from app.schema import RegisterUserRequest
from app.auth.dependency import register_user
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import datetime, date, timedelta
from typing import Annotated
from app.schema import PasswordChange
from app.auth.dependency import get_current_user, change_password, get_hashed_password, create_access_token
from app.auth.dependency import authenticate_user, get_current_active_user
from app.schema import PasswordChange
from app.auth.dependency import change_password
from app.core.config import settings


router = APIRouter()
templates = Jinja2Templates(directory="templates")

db_dependency = Annotated[Session, Depends(get_db)]

# GET: Render login form
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": None})

# POST: Handle login form
@router.post("/login", response_class=HTMLResponse, status_code=200)
async def login_submit(
    db: db_dependency,
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission"""
    #Authenticate user
    user = authenticate_user(db, email, password)

    if not user:
        return RedirectResponse(
            url="/login?error=Invalid+email+or+password",
            status_code = status.HTTP_303_SEE_OTHER
        )
    
    if user.is_active is not True:
        return RedirectResponse(
            url="/login?error=Account+is+disabled",
            status_code = status.HTTP_303_SEE_OTHER
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data = {"sub": user.email},
        expires_delta = access_token_expires
    )

    login_log= UserLoginLog(user_id=user.id)
    db.add(login_log)
    db.commit()
    db.refresh(login_log)
    response = RedirectResponse(url="/tasks", status_code = status.HTTP_303_SEE_OTHER)


    # Set HTTP-only cookie with token

    response.set_cookie(
        key="access_token",
        value= access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure = True,
        samesite="lax"
    )

    return response






@router.get("/create_account", response_class=HTMLResponse)
async def create_account_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "message": None})

@router.post("/create_account", response_class=HTMLResponse)
async def create_account_submit(
    request: Request,
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(
        (User.email == email) | (User.user_name == username)).first()
    
    if db_user:
        error_msg = ""
        if db_user.email == email:   # type: ignore
            error_msg += "Email already registered"
        if db_user.user_name == username: # type: ignore
            error_msg += "Username already taken"
        return RedirectResponse(
            url=f"/signup?error={error_msg.strip().replace(' ', '+')}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        reg = RegisterUserRequest(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=get_hashed_password(password)
        )
        await register_user(db, reg)
        message = "Account created successfully."
        return templates.TemplateResponse("register.html", {"request": request, "message": message})
    except Exception as e:
        db.rollback()
        message = f"Failed to create account: {str(e)}"
        return templates.TemplateResponse("register.html", {"request": request, "message": message})



# GET: Render change password form
@router.get("/changepassword", response_class=HTMLResponse)
async def change_password_form(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("changepassword.html", {"request": request, "message": None, "user": user})

# POST: Handle change password form
@router.post("/changepassword", response_class=HTMLResponse)
async def change_password_submit(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        password_change = PasswordChange(
            current_password=current_password,
            new_password=new_password,
            new_password_confirm=new_password_confirm
        )
        change_password(db, user.id, password_change)
        message = "Password changed successfully."
        return templates.TemplateResponse("changepassword.html", {"request": request, "message": message, "user": user})
    except Exception as e:
        message = f"Failed to change password: {str(e)}"
        return templates.TemplateResponse("changepassword.html", {"request": request, "message": message, "user": user})


# GET: Render forget password form
@router.get("/forgetpassword", response_class=HTMLResponse)
async def forget_password_form(request: Request):
    return templates.TemplateResponse("forgetpassword.html", {"request": request, "message": None})

# POST: Handle forget password form
@router.post("/forgetpassword", response_class=HTMLResponse)
async def forget_password_submit(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    # Here you would implement sending a reset link or similar logic
    # For now, just show a message
    message = f"If an account with {email} exists, a reset link has been sent."
    return templates.TemplateResponse("forgetpassword.html", {"request": request, "message": message})
# POST: Create account endpoint


# LOGOUT endpoint
@router.post("/logout", response_class=HTMLResponse, status_code=200)
async def logout_user(
     db: db_dependency,
    user = Depends(get_current_active_user)
):
    """
    Handle user logout by:
    1. Recording logout time in UserLoginLog
    2. Clearing authentication cookie
    3. Redirecting to login page
    """
    # Find the most recent login entry withour login time
    login_log = db.query(UserLoginLog).filter(
        UserLoginLog.user_id == user.id,
        UserLoginLog.logout_time.is_(None)
    ).order_by(UserLoginLog.login_time.desc()).first()

    if login_log:
        login_log.logout_time = datetime.now() #type: ignore
        db.add(login_log)
        db.commit()

    response = RedirectResponse(
        url="/login",
        status_code = status.HTTP_303_SEE_OTHER
    )

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
        )

    return response

@router.get("/debug-cookies", response_class=JSONResponse)
async def debug_cookies(request: Request):
    cookies = request.cookies
    print(f"[DEBUG] All cookies received: {cookies}")
    return {"cookies": dict(cookies)}