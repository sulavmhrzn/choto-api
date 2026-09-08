MIN_SHORT_CODE_LENGTH = 3
MAX_SHORT_CODE_LENGTH = 50

RESERVED_SHORT_CODES = {
    "admin",
    "admin-tipbba",
    "api",
    "auth",
    "accounts",
    "links",
    "login",
    "logout",
    "signup",
    "register",
    "static",
    "media",
    "health",
    "docs",
    "swagger",
    "redoc",
}

SHORT_LINK_ORDERING_CHOICES = [
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
    "title",
    "-title",
]
