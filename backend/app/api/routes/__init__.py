from fastapi import APIRouter

from app.api.routes import auth, job, resume, candidate, analytics

# Central application Router hooking individual module paths
router = APIRouter()

router.include_router(auth.router)
router.include_router(resume.router)
router.include_router(job.router)
router.include_router(candidate.router)
router.include_router(analytics.router)
