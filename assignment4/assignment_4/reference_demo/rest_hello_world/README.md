# RESTful API - Hello World with Python Flask
Implementing a simple RESTful API server using Python Flask.

## Requirements
- Check `pyproject.toml` or `requirements.txt` for Python requirements. Set up with `uv sync`.

> If you are not working with `uv`, then just run `python -m pip install -r requirements.txt`.

## Update OpenAPI Specification File
The `hello_world.yaml` records the API specifications of how the client will interact with the server. We will implement our backend server based on this specification file, but keep in mind that this file does not strictly break our backend implementation upon updates - it is merely a verbal agreement (unless you are generating backend code from the YAML file, as we demonstrate in the next part).

Optionally, we can copy this file into https://editor.swagger.io/, where a Swagger UI page for the API specifications will be rendered for us to examine more easily.

For more information on OpenAPI Specification, check here: https://swagger.io/specification/.

## Implement the Backend Server
Now we have synchronized with other frontend and backend developers on the API design (i.e., the YAML file). As backend developers (in this part), we will now implement a Python Flask server that handles these API functions in the `server.py` file.

To understand how input parameters and request bodies are captured by Flask, check this link: https://flask.palletsprojects.com/en/3.0.x/quickstart/#the-request-object.

## Run and Test the Backend Server
Run the following command to start the backend server at port=`8081`:
```bash
uv run python server.py
```

We are starting the server with `debug=True`, which supports a hot-reloading feature that enables us to update the code changes without stopping the server.

### Testing the Basic Greeting Function
Run:
```bash
curl http://localhost:8081/
```

The output will be:
```bash
{
  "message": "Hello World!"
}
```

### Testing Greeting with Info
Run:
```bash
curl http://localhost:8081/chat/Peter?institution=SUSTech
```

The output will be:
```bash
{
  "message": "Hello Peter from SUSTech!"
}
```

### Testing Multiplication
Run:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"xin": 1.5, "yin": 6}' http://localhost:8081/calculator/mult
```
where we specify to use POST method via `-X` and add a JSON type request body via `-H` (specify format) and `-d` (specify data).

The output will be:
```bash
{
  "result": 9.0,
  "xin": 1.5,
  "yin": 6
}
```

The above commands can all be found in `request.sh` which can be executed using:
```bash
chmod +x request.sh
./request.sh
```

An equivilant set of comands utilising python's requests library can be found in `request.py`. This showcases one method through which REST_API's can be called directly using python.

To run simply use:
```bash
uv run python request.py
```

