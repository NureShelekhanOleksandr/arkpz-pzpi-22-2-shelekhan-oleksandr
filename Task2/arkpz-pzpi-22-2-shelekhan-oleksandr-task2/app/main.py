from fastapi import FastAPI
import uvicorn
from app.routers import user, login, property, booking, payment

app = FastAPI()

app.include_router(user.router)
app.include_router(login.router)
app.include_router(property.router)
app.include_router(booking.router)
app.include_router(payment.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
