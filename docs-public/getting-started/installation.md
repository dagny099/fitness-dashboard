# Installation

This guide will walk you through setting up the Fitness Dashboard on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+**: Download from [python.org](https://python.org)
- **Git**: For cloning the repository
- **MySQL**: Local database server (for development)

## Installation Methods

Choose the installation method that best suits your workflow:

=== "Poetry (Recommended)"
    
    Poetry provides dependency management and virtual environment handling.

    ### Step 1: Install Poetry
    
    If you don't have Poetry installed:
    
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
    
    !!! note
        Poetry may be installed in `~/.local/bin/poetry` on some systems.
    
    ### Step 2: Clone and Setup
    
    ```bash
    git clone https://github.com/dagny099/fitness-dashboard.git
    cd fitness-dashboard
    
    # Install dependencies
    poetry install
    
    # Activate the virtual environment
    poetry shell
    ```

=== "Virtual Environment"
    
    Traditional Python virtual environment setup.

    ### Step 1: Clone Repository
    
    ```bash
    git clone https://github.com/dagny099/fitness-dashboard.git
    cd fitness-dashboard
    ```
    
    ### Step 2: Create Virtual Environment
    
    ```bash
    python3 -m venv .st-db
    source .st-db/bin/activate  # On Windows: .st-db\Scripts\activate
    ```
    
    ### Step 3: Install Dependencies
    
    ```bash
    pip install -r requirements.txt
    ```

=== "direnv (Advanced)"
    
    Automatic environment activation when entering the project directory.

    ### Step 1: Install direnv
    
    ```bash
    brew install direnv  # macOS
    # or
    sudo apt install direnv  # Ubuntu
    ```
    
    ### Step 2: Setup Shell Integration
    
    Add to your `~/.zshrc` or `~/.bashrc`:
    
    ```bash
    eval "$(direnv hook zsh)"  # for zsh
    eval "$(direnv hook bash)" # for bash
    ```
    
    ### Step 3: Project Setup
    
    ```bash
    git clone https://github.com/dagny099/fitness-dashboard.git
    cd fitness-dashboard
    
    poetry config virtualenvs.in-project true
    poetry install
    ```
    
    ### Step 4: Create .envrc
    
    ```bash
    cat > .envrc << EOF
    VENV_PATH=$(poetry env info -p)
    source "$VENV_PATH/bin/activate"
    export STREAMLIT_THEME="dark"
    dotenv
    EOF
    
    touch .env
    echo ".env" >> .gitignore
    direnv allow
    ```

## Environment Configuration

Create your environment configuration file:

```bash
cp .env.example .env  # If available
# or create manually
touch .env
```

Add the following environment variables to your `.env` file:

```bash
# Database Configuration
MYSQL_USER=your_username
MYSQL_PWD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Application Settings
STREAMLIT_THEME=dark
DEBUG=true
```

## Verify Installation

Test your installation by running:

```bash
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
python -c "import pymysql; print('PyMySQL installed successfully')"
```

## Next Steps

Once installation is complete:

1. **Database Setup**: Configure your MySQL database following the [Database Setup](database-setup.md) guide
2. **Quick Start**: Launch the application with our [Quick Start](quick-start.md) guide
3. **Configuration**: Customize your setup in the [Configuration Guide](../developer/configuration.md)

## Troubleshooting

### Common Issues

!!! warning "Poetry Not Found"
    If `poetry` command is not found, try:
    ```bash
    ~/.local/bin/poetry --version
    ```
    Add `~/.local/bin` to your PATH or create an alias.

!!! warning "MySQL Connection Error"
    Ensure MySQL is running and credentials are correct:
    ```bash
    mysql -u your_username -p
    ```

!!! warning "Python Version Compatibility"
    The application requires Python 3.10+. Check your version:
    ```bash
    python --version
    ```

For more troubleshooting help, see the [Troubleshooting Reference](../reference/troubleshooting.md).