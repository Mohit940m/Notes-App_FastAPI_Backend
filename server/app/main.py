from fastapi import FastAPI
from app.routes import auth_routes, note_routes


app = FastAPI(title="Notes App API")

# include routers
app.include_router(auth_routes.router)
app.include_router(note_routes.router)

@app.get("/")
def root():
    return {"message": "FastAPI Notes App Backend Running 🚀"}
