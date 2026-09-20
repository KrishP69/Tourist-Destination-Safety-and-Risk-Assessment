from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..database import get_db
from ..models.schemas import UserRegister, UserLogin, UserOut, TokenResponse
from ..auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication & Travelers"])

def get_badge_title(xp: int) -> str:
    if xp >= 1000:
        return "Bharat Trail Master"
    elif xp >= 500:
        return "Trail Guardian"
    elif xp >= 250:
        return "Field Scout"
    return "Verified Explorer"

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister):
    with get_db() as conn:
        cursor = conn.cursor()
        email_clean = payload.email.strip().lower()
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email_clean,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists. Please sign in."
            )
        
        # Generate username if not provided
        username = payload.username.strip() if payload.username else email_clean.split("@")[0]
        cursor.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        if cursor.fetchone():
            username = f"{username}_{int(datetime.now().timestamp()) % 10000}"

        hashed = hash_password(payload.password)
        cursor.execute("""
            INSERT INTO users (full_name, email, username, password_hash, role, reputation_xp, home_city)
            VALUES (?, ?, ?, ?, 'tourist', 100, ?)
        """, (payload.full_name.strip(), email_clean, username, hashed, payload.home_city or "India"))
        
        user_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT id, full_name, email, username, role, reputation_xp, home_city, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        badge = get_badge_title(row["reputation_xp"])
        user_out = UserOut(
            id=row["id"],
            full_name=row["full_name"],
            email=row["email"],
            username=row["username"],
            role=row["role"],
            reputation_xp=row["reputation_xp"],
            reputation_badge=badge,
            home_city=row["home_city"],
            created_at=str(row["created_at"])
        )

        token = create_access_token({"sub": str(user_out.id), "email": user_out.email, "name": user_out.full_name, "role": user_out.role})
        return TokenResponse(access_token=token, user=user_out)

@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin):
    with get_db() as conn:
        cursor = conn.cursor()
        email_clean = payload.email.strip().lower()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email_clean,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password credentials."
            )
        
        if not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password credentials."
            )
        
        badge = get_badge_title(row["reputation_xp"])
        user_out = UserOut(
            id=row["id"],
            full_name=row["full_name"],
            email=row["email"],
            username=row["username"],
            role=row["role"],
            reputation_xp=row["reputation_xp"],
            reputation_badge=badge,
            home_city=row["home_city"],
            created_at=str(row["created_at"])
        )
        token = create_access_token({"sub": str(user_out.id), "email": user_out.email, "name": user_out.full_name, "role": user_out.role})
        return TokenResponse(access_token=token, user=user_out)

@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, username, role, reputation_xp, home_city, created_at FROM users WHERE id = ?", (current_user["id"],))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return UserOut(
            id=row["id"],
            full_name=row["full_name"],
            email=row["email"],
            username=row["username"],
            role=row["role"],
            reputation_xp=row["reputation_xp"],
            reputation_badge=get_badge_title(row["reputation_xp"]),
            home_city=row["home_city"],
            created_at=str(row["created_at"])
        )

@router.get("/leaderboard", response_model=List[UserOut])
def get_top_contributors():
    """Returns top travel guardians with highest field verification reputation XP."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, full_name, email, username, role, reputation_xp, home_city, created_at
            FROM users
            ORDER BY reputation_xp DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        return [
            UserOut(
                id=r["id"],
                full_name=r["full_name"],
                email=r["email"][:3] + "***@" + r["email"].split("@")[-1] if "@" in r["email"] else r["email"],
                username=r["username"],
                role=r["role"],
                reputation_xp=r["reputation_xp"],
                reputation_badge=get_badge_title(r["reputation_xp"]),
                home_city=r["home_city"],
                created_at=str(r["created_at"])
            )
            for r in rows
        ]
