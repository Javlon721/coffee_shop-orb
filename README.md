## To run this project, you have this options:

## Run entire project with Docker:

- In terminal:
    
    ```
    docker compose up -d
    ```
    
- Connect to API via [http://0.0.0.0:8000/](http://0.0.0.0:8000/users/)

---

### Note:

You MUST trigger GET endpoint [http://0.0.0.0:8000/refresh](http://0.0.0.0:8000/users/refresh) to initialize database tables and default user

---

### Default user is:

- You can find `admin credentials` in `.env` files (change them according to method you chose to run project), which look like this:
    
    ```
    #Admin credentials
    ADMIN_EMAIL=admin@mail.ru
    ADMIN_PASSWORD=qwerty
    ```
    

## Run project manually:

### Install python modules:

- In terminal:
    
    ```
    Create .venv folder for local modules
    
    python3 -m venv .venv  
    ```
    
    ```
    Activate .venv folder
    
    source .venv/bin/activate
    ```
    
    ```
    Install all modules
    
    pip install -r requirements.txt
    ```
    
    ### Note:
    
    I am using `macOS` so if you use different OS then change some commands in terminal, like: python3 to python etc…
    

### Run only databases (with celery tasks) with Docker:

- In terminal:
    
    ```
    docker compose up celery_worker celery_beat -d
    ```
    
    It automaticly starts all databases, because `celery_worker` and `celery_beat` services depends op `db` and `redis`
    

### Run only databases (without celery tasks) with Docker:

- In terminal:
    
    ```
    docker compose up db redis -d
    ```
    
- Then you need to manually start celery tasks:
    
    ```
    celery -A auto_deletions.celery_app worker -l info
    celery -A auto_deletions.celery_app beat -l info
    ```
    

### And start the API:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

### To run tests:

### Note:

Please do not run all tests together because `api_test.py` and `module_test.py` will conflict with each other

---

- In terminal start database for tests
    
    ```
    docker compose -f docker-compose-test.yaml up -d
    ```
    
- And run specific test
    
    ```
    PYTHONPATH=. pytest tests/api_test.py
    ```
    
    ```
    PYTHONPATH=. pytest tests/module_test.py
    ```
    
    ```
    PYTHONPATH=. pytest tests/unit_test.py
    ```
    
    ### Note:
    
    Make sure to add `PYTHONPATH=.` env variable before running any of tests. It correctly will resolve all import paths.
    

## Project structure

Some documentations are omited. I believe that name of functionality should tell what is happening). Mostly i managed functions with DI help.

There are many ways to structure a project, however i choose this common pattern:

```
├── module
│   ├── config.py
│   ├── dependencies.py
│   ├── models.py
│   ├── repository.py
│   ├── router.py
│   ├── utils.py
│   └── etc...
```

`config`  has all variables that module depends on

`dependencies` are functions that can be injected to other functions/methods, etc…

`models` are Pydantic and SQLAlchemy models

`router` has all endpoints of concrete module, i.e users CRUD endpoints

`utils` are common functions that can be used by any other modules including parent one

`repository` is center of database to api managment system

Then we have separate module for testing and celery tasks:

```
├── auto_deletions
│   ├── celery_app.py
│   ├── config.py
│   ├── raw_data.py
│   └── router.py
├── tests
│   ├── api_test.py
│   ├── module_test.py
│   └── unit_test.py
```

I created not all tests though, but listed examples of what other tests would look like :) 

And also, please do not judge me because of code repetitions, it can be managed in the future. Thx!)

I left the `sql` module out for simplicity, so you can see what the database looks like.

So if we look to the project we can observe this hierarchy:

```
├── auth
│   ├── config.py
│   ├── dependencies.py
│   ├── models.py
│   ├── router.py
│   ├── utils.py
│   └── verification
│       ├── models.py
│       └── repository.py
├── auto_deletions
│   ├── celery_app.py
│   ├── config.py
│   ├── raw_data.py
│   └── router.py
├── db
│   ├── config.py
│   ├── connection.py
│   └── models.py
├── roles
│   ├── models.py
│   ├── repository.py
│   └── router.py
├── sql
│   ├── roles.sql
│   ├── users_roles.sql
│   ├── users.sql
│   └── verifications.sql
├── tests
│   ├── api_test.py
│   ├── module_test.py
│   └── unit_test.py
├── users
│   ├── models.py
│   ├── repository.py
│   └── router.py
├── users_roles
│   ├── models.py
│   ├── repository.py
│   └── router.py
└── utils
    ├── models.py
    └── utils.py
├── docker-compose.yaml
├── .dockerignore
├── DockerFile
├── main.py
├── Makefile
├── README.md
├── requirements.txt
```