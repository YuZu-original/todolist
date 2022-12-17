<h1 align="center">Todolist</h1>

## 📖 About

Todolist is a task manager and to-do list app.

Site: [http://yuzudev.ga/](http://yuzudev.ga/)

## 🛠 Setup

### 🧾 Requirements

- Python3.10
- Pip
- Docker

If you want to use VK login, you must configure `SOCIAL_AUTH_VK_OAUTH2_KEY` and `SOCIAL_AUTH_VK_OAUTH2_SECRET` in `.env`.

## 🕹 Usage

### Build
```
$ docker-compose build
```

### Start
```
$ docker-compose up -d
```

### Stop
```
$ docker-compose down
```

Open **[http://localhost/](http://localhost/)**