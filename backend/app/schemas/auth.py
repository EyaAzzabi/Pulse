from pydantic import BaseModel, EmailStr, Field


class OtpRequest(BaseModel):
    email: EmailStr


class OtpResponse(BaseModel):
    delivery: str  # "email" | "server_log"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=255)
    organization_name: str = Field(min_length=1, max_length=255)
    otp_code: str = Field(pattern=r"^\d{6}$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    preferred_language: str
    default_currency: str
    timezone: str

    class Config:
        from_attributes = True


class MembershipOut(BaseModel):
    organization_id: str
    organization_name: str
    role: str


class MeResponse(BaseModel):
    user: UserOut
    memberships: list[MembershipOut]
