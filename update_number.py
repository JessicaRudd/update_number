#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import GenerationConfig


def read_number():
    with open("number.txt", "r", encoding="utf-8") as f:
        return int(f.read().strip())


def write_number(num):
    with open("number.txt", "w", encoding="utf-8") as f:
        f.write(str(num))


def generate_random_commit_message(gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-pro")

    prompt = """
        Generate a Git commit message following the Conventional Commits standard. The message should include a type, an optional scope, and a subject. Please keep it short. Here are some examples:

        - feat(auth): add user authentication module
        - fix(api): resolve null pointer exception in user endpoint
        - docs(readme): update installation instructions
        - chore(deps): upgrade lodash to version 4.17.21
        - refactor(utils): simplify date formatting logic

        Now, generate a new commit message:
    """
    generation_config = GenerationConfig(
        temperature=0.9,
        top_p=0.9,
        top_k=50,
        max_output_tokens=50,
    )
    response = model.generate_content(prompt, generation_config=generation_config)
    text = response.text

    if "- " in text:
        return text.rsplit("- ", 1)[-1].strip()
    else:
        return text.strip()


def git_commit(github_pat):
    # Stage the changes
    subprocess.run(["git", "add", "number.txt"])
    # Create commit with current date
    if "FANCY_JOB_USE_LLM" in os.environ:
        commit_message = generate_random_commit_message(os.environ.get("GEMINI_API_KEY"))
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"Update number: {date}"
    subprocess.run(["git", "config", "--global", "user.name", "Automated Commit Bot"])
    subprocess.run(["git", "config", "--global", "user.email", "bot@example.com"])
    subprocess.run(["git", "commit", "-m", commit_message])

    # Ensure git actions are done using the specified github pat
    github_repo = os.environ.get("GITHUB_REPOSITORY")
    github_username = os.environ.get("GITHUB_USERNAME")
    remote_url = f"https://{github_username}:{github_pat}@github.com/{github_repo}.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url])

def git_push(github_pat):
    # Push the committed changes to GitHub
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)


def main(request):
    try:
        print("Function start")
        # initialize git if this is the first run
        if not os.path.exists(".git"):
            print("Initializing git")
            subprocess.run(["git", "init"])
      
            # Create a basic .gitignore file
            with open(".gitignore", "w") as f:
                f.write("venv/\n")
                f.write("__pycache__/\n")

        current_number = read_number()
        new_number = current_number + 1
        write_number(new_number)
        github_pat = os.environ.get("GITHUB_PAT")
        git_commit(github_pat)
        git_push(github_pat)

        return 'Success'
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    # This part is for local testing, not for deployment to Cloud Functions
    # Set up a test number.txt file
    if not os.path.exists("number.txt"):
        with open("number.txt", "w") as f:
            f.write("0")

    main(None)