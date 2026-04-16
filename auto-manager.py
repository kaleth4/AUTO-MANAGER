#!/usr/bin/env python3
"""
Auto-Manager: Sistema de automatización para gestión de proyectos
Crea, verifica y gestiona proyectos automáticamente
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class ProjectManager:
    """Gestor automático de proyectos"""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.home() / "Desktop"
        self.projects = []
        self.log_file = self.base_path / "project-manager.log"

    def log(self, message: str):
        """Registra mensaje en log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def scan_projects(self) -> List[Dict]:
        """Escanea y cataloga proyectos existentes"""
        self.projects = []

        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
                project_info = self._analyze_project(item)
                self.projects.append(project_info)

        return self.projects

    def _analyze_project(self, project_path: Path) -> Dict:
        """Analiza un proyecto y extrae información"""
        info = {
            "name": project_path.name,
            "path": str(project_path),
            "has_readme": (project_path / "README.md").exists(),
            "file_count": len(list(project_path.rglob("*"))),
            "languages": [],
            "size_mb": 0
        }

        # Detectar lenguajes
        if list(project_path.rglob("*.py")):
            info["languages"].append("Python")
        if list(project_path.rglob("*.js")):
            info["languages"].append("JavaScript")
        if list(project_path.rglob("*.html")):
            info["languages"].append("HTML/CSS")
        if list(project_path.rglob("*.json")):
            info["languages"].append("JSON")

        # Calcular tamaño
        total_size = 0
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except:
                    pass

        info["size_mb"] = round(total_size / (1024 * 1024), 2)

        return info

    def generate_report(self) -> str:
        """Genera reporte de proyectos"""
        if not self.projects:
            self.scan_projects()

        report = f"""# 📊 Reporte de Proyectos

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Ubicación:** {self.base_path}

## Resumen

| Métrica | Valor |
|---------|-------|
| Total de Proyectos | {len(self.projects)} |
| Con README | {sum(1 for p in self.projects if p['has_readme'])} |
| Tamaño Total | {sum(p['size_mb'] for p in self.projects):.2f} MB |

## Proyectos

"""

        for project in sorted(self.projects, key=lambda x: x['name']):
            status = "✅" if project['has_readme'] else "❌"
            langs = ", ".join(project['languages']) if project['languages'] else "N/A"

            report += f"""### {project['name']}

- **README:** {status}
- **Archivos:** {project['file_count']}
- **Lenguajes:** {langs}
- **Tamaño:** {project['size_mb']} MB
- **Ruta:** `{project['path']}`

"""

        return report

    def verify_structure(self) -> Dict:
        """Verifica estructura de proyectos"""
        issues = []
        warnings = []

        for project in self.projects:
            if not project['has_readme']:
                issues.append(f"{project['name']}: Falta README.md")

            if project['file_count'] < 2:
                warnings.append(f"{project['name']}: Proyecto casi vacío")

        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    def create_requirements_files(self):
        """Crea archivos requirements.txt para proyectos Python"""
        created = 0

        for project in self.projects:
            if "Python" in project['languages']:
                req_file = Path(project['path']) / "requirements.txt"

                if not req_file.exists():
                    # Detectar imports
                    imports = self._detect_imports(Path(project['path']))

                    if imports:
                        with open(req_file, 'w') as f:
                            for imp in sorted(set(imports)):
                                f.write(f"{imp}\n")
                        created += 1
                        self.log(f"Creado {req_file}")

        return created

    def _detect_imports(self, project_path: Path) -> List[str]:
        """Detecta imports de un proyecto Python"""
        imports = set()

        for file_path in project_path.rglob("*.py"):
            try:
                content = file_path.read_text(encoding='utf-8')

                # Parsear imports
                for line in content.split('\n'):
                    if line.startswith('import ') or line.startswith('from '):
                        module = line.split()[1].split('.')[0]
                        if module not in ['os', 'sys', 'json', 're', 'pathlib',
                                        'typing', 'datetime', 'argparse',
                                        'subprocess', 'asyncio', 'collections',
                                        'dataclasses', 'enum', 'hashlib']:
                            imports.add(module)
            except:
                pass

        return list(imports)

    def generate_master_readme(self):
        """Genera README maestro con todos los proyectos"""
        readme = f"""# 🚀 Mis Proyectos

Colección de proyectos creados automáticamente.

## 📁 Lista de Proyectos

"""

        for project in sorted(self.projects, key=lambda x: x['name']):
            readme += f"- [{project['name']}](./{project['name']}/)\n"

        readme += f"""

## 📊 Estadísticas

- **Total:** {len(self.projects)} proyectos
- **Fecha de actualización:** {datetime.now().strftime('%Y-%m-%d')}

---
*Generado automáticamente por Auto-Manager*
"""

        readme_path = self.base_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)

        self.log(f"README maestro generado: {readme_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Manager de Proyectos")
    parser.add_argument("command",
                       choices=["scan", "report", "verify", "fix", "all"],
                       help="Comando a ejecutar")
    parser.add_argument("--path", default=None,
                       help="Ruta base de proyectos")

    args = parser.parse_args()

    manager = ProjectManager(args.path)

    print("=" * 60)
    print("🚀 AUTO-MANAGER DE PROYECTOS")
    print("=" * 60)
    print()

    if args.command == "scan" or args.command == "all":
        manager.log("Escaneando proyectos...")
        projects = manager.scan_projects()
        manager.log(f"Encontrados {len(projects)} proyectos")

        for p in projects:
            print(f"  📁 {p['name']}: {', '.join(p['languages'])}")

    if args.command == "report" or args.command == "all":
        if not manager.projects:
            manager.scan_projects()

        report = manager.generate_report()
        report_path = manager.base_path / "PROJECTS_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        manager.log(f"Reporte generado: {report_path}")

    if args.command == "verify" or args.command == "all":
        if not manager.projects:
            manager.scan_projects()

        result = manager.verify_structure()
        manager.log(f"Verificación: {'OK' if result['ok'] else 'CON PROBLEMAS'}")

        if result['issues']:
            print("\n❌ Problemas:")
            for issue in result['issues']:
                print(f"  - {issue}")

        if result['warnings']:
            print("\n⚠️  Advertencias:")
            for warning in result['warnings']:
                print(f"  - {warning}")

    if args.command == "fix" or args.command == "all":
        if not manager.projects:
            manager.scan_projects()

        manager.log("Creando archivos requirements.txt...")
        created = manager.create_requirements_files()
        manager.log(f"Creados {created} archivos requirements.txt")

        manager.log("Generando README maestro...")
        manager.generate_master_readme()

    print("\n" + "=" * 60)
    print("✅ Proceso completado")
    print(f"📝 Log guardado en: {manager.log_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
