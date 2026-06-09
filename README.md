# Amazon Playwright Assignment

Automated Amazon add-to-cart tests built with Python, Playwright, and pytest.

The suite covers:

- Test Case 1: search Amazon.com for an iPhone, open a selected device, print its price, and add it to the cart.
- Test Case 2: search Amazon.com for a Samsung Galaxy device, open a selected device, print its price, and add it to the cart.
- Parallel execution: both tests run concurrently with `pytest-xdist` using two workers.
- Bonus: optional LambdaTest cloud execution through environment variables.

## Tech Stack

- Language: Python
- Framework: Playwright
- Test runner: pytest
- Parallelism: pytest-xdist
- Optional cloud provider: LambdaTest

## Project Structure

```text
.
├── conftest.py
├── pages/
│   ├── amazon_home_page.py
│   ├── product_page.py
│   └── search_results_page.py
├── tests/
│   ├── test_galaxy.py
│   └── test_iphone.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Run Locally

Run both tests in parallel:

```bash
pytest
```

The default options are configured in `pytest.ini`:

```ini
addopts = -n 2 -s -v
```

The `-n 2` flag runs the iPhone and Galaxy tests in parallel, and `-s` keeps console output visible so the selected device prices are printed.

To run headless:

```bash
HEADLESS=true pytest
```

To run a single test:

```bash
pytest tests/test_iphone.py
pytest tests/test_galaxy.py
```

## LambdaTest Cloud Execution

Create a `.env` file in the project root:

```bash
RUN_ON_LT=true
LT_USERNAME=your_lambdatest_username
LT_ACCESS_KEY=your_lambdatest_access_key
HEADLESS=true
```

Then run:

```bash
pytest
```

When `RUN_ON_LT=true`, the fixture in `conftest.py` connects Playwright to LambdaTest using the configured credentials.

## Notes

- Amazon may occasionally show CAPTCHA or bot-detection pages during automation. If that happens locally, rerun in headed mode with `HEADLESS=false`.
- Failure screenshots and HTML snapshots are written as `iphone_failure.*` or `galaxy_failure.*` to help debug page-state issues.
