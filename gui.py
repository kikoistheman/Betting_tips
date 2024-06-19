import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from transcript import extract_video_id
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from ai_summery import summarize_betting_tips
import csv
import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from groq_api import api_key
import torch
from transformers import pipeline
import arabic_reshaper
from bidi.algorithm import get_display
from deep_translator import GoogleTranslator
import re
from datetime import datetime

class BettingTipGUI:
    def __init__(self, master):
        self.master = master
        master.title("Betting Tips")

        # Initialize WebDriver options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')

        # Initialize Test class
        self.test_instance = Test(self.options)

        # Initialize GUI elements
        self.label = tk.Label(master, text="Choose a team:", width=40)
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.team_listbox = tk.Listbox(master, selectmode=tk.SINGLE, width=40)
        self.team_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL, command=self.team_listbox.yview)
        self.team_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=1, pady=5, sticky='nsw')

        self.language_label = tk.Label(master, text="Choose language:", width=40)
        self.language_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.language_combobox = ttk.Combobox(master, values=["English", "Arabic"])
        self.language_combobox.current(0)
        self.language_combobox.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.choose_button = tk.Button(master, text="Choose Team", command=self.choose_team)
        self.choose_button.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.save_csv_button = tk.Button(master, text="Save to CSV", command=self.save_to_csv)
        self.save_csv_button.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.output_text = scrolledtext.ScrolledText(master, width=40, height=20)
        self.output_text.grid(row=6, column=0, padx=10, pady=5, sticky="w")

        self.load_youtube_data_button = tk.Button(master, text="Load YouTube Data", command=self.load_youtube_data)
        self.load_youtube_data_button.grid(row=7, column=0, padx=10, pady=5, sticky="w")

        self.video_listbox = tk.Listbox(master, selectmode=tk.SINGLE, width=40)
        self.video_listbox.grid(row=8, column=0, padx=10, pady=5, sticky="w")

        self.summarize_button = tk.Button(master, text="Summarize YouTube Video", command=self.summarize_youtube_video)
        self.summarize_button.grid(row=9, column=0, padx=10, pady=5, sticky="w")

        # Text area to display summary
        self.youtube_summary_text = scrolledtext.ScrolledText(master, width=40, height=40)
        self.youtube_summary_text.grid(row=0, column=2, rowspan=10, padx=10, pady=5, sticky="nsew")

        master.grid_columnconfigure(2, weight=1)
        master.grid_rowconfigure(6, weight=1)

        # Populate teams
        self.populate_teams()

    def populate_teams(self):
        filename = 'links.txt'
        teams = self.test_instance.fetch_team_names(filename)
        for team_name in teams:
            self.team_listbox.insert(tk.END, team_name)

    def choose_team(self):
        selected_index = self.team_listbox.curselection()
        if selected_index:
            chosen_team = self.team_listbox.get(selected_index)
            link = self.test_instance.get_link_for_team(chosen_team)
            self.show_output(link)
        else:
            messagebox.showinfo("Info", "Please select a team.")

    def show_output(self, link):
        content = self.test_instance.read_predictextp_content(link)
        if content:
            output = self.test_instance.invoke_chat_model(content)
            selected_language = self.language_combobox.get()
            if selected_language == "Arabic":
                output = self.translate_to_arabic(output)
                output = self.reshape_arabic_text(output)
            self.output_text.delete(1.0, tk.END)  # Clear previous content
            self.output_text.insert(tk.END, output)
        else:
            messagebox.showinfo("Info", "Failed to fetch content.")

    def save_to_csv(self):
        # Load the context from context.txt
        with open('context.txt', 'r') as f:
            context = f.read().strip()  # Ensure to strip any leading/trailing whitespace
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model_name = "deepset/roberta-base-squad2"
        # List of questions
        questions = [
            'who is the winner team?',
            "will both teams have a draw?",
            'over 2.5 goals?',
            'will both teams score?',
            "who is vs who?",
            "what is the time of the match?"
        ]

        # Initialize a list to store results
        results = []

        # Get predictions
        nlp = pipeline('question-answering', model=model_name, tokenizer=model_name, device=0 if torch.cuda.is_available() else -1)

        for question in questions:
            QA_input = {
                'question': question,
                'context': context
            }
            res = nlp(QA_input)
            
            # Collect results
            results.append(res['answer'])

        # Append results to CSV file
        csv_filename = 'matches.csv'
        with open(csv_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            if csvfile.tell() == 0:
                # Write header row if file is empty
                csv_writer.writerow(['Question'] + questions)
            
            # Write answers row
            csv_writer.writerow(['Answer'] + results)

        messagebox.showinfo("Info", f"Results saved to {csv_filename}")

    def translate_to_arabic(self, text):
        translator = GoogleTranslator(source='en', target='ar')
        translation = translator.translate(text)
        return translation
    def get_today_date(self):
        current_date = datetime.now()
        formatted_date = current_date.strftime("%m/%d")
        return formatted_date


         
    def reshape_arabic_text(self, text):
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text

    def load_youtube_data(self):
        self.test_instance.get_video_data(f"betting tips today football{self.get_today_date()} 2024")
        self.video_listbox.delete(0, tk.END)  # Clear previous listbox entries
        for title, _ in self.test_instance.video_data:
            self.video_listbox.insert(tk.END, title)

    def summarize_youtube_video(self):
        selected_index = self.video_listbox.curselection()
        if selected_index:
            video_title, video_link = self.test_instance.video_data[selected_index[0]]
            self.test_instance.perform_action(video_title, video_link)
            with open("transcript.txt", "r") as file:
                transcript_text = file.read()
            summary = summarize_betting_tips()
            self.youtube_summary_text.delete(1.0, tk.END)  # Clear previous text
            self.youtube_summary_text.insert(tk.END, summary)
        else:
            messagebox.showinfo("Info", "Please select a video.")

class Test:
    def __init__(self, options):
        self.options = options
        self.video_data = []
        self.fetch_and_save_links()

    def fetch_and_save_links(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get("https://www.bettingtips.today/")

        # Extract all links from the webpage
        links = self.driver.find_elements(By.TAG_NAME, "a")

        # Define the regex pattern to match "ID" followed by numbers
        pattern = re.compile(r'ID\d+')

        # List to store matched href links
        matched_links = []

        # Collect the href attributes of the links that match the pattern
        for link in links:
            href = link.get_attribute("href")
            if href and pattern.search(href):  # Ensure the link has an href attribute and matches the pattern
                matched_links.append(href)

        # Close the driver
        self.driver.quit()

        # Write matched links to a text file
        with open("links.txt", "w") as file:
            for link in matched_links:
                file.write(link + "\n")

        print("Links written to links.txt")

    def get_video_data(self, search_query):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(f"https://www.youtube.com/results?search_query={search_query}")
        sleep(1)
        
        # Find all video titles with href attribute containing "/watch?v="
        video_elements = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[@id='video-title' and contains(@href, '/watch?v=')]")))
        
        # Extract and store the title and href attribute of each video element
        for idx, video in enumerate(video_elements, start=1):
            video_title = video.text.strip()
            video_link = video.get_attribute("href")
            self.video_data.append((video_title, video_link))
        
        self.driver.quit()

    def fetch_team_names(self, filename):
        # Regular expression pattern to extract team names
        pattern = re.compile(r'/ID\d+-(\w+(?:-\w+)*)-prediction')

        # Read links from the file and extract team names
        with open(filename, "r") as file:
            links = file.readlines()

        teams = []
        for link in links:
            match = pattern.search(link)
            if match:
                team_name = match.group(1).replace("-", " ")  # Replace hyphens with spaces
                teams.append(team_name)
        return teams

    def get_link_for_team(self, team_name):
        # Read links from the file and find link for given team name
        with open("links.txt", "r") as file:
            links = file.readlines()

        pattern = re.compile(r'/ID\d+-(\w+(?:-\w+)*)-prediction')
        for link in links:
            match = pattern.search(link)
            if match:
                current_team_name = match.group(1).replace("-", " ")
                if current_team_name == team_name:
                    return link.strip()
        return None

    def read_predictextp_content(self, link):
        try:
            response = requests.get(link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                predictextp_elements = soup.find_all('p', class_='predictextp')
                if predictextp_elements:
                    return " ".join([element.get_text(strip=True) for element in predictextp_elements])
                else:
                    print(f"No <p class=\"predictextp\"> tags found in {link}")
            else:
                print(f"Failed to retrieve content. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching content: {e}")
        return None

    def invoke_chat_model(self, text):
        system = "1: winner team : team name or draw 2: over 2.5 or under 2.5 3: both teams to score or not 4:team name vs team name 5 : the time of the match then stop the sentence like realy dont over talk just respond with the template"
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

        chain = prompt | ChatGroq(temperature=0, groq_api_key=api_key, model_name="mixtral-8x7b-32768")
        text = chain.invoke({"text": text})
        
        output = text.content
        
        # Save the output to context.txt
        with open("context.txt", "w") as file:
            file.write(output + "\n")
        
        # Return only the first 100 characters
        return text.content

    def perform_action(self, video_title, video_link):
        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=self.options)
        
        # Extract video ID from YouTube link
        video_id = extract_video_id(video_link)

        try:
            if video_id:  
                # Get transcript from YouTube
                dd = YouTubeTranscriptApi.get_transcript(video_id)
                # Extracting text from the transcript
                text_only = [item['text'] for item in dd]
                
                # Save the transcript to a text file
                with open("transcript.txt", "w") as file:
                    for line in text_only:
                        file.write(line + "\n")
            else:
                print("Could not extract video ID.")
        except TranscriptsDisabled as e:
            print(f"TranscriptsDisabled: Could not retrieve a transcript for the video {video_link} - {e}")
            print("Please choose another video.")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please choose another video.")
        
        # Quit WebDriver
        self.driver.quit()

# Create the main application window
if __name__ == "__main__":
    root = tk.Tk()
    app = BettingTipGUI(root)
    root.mainloop()
