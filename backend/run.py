import uvicorn

if __name__ == "__main__":
    # This tells uvicorn to look for the 'app' object inside the 'app/main.py' file.
    # Running it from this script ensures Python knows where to find the 'app' module.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)