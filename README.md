
# FastAPI Backend Code Structure

Repository housing code for FastAPI backend

## **Code Structure**

Please follow the below mentioned directory structure

```yaml
.
├── .git
├── .env
├── .cz.toml
├── .flake8
├── .gitignore
├── .isort.cfg
├── .pre-commit-config.yaml
├── .pylintrc
├── .mypy.ini
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── response_schemas/
│   │   ├── __init__.py
│   │   └── example.json
│   └── server/
│       ├── config/
│       │   ├── __init__.py
│       │   └── config.py
│       ├── document/
│       │   ├── __init__.py
│       │   └── metadata.py
│       ├── encoder/
│       ├── handler/
│       ├── logger/
│       ├── middlewares/
│       ├── models/
│       ├── routes/
│       │   └── __init__.py
│       ├── services/
│       │   └── __init__.py
│       ├── static/
│       │   ├── __init__.py
│       │   ├── constants.py
│       │   └── enums.py
│       ├── templates/
│       │   ├── __init__.py
│       │   └── example.html
│       └── utils/
├── docs/
├── env/
└── tests/
```

## Setup environment variables

Create a new environment file .env and at it to the parent directory

> PORT=4000
>
> LOG_LEVEL=DEBUG
>
> JWT_SECRET=
>
> DOC_USERNAME=admin
>
> DOC_PASSWORD=admin
>
> MONGO_URI=mongodb://localhost:27017/test-dev
>
> AWS_REGION=ap-south-1
>
> AWS_ACCESS_ID=
>
> AWS_SECRET_KEY=
>
> AWS_STORAGE_BUCKET=
>
> AWS_S3_PRESIGNED_EXPIRATION=900
>
> EMAIL_SENDER=
>

## Using Pre-commit with Your GitHub Repository

Pre-commit is a useful tool that allows you to run various checks and tasks before each commit in your Git repository. This helps maintain a consistent codebase and ensures that certain checks are always performed, such as linting, formatting, and code quality analysis.

To use pre-commit with your GitHub repository, follow these steps:

### Step 1: Install Pre-commit

Using pip:

```bash
pip install pre-commit
```

Using homebrew:

```bash
brew install pre-commit
```

### Step 2: Install the git hook scripts

```bash
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

Install Commitzen

```bash
$ pre-commit install --hook-type commit-msg
pre-commit installed at .git/hooks/commit-msg
```

Commitzen requires the commit messages to be in particular format so please enter a commit message in the commitizen format.

> commit "feat": "Added auth apis"
>
> pattern: (?s)(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)(\(\S+\))?!?:( [^\n\r]+)((\n\n.*)|(\s*))?$
>

Now pre-commit will run automatically on git commit!

### Step 3: Commit and Push

Now, whenever you make a new commit, the pre-commit hooks will automatically run and check your code against the specified rules. If any issues are found, the commit will be aborted, allowing you to fix the problems before proceeding.

Commit your changes as usual and push them to your GitHub repository.

## Export all package licenses

```bash
pip-licenses --with-authors --format=markdown --output-file=docs/licenses.md
```

## Poetry as your package manager

Install (Linux, macOS, Windows (WSL))

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

---
> On some systems, python may still refer to Python 2 instead of Python 3. We always suggest the python3 binary to avoid ambiguity.
---

Install (Windows (Powershell))

```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

---
> If you have installed Python through the Microsoft Store, replace py with python in the command above.
---

Add to bash profile (Mac)

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add poetry to your existing project

```bash
poetry init
```

Creating a new project with poetry set-up

```bash
poetry new <project_name>
```

Use an existing requirements.txt file for existing project

```bash
poetry add `cat requirements.txt`
```

---
> **External virtual environment management**
Poetry will detect and respect an existing virtual environment that has been externally activated. This is a powerful mechanism that is intended to be an alternative to Poetry’s built-in, simplified environment management.
To take advantage of this, simply activate a virtual environment using your preferred method or tooling, before running any Poetry commands that expect to manipulate an environment.
---

Get path of existing virtual environment you are in

```bash
poetry env info --path
```

To install the defined dependencies for your project, just run the install command

```bash
poetry install
```

Add new dependency

```bash
poetry add requests==2.31.0
```

Update dependencies

```bash
poetry update
```

Remove Dependency (The remove command removes a package from the current list of installed packages)

```bash
poetry remove requests
``````

Update specific dependencies:

```bash
poetry update requests
```

Add dev dependency (To explicitly tell Poetry that a package is a development dependency, you run poetry add with the --dev option. You can also use a shorthand -D option, which is the same as --dev)

```bash
poetry add black -D
```

## Using the PROXY_API_PREFIX Environment Variable

The `PROXY_API_PREFIX` environment variable is designed to assist in configuring proxy servers when running multiple services under the same domain. This variable allows the proxy server to distinguish between different services based on their paths and route the requests accordingly.

### Why Use PROXY_API_PREFIX?

When you have multiple services running on the same domain, a proxy server like Nginx will need to know how to route incoming HTTP requests to the correct service. Setting the `PROXY_API_PREFIX` variable allows you to specify a unique path prefix for each service, aiding the proxy server in routing the requests.

### How to Set PROXY_API_PREFIX

Set the `PROXY_API_PREFIX` environment variable with the desired path prefix. For example, if you want to set the path prefix for "Service A" to `/serviceA`, you can set the environment variable like so:

```bash
export PROXY_API_PREFIX=/serviceA
```

### Nginx Configuration Example

Here's an example Nginx configuration snippet that uses `PROXY_API_PREFIX` to route requests to "Service A":

```nginx
server {
    listen 80;
    server_name _;

    location ~ ^/serviceA(/.*)?$ {
        rewrite ^/serviceA(/.*)?$ $1 break;
        proxy_pass http://fastapi_backend:4000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

}
```

In this example, requests to `http://your-domain.com/serviceA/...` will be routed to "Service A" running on `serviceA_backend:4000`.

### Running without PROXY_API_PREFIX

If the `PROXY_API_PREFIX` is not set, the service will run without any path prefix, and you can access it directly using its base URL.

## Performance Testing with Locust

We use [Locust](https://locust.io/) for performance testing of our REST APIs. Locust allows us to simulate multiple users and their actions, thereby providing insights into how our system performs under various loads.

### Why Locust?

- **Ease of Use**: Written in Python, it's quick to set up and easy to script custom scenarios.
- **Real-Time Metrics**: Provides a real-time web UI for monitoring.
- **Distributed Testing**: Supports distributed testing to simulate a larger number of users.

### Quick Start

1. **Install Locust**:

    ```bash
    pip install locust
    ```

2. **Run Locust**:

    ```bash
    locust -f your_locust_file.py
    ```

    This starts the Locust web UI, usually at <http://localhost:8089>.

3. **Start Testing**:
    - Input the number of users and spawn rate in the web UI.
    - Start the test and observe real-time metrics.

For a detailed guide on setting up and running performance tests, please refer to our [Locust Performance Testing Guide](docs/performance.md).
