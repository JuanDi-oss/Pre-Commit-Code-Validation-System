import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional

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

# Contenido del archivo pre_commit_code_check.py
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
    """Analiza un archivo individual"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    messages = [
        {"role": "system", "content": """Analiza este código detalladamente y proporciona feedback específico para:
            1. Principios de código limpio:
               - Nombres de variables y funciones
               - Estructura y organización
               - Comentarios y documentación
               - Duplicación de código
            
            2. Mejores prácticas de seguridad:
               - Validación de entrada
               - Manejo de datos sensibles
               - Vulnerabilidades comunes
            
            3. Consideraciones de rendimiento:
               - Optimización de algoritmos
               - Uso de memoria
               - Complejidad temporal
            
            4. Seguridad de tipos:
               - Uso correcto de tipos
               - Type hints
               - Validación de tipos
            
            5. Manejo de errores:
               - Try/catch apropiados
               - Mensajes de error descriptivos
               - Logging
            
            Para cada problema encontrado, proporciona:
            - Severidad (alta/media/baja)
            - Mensaje claro del problema
            - Sugerencia específica de mejora
            - Categoría del problema
            - Línea de código específica cuando sea posible
            
            Asigna una puntuación de calidad del código de 0 a 100."""},
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
        print("No se encontraron archivos para analizar")
        sys.exit(0)

    total_issues = []
    all_scores = []
    failed = False

    print("\\n🔍 Iniciando análisis de código...")
    print("=" * 80)

    for file_path in files_to_check:
        print(f"\\n📝 Analizando {file_path}...")
        try:
            result = analyze_file(client, file_path)
            all_scores.append(result.code_quality_score)
            
            print(f"\\n📊 Puntuación de calidad: {result.code_quality_score}/100")
            
            if not result.passed or result.code_quality_score < 70:
                failed = True
                total_issues.extend(result.issues)
                print(f"\\n⚠️ Problemas encontrados en {file_path}:")
                print(f"Resumen: {result.summary}")
                
                issues_by_category = {}
                for issue in result.issues:
                    if issue.category not in issues_by_category:
                        issues_by_category[issue.category] = []
                    issues_by_category[issue.category].append(issue)
                
                for category, issues in issues_by_category.items():
                    print(f"\\n📌 {category.upper()}:")
                    for issue in issues:
                        print(f"\\n  Severidad: {issue.severity}")
                        print(f"  Problema: {issue.message}")
                        print(f"  Sugerencia: {issue.suggestion}")
                        if issue.line_number:
                            print(f"  Línea: {issue.line_number}")
                        print("  " + "-" * 40)

        except Exception as e:
            print(f"❌ Error analizando {file_path}: {str(e)}")
            sys.exit(1)

    print("\\n" + "=" * 80)
    if len(all_scores) > 0:
        avg_score = sum(all_scores) / len(all_scores)
        print(f"\\n📊 Puntuación promedio del proyecto: {avg_score:.2f}/100")

    if failed:
        print("\\n❌ Revisión fallida. Por favor, corrige los problemas antes de commitear.")
        sys.exit(1)
    else:
        print("\\n✅ ¡Todos los archivos pasaron la revisión!")
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
            print("\n💡 No se encontraron archivos nuevos o staged para analizar")
            print("   Para analizar archivos:")
            print("   1. Crea nuevos archivos .py, .ts o .mjs")
            print("   2. O modifica archivos existentes y haz 'git add'")
            
        return valid_files
        
    except Exception as e:
        print(f"\n❌ Error obteniendo archivos: {e}")
        return []

def analyze_file(client, file_path: str) -> AnalysisResult:
    """Analiza un archivo individual"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    messages = [
        {"role": "system", "content": """Analiza este código detalladamente para:
            1. Principios de código limpio
            2. Mejores prácticas de seguridad
            3. Consideraciones de rendimiento
            4. Seguridad de tipos
            5. Manejo de errores"""},
        {"role": "user", "content": f"Archivo {file_path}:\n{content}"}
    ]

    return client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_model=AnalysisResult
    )

def analyze_setup_files(repo_path: str, client) -> bool:
    """Analiza los archivos de configuración antes de instalarlos"""
    setup_files = [
        ('pre_commit_code_check.py', CODE_CHECK_CONTENT),
        ('setup_code_review.py', Path(__file__).read_text())
    ]
    
    print("\n🔍 Analizando archivos de configuración...")
    print("=" * 80)
    
    all_passed = True
    for filename, content in setup_files:
        print(f"\n📝 Analizando {filename}...")
        
        # Crear archivo temporal para análisis
        temp_path = os.path.join(repo_path, filename)
        with open(temp_path, 'w') as f:
            f.write(content)
            
        try:
            result = analyze_file(client, temp_path)
            print(f"\n📊 Puntuación de calidad: {result.code_quality_score}/100")
            
            if not result.passed or result.code_quality_score < 70:
                all_passed = False
                print(f"\n⚠️ Problemas encontrados en {filename}:")
                print(f"Resumen: {result.summary}")
                
                issues_by_category = {}
                for issue in result.issues:
                    if issue.category not in issues_by_category:
                        issues_by_category[issue.category] = []
                    issues_by_category[issue.category].append(issue)
                
                for category, issues in issues_by_category.items():
                    print(f"\n📌 {category.upper()}:")
                    for issue in issues:
                        print(f"\n  Severidad: {issue.severity}")
                        print(f"  Problema: {issue.message}")
                        print(f"  Sugerencia: {issue.suggestion}")
                        if issue.line_number:
                            print(f"  Línea: {issue.line_number}")
                        print("  " + "-" * 40)
            
        except Exception as e:
            print(f"❌ Error analizando {filename}: {str(e)}")
            all_passed = False
            
        os.remove(temp_path)  # Limpiar archivo temporal
    
    return all_passed

def create_files(repo_path):
    # Crear pre_commit_code_check.py
    with open(os.path.join(repo_path, 'pre_commit_code_check.py'), 'w') as f:
        f.write(CODE_CHECK_CONTENT.strip())
    
    # Crear .pre-commit-config.yaml
    precommit_config_content = '''
repos:
-   repo: local
    hooks:
    -   id: code-review
        name: Code Review AI
        entry: python pre_commit_code_check.py
        language: python
        types: [python, typescript, javascript]
        pass_filenames: false
'''
    with open(os.path.join(repo_path, '.pre-commit-config.yaml'), 'w') as f:
        f.write(precommit_config_content.strip())
    
    # Crear requirements.txt
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
        print("\n⚠️ No se encontraron archivos para analizar")
        print("💡 El análisis incluye:")
        print("   1. Archivos nuevos (untracked)")
        print("   2. Archivos modificados (unstaged)")
        print("   3. Archivos staged para commit")
        print("   Solo archivos: .py, .ts, .mjs")
        return

    total_issues = []
    all_scores = []

    print("\n🔍 Iniciando análisis de código...")
    print("=" * 80)

    for file_path in files_to_check:
        full_path = os.path.join(repo_path, file_path)
        
        if not os.path.exists(full_path):
            print(f"\n⚠️ El archivo {file_path} no existe en el repositorio")
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
            
        print(f"\n📝 Analizando {file_path} {status}...")
        
        try:
            result = analyze_file(client, full_path)
            all_scores.append(result.code_quality_score)
            
            print(f"\n📊 Puntuación de calidad: {result.code_quality_score}/100")
            
            if not result.passed or result.code_quality_score < 70:
                total_issues.extend(result.issues)
                print(f"\n⚠️ Problemas encontrados en {file_path}:")
                print(f"Resumen: {result.summary}")
                
                issues_by_category = {}
                for issue in result.issues:
                    if issue.category not in issues_by_category:
                        issues_by_category[issue.category] = []
                    issues_by_category[issue.category].append(issue)
                
                for category, issues in issues_by_category.items():
                    print(f"\n📌 {category.upper()}:")
                    for issue in issues:
                        print(f"\n  Severidad: {issue.severity}")
                        print(f"  Problema: {issue.message}")
                        print(f"  Sugerencia: {issue.suggestion}")
                        if issue.line_number:
                            print(f"  Línea: {issue.line_number}")
                        print("  " + "-" * 40)

        except Exception as e:
            print(f"❌ Error analizando {file_path}: {str(e)}")

    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        print(f"\n📊 Puntuación promedio del proyecto: {avg_score:.2f}/100")

def setup_repository():
    print("🔍 Ingresa la ruta del repositorio que quieres revisar")
    print("(Presiona Enter para usar el directorio actual)")
    
    repo_path = input("Ruta: ").strip()
    
    if not repo_path:
        repo_path = os.getcwd()
    
    if not os.path.exists(repo_path):
        print("❌ La ruta especificada no existe")
        sys.exit(1)

    print(f"\n📂 Repositorio seleccionado: {repo_path}")

    if not os.path.exists(os.path.join(repo_path, '.git')):
        print("⚠️ Inicializando git en el repositorio...")
        subprocess.run(['git', 'init'], cwd=repo_path)
        subprocess.run(['git', 'checkout', '-b', 'main'], cwd=repo_path)

    print("\n📝 Creando archivos de configuración...")
    create_files(repo_path)

    print("\n📦 Instalando dependencias...")
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'], cwd=repo_path)

    print("\n⚙️ Configurando pre-commit...")
    subprocess.run(['pre-commit', 'install'], cwd=repo_path)

    # Configurar API key en .env
    env_path = os.path.join(repo_path, '.env')
    if not os.path.exists(env_path):
        api_key = input("\n🔑 Ingresa tu OpenAI API key: ").strip()
        with open(env_path, 'w') as f:
            f.write(f'OPENAI_API_KEY={api_key}\n')

    print("\n✅ Configuración completada!")
    print("\n💡 El pre-commit hook está instalado y listo para:")
    print("   1. Analizar nuevos archivos (.py, .ts, .mjs) cuando uses 'git add'")
    print("   2. Revisar el código antes de cada commit")
    print("\nPara usar:")
    print("   1. Modifica o crea nuevos archivos")
    print("   2. Usa 'git add' en los archivos que quieres commitear")
    print("   3. El análisis se ejecutará automáticamente al hacer 'git commit'")
if __name__ == "__main__":
    setup_repository()