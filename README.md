<h1 align="center">Todolist</h1>

## 📖 About

Todolist is a task manager and to-do list app.

## 💾 Installation

```
$ git clone https://github.com/YuZu-original/todolist.git
```

or [download](https://github.com/YuZu-original/todolist/archive/refs/heads/master.zip) zip archive.

### 🧾 Requirements

- Python3.10
- Pip
- Docker

## 🛠 Setup

1. **Go to the folder.**
   
   Open folder in the terminal.

2. **Create and activate venv.**

    **Windows**:
    
    ```sh
    python -m venv venv
    venv\Scripts\activate
    ```
    
    **Linux/MacOS**
    
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
3. **Install requirements**
   
   ```sh
   pip install -r requirements.txt
   ```

## 🕹 Usage

Create postgresql docker container.

```sh
docker run --name todolist_postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

And run server:
- Linux\MacOS: `python3 manage.py runserver`
- Windows: `python manage.py runserver`

Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**