from fastapi import FastAPI, responses, Request, status, Response, staticfiles
import aiosqlite


app = FastAPI()
app.mount("/site", staticfiles.StaticFiles(directory="site", html=True), name="site")


@app.on_event("startup")
async def startup():
    db = await aiosqlite.connect("database/answer_submissions.sqlite")
    app.state.db = db


@app.on_event("shutdown")
async def startup():
    await app.state.db.commit()
    await app.state.db.close()


# @app.post("/submit")
# async def that(request: Request, response: Response):
#     data = await request.json()
#     db = app.state.db
#     await db.execute("insert into answer_submissions (roll_no) values (?)", (data[0],))
#     response.status_code = status.HTTP_201_CREATED
#     return {"done": "done"}


@app.get("/")
async def test():
    return responses.FileResponse("index.html")
