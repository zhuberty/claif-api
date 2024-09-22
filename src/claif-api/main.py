from fastapi import FastAPI

app = FastAPI()


@app.get("/accept")
def accept():
    return {"status": 200}


@app.get("/questions")
def questions():
    return {"status": 200}


@app.get("/answers")
def answers():
    return {"status": 200}


@app.get("/engines")
def engines():
    return {"status": 200}


@app.post("/submit")
def submit():
    return {"status": 200}

