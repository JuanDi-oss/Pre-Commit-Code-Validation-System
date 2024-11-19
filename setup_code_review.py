import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional

load_dotenv()

class IssueCode(BaseModel):
    file_path: str
    line_number: Optional[int]
    severity: str
    message: str
    suggestion: str
    category: str

class AnalysisResult(BaseModel):
    issues: List[IssueCode]
    passed: bool
    summary: str
    code_quality_score: int

CODE_CHECK_CONTENT = '''
import os
import sys
from typing import List, Optional
import instructor
from openai import OpenAI
from pydantic import BaseModel
import subprocess
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class IssueCode(BaseModel):
    file_path: str
    line_number: Optional[int]
    severity: str
    message: str
    suggestion: str
    category: str

class AnalysisResult(BaseModel):
    issues: List[IssueCode]
    passed: bool
    summary: str
    code_quality_score: int

def get_files_to_analyze():
    """Get only new and staged files that actually exist"""
    files_to_check = set()  # Using set to avoid duplicates
    repo_path = os.getcwd()
    
    try:
        # Get staged files
        staged = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True
        )
        staged_files = staged.stdout.splitlines()
        
        # Get untracked (new) files
        untracked = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            capture_output=True,
            text=True
        )
        untracked_files = untracked.stdout.splitlines()
        
        # Combine and filter files
        all_files = set(staged_files + untracked_files)
        
        # Filter by extension and existence
        valid_files = []
        for file in all_files:
            full_path = os.path.join(repo_path, file)
            if (file.endswith(('.py', '.ts', '.mjs')) and 
                os.path.exists(full_path) and 
                os.path.isfile(full_path)):
                valid_files.append(file)
        
        if not valid_files:
            print("\n💡 No se encontraron archivos nuevos o staged para analizar")
            print("   Para analizar archivos:")
            print("   1. Crea nuevos archivos .py, .ts o .mjs")
            print("   2. O modifica archivos existentes y haz 'git add'")
            
        return valid_files
        
    except Exception as e:
        print(f"\n❌ Error obteniendo archivos: {e}")
        return []

def analyze_file(client, file_path: str) -> AnalysisResult:
    """Analyzes an individual file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    messages = [
        {"role": "system", "content": """Please analyze this code in detail and provide specific feedback for:
1. Clean code principles:
- Variable and function names
- Structure and organization
- Comments and documentation
- Code duplication

2. Security best practices:
- Input validation
- Sensitive data handling
- Common vulnerabilities

3. Performance considerations:
- Algorithm optimization
- Memory usage
- Time complexity

4. Type safety:
- Correct type usage
- Type hints
- Type validation

5. Error handling:
- Appropriate try/catch
- Descriptive error messages
- Logging

For each issue found, provide:
- Severity (high/medium/low)
- Clear problem message
- Specific suggestion for improvement
- Problem category
- Specific line of code when possible

Assign a code quality score from 0 to 100."""},
        {"role": "user", "content": f"Archivo {file_path}:\\n{content}"}
    ]

    return client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_model=AnalysisResult
    )

def main():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️ Error: OPENAI_API_KEY no está configurada en el archivo .env")
        sys.exit(1)

    client = instructor.from_openai(OpenAI())
    files_to_check = get_files_to_analyze()

    if not files_to_check:
        print("No files found to analyze")
        sys.exit(0)

    total_issues = []
    all_scores = []
    failed = False

    print("\\n🔍 Starting code analysis...")
    print("=" * 80)

    for file_path in files_to_check:
        print(f"\\n📝 Analyzing {file_path}...")
        try:
            result = analyze_file(client, file_path)
            all_scores.append(result.code_quality_score)
            
            print(f"\\n📊 Quality Score: {result.code_quality_score}/100")
            
            if not result.passed or result.code_quality_score < 70:
                failed = True
                total_issues.extend(result.issues)
                print(f"\\n⚠️ Problems encountered in {file_path}:")
                print(f"Summary: {result.summary}")
                
                issues_by_category = {}
                for issue in result.issues:
                    if issue.category not in issues_by_category:
                        issues_by_category[issue.category] = []
                    issues_by_category[issue.category].append(issue)
                
                for category, issues in issues_by_category.items():
                    print(f"\\n📌 {category.upper()}:")
                    for issue in issues:
                        print(f"\\n  Severity: {issue.severity}")
                        print(f"  Problem: {issue.message}")
                        print(f"  Advice: {issue.suggestion}")
                        if issue.line_number:
                            print(f"  Line: {issue.line_number}")
                        print("  " + "-" * 40)

        except Exception as e:
            print(f"❌ Error parsing {file_path}: {str(e)}")
            sys.exit(1)

    print("\\n" + "=" * 80)
    if len(all_scores) > 0:
        avg_score = sum(all_scores) / len(all_scores)
        print(f"\\n📊 Average project score: {avg_score:.2f}/100")

    if failed:
        print("\\n❌ Review failed. Please fix the issues before committing.")
        sys.exit(1)
    else:
        print("\\n✅ All files passed review!")
        sys.exit(0)

if __name__ == "__main__":
    main()
'''

def get_files_to_analyze():
    """Get only new and staged files that actually exist"""
    files_to_check = set()  # Using set to avoid duplicates
    repo_path = os.getcwd()
    
    try:
        # Get staged files
        staged = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True
        )
        staged_files = staged.stdout.splitlines()
        
        # Get untracked (new) files
        untracked = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            capture_output=True,
            text=True
        )
        untracked_files = untracked.stdout.splitlines()
        
        # Combine and filter files
        all_files = set(staged_files + untracked_files)
        
        # Filter by extension and existence
        valid_files = []
        for file in all_files:
            full_path = os.path.join(repo_path, file)
            if (file.endswith(('.py', '.ts', '.mjs')) and 
                os.path.exists(full_path) and 
                os.path.isfile(full_path)):
                valid_files.append(file)
        
        if not valid_files:
            print("\n💡 No new or staged files found to analyze")
            print(" To analyze files:")
            print(" 1. Create new .py, .ts or .mjs files")
            print(" 2. Or modify existing files and do 'git add'")
            
        return valid_files
        
    except Exception as e:
        print(f"\n❌ Error obteniendo archivos: {e}")
        return []

def analyze_file(client, file_path: str) -> AnalysisResult:
    """Analiza un archivo individual"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    messages = [
        {"role": "system", "content": """Analyze this code closely for:
        1. Clean code principles
        2. Security best practices
        3. Performance considerations
        4. Type safety
        5. Error handling"""},
        {"role": "user", "content": f"Archivo {file_path}:\n{content}"}
    ]

    return client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_model=AnalysisResult
    )

def analyze_setup_files(repo_path: str, client) -> bool:
    """Scan configuration files before installing them"""
    setup_files = [
        ('pre_commit_code_check.py', CODE_CHECK_CONTENT),
        ('setup_code_review.py', Path(__file__).read_text())
    ]
    
    print("\n🔍 Parsing configuration files...")
    print("=" * 80)
    
    all_passed = True
    for filename, content in setup_files:
        print(f"\n📝 Analyzing {filename}...")
        
        # Crear archivo temporal para análisis
        temp_path = os.path.join(repo_path, filename)
        with open(temp_path, 'w') as f:
            f.write(content)
            
        try:
            result = analyze_file(client, temp_path)
            print(f"\n📊 Quality Score: {result.code_quality_score}/100")
            
            if not result.passed or result.code_quality_score < 70:
                all_passed = False
                print(f"\n⚠️ Problems encountered in {filename}:")
                print(f"Sumamry: {result.summary}")
                
                issues_by_category = {}
                for issue in result.issues:
                    if issue.category not in issues_by_category:
                        issues_by_category[issue.category] = []
                    issues_by_category[issue.category].append(issue)
                
                for category, issues in issues_by_category.items():
                    print(f"\n📌 {category.upper()}:")
                    for issue in issues:
                        print(f"\n  Severity: {issue.severity}")
                        print(f"  Problem: {issue.message}")
                        print(f"  Advice: {issue.suggestion}")
                        if issue.line_number:
                            print(f"  Line: {issue.line_number}")
                        print("  " + "-" * 40)
            
        except Exception as e:
            print(f"❌ Error parsing {filename}: {str(e)}")
            all_passed = False
            
        os.remove(temp_path)  # Limpiar archivo temporal
    
    return all_passed

def create_files(repo_path):
    with open(os.path.join(repo_path, 'pre_commit_code_check.py'), 'w') as f:
        f.write(CODE_CHECK_CONTENT.strip())
    
    precommit_config_content = '''
repos:
-   repo: local
    hooks:
    -   id: code-review
        name: Code Review AI
        entry: python pre_commit_code_check.py
        language: python
        types: [python, typescript, javascript, sql, css, html]
        additional_dependencies: []
        files: \.(py|ts|js|sql|css|html|ipynb)$
        pass_filenames: false

'''
    with open(os.path.join(repo_path, '.pre-commit-config.yaml'), 'w') as f:
        f.write(precommit_config_content.strip())
    
    requirements_content = '''
instructor>=1.6.4
openai>=1.12.0
pydantic>=2.0.0
pre-commit
python-dotenv
'''
    with open(os.path.join(repo_path, 'requirements.txt'), 'w') as f:
        f.write(requirements_content.strip())
    
    # Crear .gitignore
    gitignore_content = '''
.env
__pycache__/
*.pyc
.venv/
'''
    with open(os.path.join(repo_path, '.gitignore'), 'w') as f:
        f.write(gitignore_content.strip())

def analyze_repository(repo_path: str):
    client = instructor.from_openai(OpenAI())
    files_to_check = get_files_to_analyze()

    if not files_to_check:
        print("\n⚠️ No files found to scan")
        print("💡 Scan includes:")
        print(" 1. New files (untracked)")
        print(" 2. Modified files (unstaged)")
        print(" 3. Files staged for commit")
        print(" Files only: .py, .ts, .mjs")
        return

    total_issues = []
    all_scores = []

    print("\n🔍Starting code analysis...")
    print("=" * 80)

    for file_path in files_to_check:
        full_path = os.path.join(repo_path, file_path)
        
        if not os.path.exists(full_path):
            print(f"\n⚠️The file {file_path} does not exist in the repository")
            continue

        # Get file status
        status = ""
        if file_path in subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                     capture_output=True, text=True).stdout.splitlines():
            status = "[Staged]"
        elif file_path in subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], 
                                       capture_output=True, text=True).stdout.splitlines():
            status = "[Nuevo]"
        else:
            status = "[Modificado]"
            
        print(f"\n📝 Analizing {file_path} {status}...")
        
        try:
            result = analyze_file(client, full_path)
            all_scores.append(result.code_quality_score)
            
            print(f"\n📊 Quality Score: {result.code_quality_score}/100")
            
            if not result.passed or result.code_quality_score < 70:
                total_issues.extend(result.issues)
                print(f"\n⚠️ Problems encountered in {file_path}:")
                print(f"Summary: {result.summary}")
                
                issues_by_category = {}
                for issue in result.issues:
                    if issue.category not in issues_by_category:
                        issues_by_category[issue.category] = []
                    issues_by_category[issue.category].append(issue)
                
                for category, issues in issues_by_category.items():
                    print(f"\n📌 {category.upper()}:")
                    for issue in issues:
                        print(f"\n  Severity: {issue.severity}")
                        print(f"  Problem: {issue.message}")
                        print(f"  Advice: {issue.suggestion}")
                        if issue.line_number:
                            print(f"  Línea: {issue.line_number}")
                        print("  " + "-" * 40)

        except Exception as e:
            print(f"❌ Error parsing {file_path}: {str(e)}")

    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        print(f"\n📊 Average project score: {avg_score:.2f}/100")

def setup_repository():
    print("🔍 Enter the path of the repository you want to check out")
    print("(Press Enter to use the current directory)")
    
    repo_path = input("Ruta: ").strip()
    
    if not repo_path:
        repo_path = os.getcwd()
    
    if not os.path.exists(repo_path):
        print("❌ The specified route does not exist")
        sys.exit(1)

    print(f"\n📂Selected repository: {repo_path}")

    if not os.path.exists(os.path.join(repo_path, '.git')):
        print("⚠️ Initializing git on the repository...")
        subprocess.run(['git', 'init'], cwd=repo_path)
        subprocess.run(['git', 'checkout', '-b', 'main'], cwd=repo_path)

    print("\n📝 Creating configuration files...")
    create_files(repo_path)

    print("\n📦 Installing dependencies...")
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'], cwd=repo_path)

    print("\n⚙️ Setting up pre-commit...")
    subprocess.run(['pre-commit', 'install'], cwd=repo_path)

    env_path = os.path.join(repo_path, '.env')
    if not os.path.exists(env_path):
        api_key = input("\n🔑 Enter your OpenAI API key: ").strip()
        with open(env_path, 'w') as f:
            f.write(f'OPENAI_API_KEY={api_key}\n')

    print("\n✅ Setup complete!")
    print("\n💡 The pre-commit hook is installed and ready to:")
    print(" 1. Scan new files (.py, .ts, .mjs) when using 'git add'")
    print(" 2. Review code before each commit")
    print("\nTo use:")
    print(" 1. Modify or create new files")
    print(" 2. Use 'git add' on the files you want to commit")
    print(" 3. Scanning will run automatically when doing 'git commit'")
if __name__ == "__main__":
    setup_repository()
