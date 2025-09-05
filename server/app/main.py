from fastapi import FastAPI
from app.routes import auth_routes, note_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Notes App API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# include routers
app.include_router(auth_routes.router)
app.include_router(note_routes.router)

@app.get("/")
def root():
    return {"message": "FastAPI Notes App Backend Running 🚀"}
