#!/usr/bin/env python3
"""
Script para llenar contribuciones de GitHub
Crea commits automáticamente desde una fecha específica hasta hoy
"""

import os
import subprocess
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse

class GitHubContributionsFiller:
    def __init__(self, repo_path=".", start_date=None, author_name=None, author_email=None):
        self.repo_path = Path(repo_path).resolve()
        self.start_date = start_date or (datetime.now() - timedelta(days=365))
        self.end_date = datetime.now()
        self.original_cwd = Path.cwd()
        self.author_name = author_name
        self.author_email = author_email
        
    def _run_git_command(self, command, env=None, check=True):
        """Ejecuta un comando git con manejo de errores mejorado"""
        try:
            result = subprocess.run(
                command, 
                check=check, 
                env=env,
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error ejecutando comando Git: {' '.join(command)}")
            print(f"Salida de error: {e.stderr}")
            raise
    
    def _check_git_installed(self):
        """Verifica que Git esté instalado"""
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Error: Git no está instalado o no está disponible en PATH")
            print("Por favor instala Git: https://git-scm.com/downloads")
            sys.exit(1)
    
    def _setup_git_config(self):
        """Configura Git localmente para este repositorio"""
        try:
            # Verificar configuración actual (local primero, luego global)
            name_result = self._run_git_command(['git', 'config', 'user.name'], check=False)
            email_result = self._run_git_command(['git', 'config', 'user.email'], check=False)
            
            name_configured = name_result.returncode == 0 and name_result.stdout.strip()
            email_configured = email_result.returncode == 0 and email_result.stdout.strip()
            
            if name_configured and email_configured:
                print(f"✅ Git configurado: {name_result.stdout.strip()} <{email_result.stdout.strip()}>")
                return True
            
            # Si no está configurado, usar parámetros o configurar localmente
            print("⚙️  Configurando Git localmente para este repositorio...")
            
            if not name_configured:
                name = self.author_name or input(f"Nombre para commits (Enter para 'GitHub Contributions Bot'): ").strip() or "GitHub Contributions Bot"
                self._run_git_command(['git', 'config', 'user.name', name])
                print(f"✅ Nombre configurado localmente: {name}")
            
            if not email_configured:
                email = self.author_email or input(f"Email para commits (Enter para 'contributions@example.com'): ").strip() or "contributions@example.com"
                self._run_git_command(['git', 'config', 'user.email', email])
                print(f"✅ Email configurado localmente: {email}")
            
            return True
            
        except Exception as e:
            print(f"Error configurando Git: {e}")
            return False
    
    def setup_repository(self):
        """Configura el repositorio en el directorio actual o especificado"""
        # Verificar prerrequisitos
        self._check_git_installed()
        
        # Si es el directorio actual, no crear carpeta nueva
        if self.repo_path != Path.cwd():
            # Crear directorio si no existe
            try:
                self.repo_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print(f"❌ Error: No hay permisos para crear el directorio {self.repo_path}")
                sys.exit(1)
        
        # Verificar si ya es un repositorio git
        git_dir = self.repo_path / '.git'
        if not git_dir.exists():
            print(f"Inicializando repositorio Git en: {self.repo_path}")
            # Usar git init con -b main para versiones más nuevas, fallback para versiones antiguas
            try:
                self._run_git_command(['git', 'init', '-b', 'main'])
                print("Repositorio Git inicializado con rama 'main'")
            except subprocess.CalledProcessError:
                # Fallback para versiones antiguas de Git
                self._run_git_command(['git', 'init'])
                try:
                    self._run_git_command(['git', 'checkout', '-b', 'main'])
                except subprocess.CalledProcessError:
                    # Si ya existe main o hay otro problema, continuar
                    pass
                print("Repositorio Git inicializado")
        else:
            print(f"Usando repositorio Git existente en: {self.repo_path}")
        
        # Configurar Git localmente
        if not self._setup_git_config():
            print("❌ Error: No se pudo configurar Git")
            sys.exit(1)
        
        # Crear archivos iniciales
        self._create_initial_files()
    
    def _create_initial_files(self):
        """Crea archivos iniciales del repositorio"""
        readme_path = self.repo_path / 'README.md'
        data_path = self.repo_path / 'data.txt'
        
        if not readme_path.exists():
            try:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write("# Contribuciones Automáticas\n\n")
                    f.write("Este repositorio fue creado para llenar contribuciones de GitHub.\n\n")
                    f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            except IOError as e:
                print(f"Error creando README.md: {e}")
                sys.exit(1)
        
        if not data_path.exists():
            try:
                with open(data_path, 'w', encoding='utf-8') as f:
                    f.write("Archivo de datos para commits automáticos\n")
                    f.write(f"Iniciado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            except IOError as e:
                print(f"Error creando data.txt: {e}")
                sys.exit(1)
    
    def create_commit(self, date, message=None):
        """Crea un commit en una fecha específica"""
        if not message:
            messages = [
                "Actualización automática",
                "Progreso diario", 
                "Mejoras menores",
                "Actualización de datos",
                "Commit automático",
                "Mantenimiento del código",
                "Actualización de documentación",
                "Refactoring menor",
                "Optimización de código",
                "Corrección de bugs menores"
            ]
            message = random.choice(messages)
        
        # Modificar archivo para hacer el commit
        data_path = self.repo_path / 'data.txt'
        try:
            with open(data_path, 'a', encoding='utf-8') as f:
                f.write(f"Entrada del {date.strftime('%Y-%m-%d %H:%M:%S')} - {random.randint(1000, 9999)}\n")
        except IOError as e:
            print(f"Error modificando data.txt: {e}")
            return False
        
        # Configurar fecha del commit
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        env = os.environ.copy()
        env['GIT_COMMITTER_DATE'] = date_str
        env['GIT_AUTHOR_DATE'] = date_str
        
        try:
            # Hacer commit
            self._run_git_command(['git', 'add', '.'], env=env)
            self._run_git_command(['git', 'commit', '-m', message], env=env)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creando commit para {date_str}: {e}")
            return False
    
    def should_commit_today(self, date):
        """Determina si debe hacer commit en esta fecha"""
        # No hacer commits en fechas futuras
        if date > datetime.now():
            return False
            
        # Evitar domingos ocasionalmente para parecer más natural
        if date.weekday() == 6 and random.random() < 0.4:
            return False
        
        # Hacer commits con mayor probabilidad en días laborables
        if date.weekday() < 5:  # Lunes a Viernes
            return random.random() < 0.85
        else:  # Fines de semana
            return random.random() < 0.5
    
    def validate_dates(self):
        """Valida que las fechas sean correctas"""
        if self.start_date >= self.end_date:
            print("❌ Error: La fecha de inicio debe ser anterior a la fecha de fin")
            return False
        
        if self.start_date > datetime.now():
            print("❌ Error: La fecha de inicio no puede estar en el futuro")
            return False
        
        # Advertir si el rango es muy grande
        days_diff = (self.end_date - self.start_date).days
        if days_diff > 400:
            print(f"⚠️  Advertencia: Vas a generar commits para {days_diff} días")
            response = input("¿Estás seguro de continuar? (y/n): ").lower()
            if response not in ['y', 'yes', 'sí', 's']:
                return False
        
        return True
    
    def generate_commits(self, intensity='medium'):
        """Genera commits para el período especificado"""
        # Validar fechas
        if not self.validate_dates():
            return False
        
        intensity_map = {
            'low': (1, 2),      # 1-2 commits por día
            'medium': (1, 4),   # 1-4 commits por día  
            'high': (2, 6),     # 2-6 commits por día
            'very_high': (3, 10) # 3-10 commits por día
        }
        
        if intensity not in intensity_map:
            print(f"❌ Error: Intensidad '{intensity}' no válida. Usa: {list(intensity_map.keys())}")
            return False
        
        min_commits, max_commits = intensity_map[intensity]
        
        current_date = self.start_date
        total_commits = 0
        successful_commits = 0
        
        print(f"Generando commits desde {self.start_date.strftime('%Y-%m-%d')} hasta {self.end_date.strftime('%Y-%m-%d')}")
        print(f"Intensidad: {intensity} ({min_commits}-{max_commits} commits por día)")
        print("-" * 60)
        
        while current_date <= self.end_date:
            if self.should_commit_today(current_date):
                # Número aleatorio de commits para este día
                daily_commits = random.randint(min_commits, max_commits)
                
                for i in range(daily_commits):
                    # Hora aleatoria del día (horario laboral más probable)
                    if random.random() < 0.7:  # 70% en horario laboral
                        random_hour = random.randint(9, 18)
                    else:  # 30% fuera de horario laboral
                        random_hour = random.choice(list(range(7, 9)) + list(range(19, 23)))
                    
                    random_minute = random.randint(0, 59)
                    random_second = random.randint(0, 59)
                    
                    commit_time = current_date.replace(
                        hour=random_hour, 
                        minute=random_minute, 
                        second=random_second
                    )
                    
                    # Evitar commits en el futuro
                    if commit_time > datetime.now():
                        continue
                    
                    if self.create_commit(commit_time):
                        successful_commits += 1
                    
                    total_commits += 1
                    
                    if total_commits % 100 == 0:
                        print(f"Progreso: {successful_commits}/{total_commits} commits exitosos...")
            
            current_date += timedelta(days=1)
        
        print("-" * 60)
        print(f"✅ Proceso completado!")
        print(f"Total de commits intentados: {total_commits}")
        print(f"Commits exitosos: {successful_commits}")
        if total_commits > successful_commits:
            print(f"Commits fallidos: {total_commits - successful_commits}")
        print(f"Repositorio local: {self.repo_path}")
        
        return successful_commits > 0
    
    def setup_remote_repository(self, repo_url):
        """Configura el repositorio remoto"""
        if not repo_url:
            print("❌ Error: URL del repositorio no proporcionada")
            return False
        
        # Validar formato básico de URL
        if not (repo_url.startswith('https://github.com/') or 
                repo_url.startswith('git@github.com:') or
                repo_url.startswith('https://gitlab.com/') or
                repo_url.startswith('git@gitlab.com:')):
            print("⚠️  Advertencia: La URL no parece ser de GitHub o GitLab")
        
        try:
            # Verificar si ya existe un remote
            result = self._run_git_command(['git', 'remote', 'get-url', 'origin'], check=False)
            
            if result.returncode == 0:
                existing_url = result.stdout.strip()
                if existing_url == repo_url:
                    print("Remote 'origin' ya está configurado correctamente")
                    return True
                else:
                    print(f"Remote 'origin' existe con URL diferente: {existing_url}")
                    response = input("¿Quieres actualizarlo? (y/n): ").lower()
                    if response in ['y', 'yes', 'sí', 's']:
                        self._run_git_command(['git', 'remote', 'set-url', 'origin', repo_url])
                        print(f"Remote actualizado: {repo_url}")
                        return True
                    else:
                        return False
            else:
                self._run_git_command(['git', 'remote', 'add', 'origin', repo_url])
                print(f"Remote agregado: {repo_url}")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"Error configurando remote: {e}")
            return False
    
    def push_to_github(self):
        """Sube los commits a GitHub"""
        try:
            print("Verificando conexión con el repositorio remoto...")
            
            # Verificar que existe el remote
            result = self._run_git_command(['git', 'remote', 'get-url', 'origin'], check=False)
            if result.returncode != 0:
                print("❌ Error: No hay repositorio remoto configurado")
                return False
            
            print("Subiendo commits a GitHub...")
            
            # Intentar push
            try:
                self._run_git_command(['git', 'push', '-u', 'origin', 'main'])
                print("✅ Commits subidos exitosamente a GitHub!")
                return True
            except subprocess.CalledProcessError:
                # Intentar forzar push si hay conflictos
                print("Detectado posible conflicto, intentando push forzado...")
                response = input("¿Quieres hacer push forzado? Esto sobrescribirá el repositorio remoto (y/n): ").lower()
                if response in ['y', 'yes', 'sí', 's']:
                    self._run_git_command(['git', 'push', '--force', 'origin', 'main'])
                    print("✅ Push forzado exitoso!")
                    return True
                else:
                    print("Push cancelado")
                    return False
                    
        except subprocess.CalledProcessError as e:
            print(f"❌ Error subiendo a GitHub: {e}")
            print("\nPosibles soluciones:")
            print("1. Verifica que el repositorio remoto existe")
            print("2. Verifica que tienes permisos de escritura")
            print("3. Verifica tu autenticación (token/SSH)")
            print("4. Verifica que la rama principal es 'main'")
            return False
    
    def cleanup_on_error(self):
        """Limpia recursos en caso de error"""
        try:
            os.chdir(self.original_cwd)
        except:
            pass

def parse_date(date_string):
    """Parsea una fecha string a datetime"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        print(f"❌ Error: Formato de fecha inválido '{date_string}'. Usa YYYY-MM-DD")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Llenar contribuciones de GitHub con commits automáticos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s --start-date 2024-01-01 --intensity medium
  %(prog)s --repo-url https://github.com/usuario/repo.git --intensity high
  %(prog)s --start-date 2023-06-01 --local-path ./mi-repo --intensity low
  %(prog)s --author-name "Mi Nombre" --author-email "mi@email.com"
        """
    )
    
    parser.add_argument('--start-date', type=str, 
                       help='Fecha inicio (YYYY-MM-DD)', 
                       default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    parser.add_argument('--intensity', 
                       choices=['low', 'medium', 'high', 'very_high'], 
                       default='medium', 
                       help='Intensidad de commits (default: medium)')
    parser.add_argument('--repo-url', type=str, 
                       help='URL del repositorio de GitHub/GitLab')
    parser.add_argument('--local-path', type=str, 
                       default='.',
                       help='Ruta local del repositorio (default: directorio actual)')
    parser.add_argument('--author-name', type=str,
                       help='Nombre del autor para commits (default: GitHub Contributions Bot)')
    parser.add_argument('--author-email', type=str,
                       help='Email del autor para commits (default: contributions@example.com)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simular ejecución sin crear commits')
    
    args = parser.parse_args()
    
    # Validar y convertir fecha
    start_date = parse_date(args.start_date)
    
    # Mostrar información antes de comenzar
    print("🚀 Generador de Contribuciones de GitHub")
    print("=" * 50)
    print(f"Fecha inicio: {start_date.strftime('%Y-%m-%d')}")
    print(f"Fecha fin: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Intensidad: {args.intensity}")
    print(f"Ruta local: {args.local_path}")
    if args.repo_url:
        print(f"Repositorio remoto: {args.repo_url}")
    print("=" * 50)
    
    if args.dry_run:
        print("🔍 MODO DRY-RUN - No se crearán commits reales")
        days = (datetime.now() - start_date).days
        print(f"Se procesarían aproximadamente {days} días")
        return
    
    # Confirmar antes de proceder
    response = input("\n¿Continuar con la generación de commits? (y/n): ").lower()
    if response not in ['y', 'yes', 'sí', 's']:
        print("Operación cancelada")
        return
    
    filler = None
    try:
        # Crear instancia del generador
        filler = GitHubContributionsFiller(
            repo_path=args.local_path, 
            start_date=start_date,
            author_name=args.author_name,
            author_email=args.author_email
        )
        
        # Configurar repositorio
        print("\n📁 Configurando repositorio local...")
        filler.setup_repository()
        
        # Generar commits
        print("\n💻 Generando commits...")
        success = filler.generate_commits(intensity=args.intensity)
        
        if not success:
            print("❌ No se pudieron generar commits")
            return
        
        # Configurar remote si se proporciona
        if args.repo_url:
            print("\n🔗 Configurando repositorio remoto...")
            if filler.setup_remote_repository(args.repo_url):
                # Preguntar si quiere subir a GitHub
                response = input("\n¿Quieres subir los commits al repositorio remoto ahora? (y/n): ").lower()
                if response in ['y', 'yes', 'sí', 's']:
                    success = filler.push_to_github()
                    if success:
                        print("\n🎉 ¡Proceso completado exitosamente!")
                        print("Revisa tu perfil de GitHub para ver las contribuciones")
                else:
                    print("\n📝 Para subir manualmente más tarde:")
                    print(f"   cd {args.local_path}")
                    print("   git push -u origin main")
        else:
            print("\n📝 Pasos siguientes:")
            print("1. Crea un repositorio en GitHub")
            if args.local_path == '.':
                print("2. Ejecuta los siguientes comandos en este directorio:")
                print("   git remote add origin <URL_DE_TU_REPO>")
                print("   git push -u origin main")
            else:
                print("2. Ejecuta los siguientes comandos:")
                print(f"   cd {args.local_path}")
                print("   git remote add origin <URL_DE_TU_REPO>")
                print("   git push -u origin main")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Operación interrumpida por el usuario")
        if filler:
            filler.cleanup_on_error()
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        if filler:
            filler.cleanup_on_error()
        sys.exit(1)

if __name__ == "__main__":
    main()