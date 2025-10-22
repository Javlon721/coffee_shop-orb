from fastapi import FastAPI


app = FastAPI()

@app.get('/test')
def test():
  return "Hello Coffee Shop API"