# Pre-Commit Code Quality Review

This repository includes a pre-commit hook that uses OpenAI's GPT-4 model to analyze your code for quality, security, and performance. The system is designed to provide actionable feedback and ensure your code adheres to best practices before committing it to the repository.

## Features

- **Code Quality Review**: Analyzes code structure, naming conventions, and cleanliness.
- **Security Best Practices**: Identifies vulnerabilities, such as missing input validation or sensitive data handling.
- **Performance Optimization**: Evaluates algorithm efficiency and memory usage.
- **Type Safety**: Ensures proper use of type hints and validations.
- **Error Handling**: Reviews try/catch blocks, logging, and error messages.
- **File Support**: Automatically scans `.py`, `.ts`, and `.mjs` files.

---

## How It Works

1. **Staged and New Files**: The hook only analyzes staged or new files with specific extensions.
2. **Automated Analysis**: Feedback is generated based on clean code principles, security, performance, and error handling.
3. **Scoring System**: Each file receives a quality score (0-100), with a minimum threshold of 70 to pass the review.
4. **Detailed Feedback**: For each issue, the system provides:
   - Severity (High/Medium/Low)
   - Clear description of the issue
   - Specific line numbers
   - Suggestions for improvement
   - Categorization of issues (e.g., Security, Performance)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Run the setup script**:
   ```bash
   python setup_repository.py
   ```

3. **Provide your OpenAI API Key**:
   During setup, you'll be prompted to enter your OpenAI API key, which will be saved in a `.env` file.

4. **Install dependencies**:
   The setup script will create necessary files and install required dependencies.

5. **Pre-Commit Hook Installation**:
   The script will install the pre-commit hook, enabling automatic code analysis during commits.

---

## Usage

1. **Modify or create files**:
   - Only `.py`, `.ts`, or `.mjs` files are analyzed.

2. **Stage the files**:
   ```bash
   git add <file>
   ```

3. **Commit your changes**:
   ```bash
   git commit -m "Your commit message"
   ```
   The pre-commit hook will automatically analyze the staged files. If issues are found, the commit will fail, and detailed feedback will be displayed.

---

## Configuration Files

- **`pre_commit_code_check.py`**: Main script for pre-commit analysis.
- **`.pre-commit-config.yaml`**: Configuration file for the pre-commit framework.
- **`requirements.txt`**: Dependencies required for the analysis.
- **`.gitignore`**: Pre-configured file to ignore unnecessary files (e.g., `.env`).

---

## Troubleshooting

- **No files to analyze**:
  Ensure that files are staged or newly created. Use `git add` to stage files.

- **API key issues**:
  If the OpenAI API key is not set, add it manually to the `.env` file:
  ```bash
  echo "OPENAI_API_KEY=your_api_key" > .env
  ```

- **Pre-commit not triggering**:
  Reinstall the hook using:
  ```bash
  pre-commit install
  ```



