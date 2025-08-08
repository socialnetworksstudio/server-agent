"""
agent.py - Simple FastAPI-based remote command execution service.

This script starts a FastAPI application exposing a single `/run` endpoint.
Clients must provide a valid `token` matching the server's `SECRET` to
authenticate.  The `cmd` parameter is executed on the host using the
system shell, and the exit code, standard output, and standard error
are returned as a JSON object.  To prevent abuse, the command is
limited to a 60‑second timeout.

Example usage:

```
SECRET=super‑secret uvicorn agent:app --host 127.0.0.1 --port 8085
```

Then call:

```
http://localhost:8085/run?token=super‑secret&cmd=whoami
```

This will return a JSON object with the result.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import os

app = FastAPI()

# Secret token used to authenticate API requests.  Override this
# environment variable at runtime.  Never hard‑code secrets in source
# code.  If the token is missing, the API will generate a default
# value which should be replaced.
SECRET = os.getenv("SECRET", "change-me")


@app.get("/run")
async def run(cmd: str, token: str) -> JSONResponse:
    """
    Execute a shell command on the host and return its exit status and
    output.

    Parameters
    ----------
    cmd : str
        The command string to execute using `bash -c`.  Commands are
        executed with the privileges of the process owner; use with
        caution.
    token : str
        Authentication token.  Must match the server's SECRET.

    Returns
    -------
    JSONResponse
        A JSON response containing ``exit``, ``stdout``, and
        ``stderr`` fields.
    """
    # Verify the secret token matches the configured secret.
    if token != SECRET:
        raise HTTPException(status_code=403, detail="Forbidden: invalid token")

    try:
        # Execute the command via bash.  Capture both stdout and stderr.
        result = subprocess.run(
            ["bash", "-lc", cmd],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return JSONResponse(
            {
                "exit": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
    except subprocess.TimeoutExpired as exc:
        # Timed out commands return exit code 124 and timeout message.
        return JSONResponse(
            {
                "exit": 124,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "Command timed out",
            }
        )
    except Exception as exc:
        # Return generic error information for unexpected exceptions.
        return JSONResponse(
            {
                "exit": 1,
                "stdout": "",
                "stderr": str(exc),
            }
        )