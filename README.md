# Fitness Dashboard

## Project Description
The Fitness Dashboard is a web application designed to help users track and manage their workout routines. It provides features such as logging exercises, tracking progress, and visualizing workout data.

[Google Document with project notes](https://docs.google.com/document/d/1lj6R9rybGuRNgUUzizTrjVLj5xpU9R1nWajcMkRqpwI/edit?usp=drive_link)

Link to download a user's own [MapMyRun workout history](https://www.mapmyfitness.com/workout/export/csv) (*requires sign-in*). 

## Features
- Exercise logging with customizable workout classification
- Progress tracking with charts and statistics
- Responsive design for mobile and desktop use

## Installation 
1. Clone the repository:
    ```bash
    git clone https://github.com/dagny/fitness-dashboard.git
    ```
2. Navigate to the project directory:
    ```bash
    cd fitness-dashboard
    ```
3. Install Poetry if you haven't already:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
- Make note of whether $HOME was successfully modified; if not, poetry may be installed in another location. For example, for my mac poetry is here:
    ```bash
    ~/.local/bin/poetry
    ```
**Instalation - A)** typical route of setting up virtual environment w project dependeincies  
4a. Create and activate a virtual environment for the project. For example, I typically use venv and am using the name ".st-db":
```bash
    python3 -m venv .st-db    
    source .st-db/bin/activate
```
5a. Within the virtual environment, install dependencies using Poetry (set to package-mode ):
```bash
    poetry install                  #If dev
```
    or
```bash
    poetry install --no-dev         #If prod
```
**Instalation - B)** use direnv to auto-load the python env and env vars when you cd int othe folder
4b. Install `direnv` installed at the shell-level, if you haven't already
```bash
brew install direnv

```
Add the hook to your shell config (`~/.zshrc`):
```bash
eval "$(direnv hook zsh)"
```
Direnv needs to be installed once system-wide and will work everywhere.

5b. Navigate to project folder and run:
```bash
poetry init
poetry config virtualenvs.in-project true
poetry install
```

6b. Add this `.envrc`:

```bash
VENV_PATH=$(poetry env info -p)
source "$VENV_PATH/bin/activate"
export STREAMLIT_THEME="dark"
dotenv
```

7b. Then:

```bash
touch .env
echo ".env" >> .gitignore
direnv allow
```

🎉 Now: Environment is **fully auto-activated, clean, and predictable.** 

**If local, run this script to setup a local db for testing**  
6. Run "init.py" from main project directory to CREATE DATABASE & TABLES
    ```bash
    poetry run python init.py
    ```
    - Loads "pyproject.toml" and looks for .streamlit folder; if none found, creates it and the .streamlit/secrets.toml file with db credentials...
    - Loads MYSQL_USER and MYSQL_PWD env vars, and sets them to "db_user" and "db_password" in "secrets.toml" file if none found
    - BE SURE TO EDIT THESE VALUES OTHERWISE DB CONNECTION WILL FAIL
    - Checks for an existing database, `sweat`, and creates it if now
    - Create table, `workout_summary` if doensn't exist. tbl_schema is hard-coded but could easily be read in.
    - Displays the number of rows in the table & Exit

**Run Dashboard and visit at `http://localhost:8501`** 
8. Run "dashboard.py" from main project directory to SHOW DASHBOARD:
    ```bash
    poetry run python dash.py
    ```

## Deployment Instructions 
Coming soon April 2025!

## Usage
1. 
2. Create an account or log in if you already have one.
3. Start logging your workouts and track your progress!

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any questions or feedback, please contact [barbs@balex.com](mailto:barbs@balex.com).

