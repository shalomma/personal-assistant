import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/connect")
async def connect_wifi(request: Request):
    # Implement your logic here, such as connecting to the Wi-Fi network
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    return {"message": "Connecting..."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
