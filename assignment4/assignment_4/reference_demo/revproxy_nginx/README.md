# Reverse Proxy - Nginx
Test load balancing requests to 3 identical Python Flask servers.

## Requirements
- Check `pyproject.toml` or `requirements.txt` for Python requirements. Set up with `uv sync` for different inner directories.

> If you are not working with `uv`, then just run `python -m pip install -r requirements.txt`.

## Configure a Simple Flask Server
Check `flask_app/app.py`. A base URL API is implemented to return a Hello World message marking the server's name.

Check `flask_app/Dockerfile` as well. It uses a lightweight Python image, installs the Python dependencies, and then executes the server.

Build the image in advance for reuse:
```bash
docker pull python:3-slim   # do this if docker build does not work properly
docker build -t flask_app .
```

## Configure Nginx
Check `nginx/nginx.conf`. It simply defines the set of Flask servers to forward requests to. The nginx server will listen on port `80`, using a default round-robin load balancing approach.

## Write the Docker Compose File
Check `compose.yaml`. It defines 3 Python Flask servers and 1 nginx server. The nginx server exposes port `80` to localhost so later we can access the Hello World API via web browser.

## Experiment
Start the docker compose environment via:
```bash
docker compose up -d
```

Now start a web browser and access http://localhost:80/. Refresh the page multiple times to check how the requests are load balanced to different servers in the default round-robin fashion:
```text
Hello from Flask Server 1!
Hello from Flask Server 2!
Hello from Flask Server 3!
Hello from Flask Server 1!
...
```

Besides, `test/clients.py` opens multiple (default=`1000`) threads to send the requests at the same time. Run it to further verify the load balancing behavior:
```bash
cd test
uv run python clients.py
```

The output provides a map to summarize how many requests are handled by each server (server_id => num_requests_handled):
```text
{1: 333, 2: 333, 3: 334}
```

As a final step, try switching to other load balancing methods in the nginx configuration file and test again. Simply modify the file and restart the nginx service container manually without destroying the Flask servers. Note that for `ip-hash`, since requests are sent from the same IP, all requests will be handled by only one of the servers:
```text
{1: 1000}
```
