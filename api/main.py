# uvicorn api.main:app --reload
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.endpoints import articles, sentiments, media

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from endpoint modules
app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(sentiments.router, prefix="/sentiments", tags=["sentiments"])
app.include_router(media.router, prefix="/media", tags=["media"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Transparency API"}