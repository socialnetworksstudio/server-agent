# Server Agent Control

This repository contains a lightweight HTTP API service for remotely
controlling a Linux server.  The agent uses **FastAPI** to expose a
single endpoint, `/run`, which executes an arbitrary shell command on
the host and returns the result as JSON.  Authentication is handled
via a shared secret passed as a query parameter.

## Features

* **Simple API** – one `GET` endpoint (`/run`) accepts a command and
  secret token, executes the command via `bash`, and returns the
  exit status, standard output and standard error.
* **Configurable secret** – the agent reads a `SECRET` environment
  variable on startup.  Requests with a different `token` value will
  be denied.
* **Timeout** – commands are limited to 60 seconds to prevent runaway
  processes.  Timed‑out commands return exit code 124 and a timeout
  message.
* **Portable** – runs on any modern Linux distribution with Python 3.
* **Easy tunnelling** – combine with Cloudflare's
  `cloudflared` to expose your agent securely over HTTPS without
  managing DNS or port forwarding.

## Usage

### 1. Clone the repository

```bash
git clone https://github.com/socialnetworsstudio/<REPO_NAME>.git
cd <REPO_NAME>
```

### 2. Install dependencies

Create a virtual environment and install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
```

### 3. Set a secret and start the agent

Choose a long, random secret and export it as an environment variable
before running the server.  By default the agent listens on
`localhost:8085`.  You can change the host/port as needed.

```bash
export SECRET="your-long-secret-here"
uvicorn agent:app --host 127.0.0.1 --port 8085
```

### 4. Expose the agent (optional)

If you need to access the agent from the internet, you can use
[Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/run-tunnel/) to create a
public URL without opening firewall ports:

```bash
cloudflared tunnel --url http://127.0.0.1:8085
```

`cloudflared` will output a temporary URL like
`https://example-name.trycloudflare.com`.  Use this URL in place of
`localhost` when making requests.

### 5. Send commands

The API uses a simple query string format.  Supply your secret token
and the command to run as query parameters.  Commands must be URL
encoded.  Example using `curl`:

```bash
curl "http://127.0.0.1:8085/run?token=your-long-secret-here&cmd=uname%20-a"

# Using a Cloudflare tunnel URL:
curl "https://example-name.trycloudflare.com/run?token=your-long-secret-here&cmd=lsblk%20-o%20NAME,SIZE,MODEL"
```

The server responds with JSON:

```json
{
  "exit": 0,
  "stdout": "Linux host 6.11.0-26-generic #26~24.04.1-Ubuntu SMP ...\n",
  "stderr": ""
}
```

## Security considerations

Running this agent with root privileges exposes **full shell access** to
anyone who knows the secret token.  Protect the token carefully and
use HTTPS for all remote access.  For production use, consider
restricting allowed commands or users, and monitor access logs.

## Disclaimer

This project is provided for demonstration and educational purposes.
Use it responsibly and at your own risk.  The authors assume no
liability for misuse or damages.

## Example prompts for ChatGPT

When using this agent via ChatGPT in agent mode, ви можете формувати 
запити для збору інформації про сервер. Ось кілька прикладів, які 
демонструють формат промтів і відповідні shell‑команди, що виконуватиме агент:

- **Отримати інформацію про користувача та версію ядра.**
  
  *Промт:* «Виконай на сервері `whoami` та `uname -a` і поверни результат».
  
  *Результат:* JSON, де `stdout` містить ім’я користувача (наприклад, `root`) та
  рядок з версією ядра Linux.

- **Переглянути інформацію про диски.**
  
  *Промт:* «Дізнайся, які дискові пристрої є на сервері, і виведи список
  їхніх назв та розмірів. Використовуй команду `lsblk -o NAME,SIZE,MODEL`.». 
  
  *Результат:* список блокових пристроїв з їхніми розмірами та моделями
  (наприклад, `sda 111.8G R5SL120G`).

- **Перевірити використання пам’яті.**
  
  *Промт:* «Скільки оперативної пам’яті та swap використовується? Запусти
  `free -h`». 
  
  *Результат:* таблиця з загальним обсягом оперативної пам’яті, використаною
  пам’яттю та доступними ресурсами, а також інформація про swap.

Ці приклади показують, як формулювати завдання: ви описуєте, яку
інформацію хочете отримати, а агент підставляє команду у запит до
ендпоінта `/run` і повертає результат у форматі JSON.