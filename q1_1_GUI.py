import requests
from bs4 import BeautifulSoup
import pandas as pd

import tkinter as tk
from tkinter import filedialog, messagebox

from q1_2_chatbot import ask_about_repos

repo_names = []

def clean_username(user_input):
    
    # Allow users to enter either a username or a URL

    user_input = user_input.strip()

    if user_input.startswith("https://github.com/"):
        user_input = user_input.replace("https://github.com/", "")

    user_input = user_input.strip("/")

    return user_input


def scrape_github_repos(username):

    repo_names_local = []
    repo_urls = []

    page = 1
    # AI assistance note: using AI for research to understand how GitHub repository pages are structured
    while True:
        url = f"https://github.com/{username}?tab=repositories&page={page}"

        response = requests.get(url)

        if response.status_code == 404:
            raise Exception("GitHub user not found. Please check the username.")

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        repo_links = soup.select("h3 a")

        current_page_repos = []

        for link in repo_links:
            href = link.get("href")

            if href is None:
                continue

            parts = href.strip("/").split("/")

            if len(parts) != 2:
                continue

            owner, repo_name = parts

            if owner.lower() != username.lower():
                continue

            if repo_name not in repo_names_local:
                repo_names_local.append(repo_name)
                repo_urls.append("https://github.com" + href)
                current_page_repos.append(repo_name)

        if len(current_page_repos) == 0:
            break

        page = page + 1

    if len(repo_names_local) == 0:
        raise Exception("No public repositories found for this user.")

    df = pd.DataFrame({
        "repository_name": repo_names_local,
        "repository_url": repo_urls
    })

    return df


def choose_save_path():

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save Excel file as"
    )

    if file_path:
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, file_path)


def run_program():

    global repo_names

    user_input = username_entry.get()
    output_path = output_path_entry.get()

    username = clean_username(user_input)

    if username == "":
        messagebox.showerror("Error", "Please enter a GitHub username or profile URL.")
        return

    if output_path == "":
        messagebox.showerror("Error", "Please choose where to save the Excel file.")
        return

    try:
        result_df = scrape_github_repos(username)
        result_df.to_excel(output_path, index=False)

        repo_names = result_df["repository_name"].dropna().tolist()

        repo_list_box.delete(0, tk.END)
        for name in repo_names:
            repo_list_box.insert(tk.END, name)

        messagebox.showinfo(
            "Success",
            f"Successfully saved {len(result_df)} repositories to Excel."
        )

    except Exception as error:
        messagebox.showerror("Error", str(error))


def ask_ai():

    question = question_entry.get().strip()

    if question == "":
        messagebox.showwarning("Missing question", "Please enter a question first.")
        return

    chat_history.insert(tk.END, f"You: {question}\n")
    chat_history.insert(tk.END, "AI: Thinking...\n")
    chat_history.update()

    answer = ask_about_repos(question, repo_names)

    chat_history.insert(tk.END, f"AI: {answer}\n\n")
    question_entry.delete(0, tk.END)

# ============================================================
#  GUI part 

root = tk.Tk()
root.title("GitHub Repository Scraper with AI Chatbot")
root.geometry("720x650")


title_label = tk.Label(
    root,
    text="GitHub Public Repository Scraper",
    font=("Arial", 14, "bold")
)
title_label.pack(pady=10)


input_frame = tk.Frame(root)
input_frame.pack(pady=10)


username_label = tk.Label(input_frame, text="GitHub Username / URL:")
username_label.grid(row=0, column=0, padx=5, pady=8, sticky="e")

username_entry = tk.Entry(input_frame, width=45)
username_entry.grid(row=0, column=1, padx=5, pady=8)


output_path_label = tk.Label(input_frame, text="Save Excel As:")
output_path_label.grid(row=1, column=0, padx=5, pady=8, sticky="e")

output_path_entry = tk.Entry(input_frame, width=45)
output_path_entry.grid(row=1, column=1, padx=5, pady=8)


browse_button = tk.Button(input_frame, text="Browse", command=choose_save_path)
browse_button.grid(row=1, column=2, padx=5, pady=8)


run_button = tk.Button(
    root,
    text="Scrape and Save to Excel",
    command=run_program,
    width=25
)
run_button.pack(pady=10)

# ============================================================
#  Repository list section 

repo_frame = tk.LabelFrame(root, text="Scraped Repository Names")
repo_frame.pack(fill="both", expand=True, padx=10, pady=10)

repo_list_box = tk.Listbox(repo_frame, height=8)
repo_list_box.pack(fill="both", expand=True, padx=5, pady=5)

# ============================================================
#  AI Chatbot section 
chat_frame = tk.LabelFrame(root, text="AI Chatbot - Ask about GitHub repo names")
chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

chat_history = tk.Text(chat_frame, height=10, wrap="word")
chat_history.pack(fill="both", expand=True, padx=5, pady=5)

question_entry = tk.Entry(chat_frame, width=80)
question_entry.pack(fill="x", padx=5, pady=5)

ask_button = tk.Button(
    chat_frame,
    text="Ask AI",
    command=ask_ai,
    width=20
)
ask_button.pack(pady=5)


root.mainloop()