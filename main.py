from fastapi import FastAPI, responses, Request, status, Response, staticfiles
import aiosqlite
import sqlite3

app = FastAPI()
app.mount("/site", staticfiles.StaticFiles(directory="site", html=True), name="site")
app.mount("/img", staticfiles.StaticFiles(directory="img", html=True), name="img")


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

    POST should be submitted as a json with this structure:
        {"roll_no": $roll_number} where $roll_number is the actual roll number
        as integer, eg. {"roll_no": 34}

    If roll number is not an integer, return status 406 and error json
    If roll exists, return status 202 and already submitted answers as json in
        {"$question_num": "answer"} form, if no answer, return empty json.
        eg. {12: "Program doesn't compile", 16: "hello"}
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
                actual_number = int(
                    question_num.split("_")[-1]
                )  # Splitting to get 3 from question_3
                prefilled_answers[actual_number] = current_row[question_num]
        response.status_code = status.HTTP_202_ACCEPTED
        return prefilled_answers
    else:
        await db.execute(
            "insert into answer_submissions (roll_no) values (?)", (roll_no,)
        )
        await db.commit()
        response.status_code = status.HTTP_201_CREATED
        return {}


@app.post("/submit")
async def answer_submit(request: Request, response: Response):
    """POST for submitting answers

    POST should be submitted as a json with this structure:
        {"roll_no": $roll_number, $question_number: $answer}
        eg. {"roll_no": 18, 1: "None of the above", 5: "24", 8: "Fibonacci"}

    If roll number is not an integer, return status 406 and error json
    If question_num is not a integer or not between 1 and 60, return status
        406 and error json
    If everything is valid, add to db and return status 201 with empty json

    """

    data = await request.json()
    db = app.state.db
    try:
        roll_no = int(data["roll_no"])
    except ValueError:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"error": "Given roll number is not valid"}

    data.pop("roll_no")

    for question_num in data:
        try:
            # To prevent SQL injection and invalid question numbers
            question_num = int(question_num)
            if not (1 <= question_num <= 60):
                raise ValueError("Number not between 1 and 60")
        except ValueError:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return {"error": "question number is not a valid integer between 1 and 60"}

        answer = data[question_num]
        question_col = f"question_{question_num}"
        await db.execute(
            f"insert into answer_submissions (roll_no, {question_col}) values (?, ?)",
            (roll_no, answer),
        )
        await db.commit()
    response.status_code = status.HTTP_201_CREATED
    return {}


@app.get("/")
async def test():
    return responses.FileResponse("index.html")
