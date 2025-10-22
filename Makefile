PYTHON := python3
API_PORT := 8000


init: 
	@$(PYTHON) -m venv venv  
	@source venv/bin/activate && pip install -r requirements.txt

install:
	@pip install --no-cache-dir -r requirements.txt

run:
	@uvicorn main:app --reload --port $(API_PORT)
