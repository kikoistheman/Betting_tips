# Betting Tips GUI Application

## Overview

The Betting Tips GUI Application is a Python-based desktop application that provides daily updated betting tips from a betting tips website and allows users to generate CSV files based on these tips. Additionally, it can fetch and summarize betting tips from YouTube videos. The application utilizes several Python libraries such as `tkinter` for the GUI, `selenium` for web scraping, and `youtube_transcript_api` for YouTube video transcripts.

## Features

- **Daily Betting Tips**: Fetches and displays daily betting tips from a betting tips website.
- **CSV Generation**: Allows users to save the betting tips to a CSV file.
- **YouTube Betting Tips**: Fetches and summarizes betting tips from YouTube videos.
- **support arabic/english**

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/kikoistheman/Betting_tips.git
    cd betting-tips-gui
    ```

2. **Install Dependencies**:
    Make sure you have Python installed. Then, install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

3. **Setup WebDriver**:
    Download the appropriate WebDriver for your browser (e.g., ChromeDriver for Google Chrome) and ensure it's in your PATH.

4. **put your groq api code into groq_api.py file**

## Usage

Run the application by executing the `gui.py` file:
```bash
python gui.py
