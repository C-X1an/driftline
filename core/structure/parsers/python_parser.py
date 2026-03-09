from __future__ import annotations

import ast
from pathlib import Path

from core.structure.models import (
    StructuralGraph,
    Symbol,
    Dependency,
    LanguageParser,
)


class PythonParser:
    """
    Python structural parser using AST.
    """

    language = "python"

    # ---------------------------------------------------------
    # Parser contract
    # ---------------------------------------------------------

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix == ".py"

    def parse_file(self, file_path: Path) -> StructuralGraph:
        """
        Extract structural graph from a Python file.
        NEVER raises fatal errors.
        """
        from core.runtime.paths import find_repo_root

        repo_root = find_repo_root(file_path)
        graph = StructuralGraph(repo_id=str(repo_root))

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            return graph  # safe empty graph

        module_id = f"{file_path}::module"

        # -----------------------------------------------------
        # Module symbol
        # -----------------------------------------------------

        graph.add_symbol(
            Symbol(
                id=module_id,
                name=file_path.name,
                type="module",
                file_path=str(file_path),
            )
        )

        # -----------------------------------------------------
        # Walk AST
        # -----------------------------------------------------

        for node in ast.walk(tree):

            # ---------------------------------------------
            # Classes
            # ---------------------------------------------
            if isinstance(node, ast.ClassDef):

                class_id = f"{file_path}::{node.name}"

                graph.add_symbol(
                    Symbol(
                        id=class_id,
                        name=node.name,
                        type="class",
                        file_path=str(file_path),
                    )
                )

                graph.add_dependency(
                    Dependency(
                        source_id=module_id,
                        target_id=class_id,
                        type="defines",
                    )
                )

            # ---------------------------------------------
            # Functions
            # ---------------------------------------------
            elif isinstance(node, ast.FunctionDef):

                fn_id = f"{file_path}::{node.name}"

                params = [arg.arg for arg in node.args.args]

                graph.add_symbol(
                    Symbol(
                        id=fn_id,
                        name=node.name,
                        type="function",
                        file_path=str(file_path),
                        parameters=params,
                        return_type=None,
                    )
                )

                graph.add_dependency(
                    Dependency(
                        source_id=module_id,
                        target_id=fn_id,
                        type="defines",
                    )
                )

            # ---------------------------------------------
            # Imports
            # ---------------------------------------------
            elif isinstance(node, ast.Import):

                for alias in node.names:
                    graph.add_dependency(
                        Dependency(
                            source_id=module_id,
                            target_id=alias.name,
                            type="imports",
                        )
                    )

            elif isinstance(node, ast.ImportFrom):

                module = node.module or ""

                for alias in node.names:
                    target = f"{module}.{alias.name}"

                    graph.add_dependency(
                        Dependency(
                            source_id=module_id,
                            target_id=target,
                            type="imports",
                        )
                    )

            # ---------------------------------------------
            # Function calls
            # ---------------------------------------------
            elif isinstance(node, ast.Call):

                called_name = None

                if isinstance(node.func, ast.Name):
                    called_name = node.func.id

                elif isinstance(node.func, ast.Attribute):
                    called_name = node.func.attr

                if called_name:
                    graph.add_dependency(
                        Dependency(
                            source_id=module_id,
                            target_id=called_name,
                            type="calls",
                        )
                    )

        return graph