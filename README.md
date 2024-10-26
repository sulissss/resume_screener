# Resume Screener Project

![Project Logo](https://via.placeholder.com/150)

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

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/resume-screener.git
   cd resume-screener

2. Set the LLM model in the .env file
3. Run your local LLM
```bash
   ollama run <LLM_MODEL>
  
