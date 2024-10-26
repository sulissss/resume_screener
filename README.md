
# Resume Screener Project

![Resume Screener Logo](https://via.placeholder.com/150)

Welcome to the **Resume Screener Project**, an intelligent system designed to streamline the recruitment process by automatically parsing, analyzing, and ranking resumes based on predefined job descriptions. This project leverages both keyword-based and cosine similarity-based scoring methods, allowing recruiters to choose the most suitable evaluation criteria.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Resume Upload & Management**: Upload, delete, and manage multiple resumes in various formats (PDF, DOCX, TXT).
- **Job Description Handling**: Upload and manage job descriptions, automatically extracting relevant keywords.
- **Flexible Scoring Criteria**: Choose between keyword-based scoring and cosine similarity-based scoring for resume ranking.
- **Fitness Assessment**: Optionally assess the fitness of candidates using a Language Learning Model (LLM).
- **Customizable Weights**: Define and adjust the importance of different resume categories such as education, skills, and experience.
- **Detailed Feedback**: Receive comprehensive feedback on how each resume was evaluated.
- **Secure API**: FastAPI-powered backend with CORS support and structured error handling.

## Technologies Used

- **Backend**: Python, FastAPI
- **Database**: MongoDB
- **NLP Libraries**: spaCy, SentenceTransformers
- **LLM Integration**: Ollama
- **Others**: PyPDF2, docx2txt, dotenv, pymongo

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8+** installed. [Download Python](https://www.python.org/downloads/)
- **MongoDB** instance set up. You can use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) for a cloud-based solution or install it locally.
- **Ollama** installed for LLM integration. [Install Ollama](https://ollama.com/docs/installation)
- **Git** installed. [Download Git](https://git-scm.com/downloads)
- **pip** package manager. Comes bundled with Python.
- **Virtual Environment Tool**: `venv` or `virtualenv` (optional but recommended).

## Installation

Follow these steps to set up the project locally.

### 1. Clone the Repository

Start by cloning the repository to your local machine.

```bash
git clone https://github.com/yourusername/resume-screener.git
cd resume-screener
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies and avoid conflicts.

```bash
python3 -m venv venv
```

Activate the virtual environment:

- **On macOS/Linux:**

  ```bash
  source venv/bin/activate
  ```

- **On Windows:**

  ```bash
  venv\Scripts\activate
  ```

### 3. Install Dependencies

Upgrade `pip` and install the required Python packages.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Pull the LLM Model with Ollama

Ollama is used for Language Learning Model integration. Pull the desired LLM model. Replace `<LLM_MODEL>` with the specific model you intend to use (e.g., `gpt-4`).

```bash
ollama pull <LLM_MODEL>
```

**Example:**

```bash
ollama pull gpt-4
```

> **Note:** Ensure Ollama is properly installed and configured on your system before running this command.

## Configuration

### 1. Environment Variables

Create a `.env` file in the root directory to store your environment variables. Use the provided `mongo.env` as a template.

```bash
cp mongo.env.example mongo.env
```

Open `mongo.env` and set your MongoDB connection string:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/resume_management?retryWrites=true&w=majority
```

> **Security Tip:** Never commit `.env` files or sensitive information to version control. Consider using tools like `gitignore` to exclude them.

### 2. Directory Structure

Ensure the following directories exist or will be created automatically:

- `employee_docs`: Directory where uploaded resumes will be stored.
- `jd_docs`: Directory for storing job description files.

These directories will be created automatically when running the application if they do not exist.

## Running the Application

Start the FastAPI server using Uvicorn.

```bash
uvicorn app:app --reload
```

- **`--reload`**: Enables auto-reloading of the server upon code changes. Remove this flag in production.

The server will start at `http://127.0.0.1:5001`.

