# Antarctica Data Scientist Challenge

This repository contains my submission for the Antarctica Data Scientist Challenge.

I completed:

* Question 1: GitHub repository scraper GUI with embedded Gemini chatbot
* Question 2: Hedge fund return analysis using multilinear regression and factor analysis

## Project Structure

```text
.
├── q1_1_GUI.py
├── q1_2_chatbot.py
├── q2.py
├── data.xlsx
├── requirements.txt
├── .env.example
├── question_answers.md
└── q2_outputs/
    ├── q2_2_actual_vs_fitted.png
    ├── q2_2_residuals.png
    └── q2_5_rolling_betas.png
```

## Question 1

`q1_1_GUI.py` contains the main GUI application. The user can enter a GitHub username or GitHub profile URL, choose a local file path, and save the public repository names into an Excel file.

The scraper uses `requests` and `BeautifulSoup` to capture the public GitHub repositories page. It does not use the GitHub Python package or the GitHub API.

`q1_2_chatbot.py` contains the Gemini chatbot function. The chatbot is embedded into the GUI and allows users to ask questions about the scraped repository names.

To protect API credential, users can create their own `.env` file using the format shown in `.env.example`:

## Question 2

`q2.py` contains the hedge fund return analysis. It performs:

* Data loading and cleaning
* Multilinear regression
* Alpha and beta estimation
* Model evaluation
* Fund vs factor portfolio profitability comparison
* Sharpe ratio calculation
* Risk comparison
* Rolling beta stationarity tests using ADF and KPSS

The output charts are saved in the `q2_outputs` folder.

## Setup

It is recommended to use a virtual environment so that the project dependencies are installed in an isolated Python environment.

Create a virtual environment:

python -m venv .venv

Activate the virtual environment on Windows:

.venv\Scripts\activate

Install the required Python packages:

pip install -r requirements.txt

## Running Question 1

To run the GitHub repository scraper GUI:

```bash
python q1_1_GUI.py
```

For the Gemini chatbot, create a `.env` file based on `.env.example` and add your own Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The real `.env` file should not be uploaded to GitHub.

## Running Question 2

Make sure `data.xlsx` is in the same folder as `q2.py`, then run:

```bash
python q2.py
```

The script prints the results in the terminal and saves plots into the `q2_outputs` folder.

## AI Usage Declaration

I used AI assistance only for research, debugging, and understanding specific implementation details. This included researching  understanding how GitHub repository names are represented in the page HTML, how to embed a simple chatbot into a GUI and learning how to organise Python code more clearly using OOP principles.

