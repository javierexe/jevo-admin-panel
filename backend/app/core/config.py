from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Configuration
    VITE_API_URL: str = "http://localhost:8000"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Cloudinary (optional)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Upload Configuration
    UPLOAD_STORAGE: str = "local"  # Options: local, cloudinary
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Admin UI credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # Cloud API configuration
    CLOUD_API_URL: str  # Required: Base URL for Cloud API (e.g., http://localhost:8001)
    CLOUD_API_ADMIN_TOKEN: str  # Required: Bearer token for Cloud API admin endpoints
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
