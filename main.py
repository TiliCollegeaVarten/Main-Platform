from fastapi import FastAPI, responses, Request, status, Response, staticfiles
import aiosqlite
import sqlite3

app = FastAPI()
app.mount("/site", staticfiles.StaticFiles(directory="site", html=True), name="site")


@app.on_event("startup")
async def startup():
    db = await aiosqlite.connect("database/answer_submissions.sqlite")
    db.row_factory = sqlite3.Row
    app.state.db = db


@app.on_event("shutdown")
async def startup():
    await app.state.db.commit()
    await app.state.db.close()


@app.post("/roll")
async def roll_no_submit(request: Request, response: Response):
    """POST for submitting the roll number
    If roll number is not an integer, return status 406 and error json
    If roll exists, return status 202 and already submitted answers as json in
        {"question_$num": "answer"} form, if no answer, return empty json
    If roll doesn't exist, insert roll into db and return 201 with empty json
    """
    db = app.state.db
    data = await request.json()
    try:
        roll_no = int(data["roll_no"])
    except ValueError:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"error": "Given roll number is not valid"}

    db_roll_row = await db.execute(
        "select * from answer_submissions where roll_no=?", (roll_no,)
    )
    db_roll_row = await db_roll_row.fetchall()
    db_roll_row = [dict(i) for i in db_roll_row]

    if db_roll_row:  # False if empty
        prefilled_answers = {}
        current_row = db_roll_row[0]
        for question_num in current_row:
            if (
                current_row[question_num] is not None
            ):  # Checking if the answer is not None
                prefilled_answers[question_num] = current_row[question_num]
        response.status_code = status.HTTP_202_ACCEPTED
        return prefilled_answers
    else:
        await db.execute(
            "insert into answer_submissions (roll_no) values (?)", (roll_no,)
        )
        await db.commit()
        response.status_code = status.HTTP_201_CREATED
        return {}


# @app.post("/submit")
# async def answer_submit(request: Request, response: Response):
#     data = await request.json()
#     db = app.state.db

#     await db.execute("insert into answer_submissions (roll_no) values (?)", (data[0],))
#     await db.commit()
#     response.status_code = status.HTTP_201_CREATED
#     return {"done": "done"}


@app.get("/")
async def test():
    return responses.FileResponse("index.html")
