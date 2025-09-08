import os

# Common module names you want to avoid shadowing
common_modules = {
    "builtins": [
        "math", "sys", "os", "json", "re", "datetime", "time",
        "logging", "email", "socket", "random", "subprocess", "pathlib",
        "typing", "threading", "http", "argparse", "csv", "shutil", "itertools"
    ],
    "third_party": [
        "pandas", "numpy", "requests", "flask", "django", "sklearn",
        "matplotlib", "seaborn", "scipy", "sqlalchemy", "pytest", "openai"
    ]
}

shadow_targets = set(common_modules["builtins"] + common_modules["third_party"])
shadowed_files = []

# 🔍 Walk through project files, but skip .venv and site-packages
for root, _, files in os.walk("."):
    # Skip known virtual environment and dependency folders
    if any(part in root for part in [".venv", "venv", "site-packages", "__pycache__"]):
        continue

    for file in files:
        if file.endswith(".py"):
            filename_no_ext = os.path.splitext(file)[0]
            if filename_no_ext in shadow_targets:
                shadowed_files.append(os.path.join(root, file))

# 📢 Output results
if shadowed_files:
    print("⚠️  Potential shadowing detected:")
    for path in shadowed_files:
        print(f" - {path}")
else:
    print("✅ No conflicting module names detected.")

