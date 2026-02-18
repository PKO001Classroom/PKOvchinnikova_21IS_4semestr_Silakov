from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import students, subjects, grades

# Инициализация БД при запуске
init_db()

# Создание приложения
app = FastAPI(
    title="Grading App API",
    description="API для учёта оценок студентов",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(students.router)
app.include_router(subjects.router)
app.include_router(grades.router)

@app.get("/")
async def root():
    return {
        "message": "Grading App API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}