"""Observe Python import syntax without consulting boundary ownership policy."""

from __future__ import annotations

import ast

from .boundary_map import (
    DependencyObservationStatus,
    PythonImportKind,
    PythonImportObservation,
    SourceDependencyObservation,
)

_DYNAMIC_BUILTINS = frozenset({"__import__", "eval", "exec"})


def _target_names(target: ast.expr) -> tuple[str, ...]:
    if isinstance(target, ast.Name):
        return (target.id,)
    if isinstance(target, (ast.Tuple, ast.List)):
        return tuple(name for child in target.elts for name in _target_names(child))
    return ()


def _dynamic_function_expression(
    expression: ast.expr,
    loader_names: set[str],
    builtin_modules: set[str],
    importlib_modules: set[str],
) -> bool:
    if isinstance(expression, ast.NamedExpr):
        return _dynamic_function_expression(
            expression.value, loader_names, builtin_modules, importlib_modules
        )
    if isinstance(expression, ast.Name):
        return expression.id in loader_names
    if isinstance(expression, ast.Attribute) and isinstance(expression.value, ast.Name):
        return (
            expression.value.id in builtin_modules
            and expression.attr in _DYNAMIC_BUILTINS
        ) or (
            expression.value.id in importlib_modules
            and expression.attr == "import_module"
        )
    if isinstance(expression, ast.Call) and isinstance(expression.func, ast.Name):
        if expression.func.id != "getattr" or len(expression.args) < 2:
            return False
        target, attribute = expression.args[:2]
        if (
            not isinstance(target, ast.Name)
            or not isinstance(attribute, ast.Constant)
            or not isinstance(attribute.value, str)
        ):
            return False
        return (
            target.id in builtin_modules and attribute.value in _DYNAMIC_BUILTINS
        ) or (
            target.id in importlib_modules and attribute.value == "import_module"
        )
    return False


def _has_dynamic_loader_call(tree: ast.AST) -> bool:
    loader_names = set(_DYNAMIC_BUILTINS)
    builtin_modules: set[str] = set()
    importlib_modules: set[str] = set()
    nodes = tuple(ast.walk(tree))

    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"builtins", "__builtin__"}:
                    builtin_modules.add(alias.asname or alias.name)
                elif alias.name == "importlib":
                    importlib_modules.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module in {"builtins", "__builtin__"}:
                loader_names.update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name in _DYNAMIC_BUILTINS
                )
            elif node.module == "importlib":
                loader_names.update(
                    alias.asname or alias.name
                    for alias in node.names
                    if alias.name == "import_module"
                )

    changed = True
    while changed:
        changed = False
        for node in nodes:
            if isinstance(node, ast.Assign) and _dynamic_function_expression(
                node.value, loader_names, builtin_modules, importlib_modules
            ):
                for target in node.targets:
                    for name in _target_names(target):
                        if name not in loader_names:
                            loader_names.add(name)
                            changed = True
            elif isinstance(node, ast.AnnAssign) and node.value is not None and _dynamic_function_expression(
                node.value, loader_names, builtin_modules, importlib_modules
            ):
                for name in _target_names(node.target):
                    if name not in loader_names:
                        loader_names.add(name)
                        changed = True
            elif isinstance(node, ast.NamedExpr) and _dynamic_function_expression(
                node.value, loader_names, builtin_modules, importlib_modules
            ):
                for name in _target_names(node.target):
                    if name not in loader_names:
                        loader_names.add(name)
                        changed = True

    for node in nodes:
        if isinstance(node, ast.Call) and _dynamic_function_expression(
            node.func, loader_names, builtin_modules, importlib_modules
        ):
            return True
    return False


def _relative_module_name(
    source_path: str, level: int, module: str | None
) -> str | None:
    if not source_path.endswith((".py", ".pyi")) or level < 1:
        return None
    components = source_path.rsplit("/", 1)[0].split("/") if "/" in source_path else []
    if not components or any(not part.isidentifier() for part in components):
        return None
    ascend = level - 1
    if ascend >= len(components):
        return None
    package = components[: len(components) - ascend]
    if module:
        module_parts = module.split(".")
        if any(not part.isidentifier() for part in module_parts):
            return None
        package.extend(module_parts)
    return ".".join(package) if package else None


def observe_python_dependencies(
    source_path: str, source: bytes
) -> SourceDependencyObservation:
    """Parse one Python blob into finite import observations, or fail closed."""

    if type(source) is not bytes:
        return SourceDependencyObservation(
            DependencyObservationStatus.NOT_VERIFIED,
            detail="NOT_VERIFIED: candidate Python blob is not exact bytes",
        )
    try:
        tree = ast.parse(source.decode("utf-8"), filename=source_path, type_comments=True)
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return SourceDependencyObservation(
            DependencyObservationStatus.NOT_VERIFIED,
            detail="NOT_VERIFIED: changed Python source cannot be parsed as UTF-8 Python",
        )
    if _has_dynamic_loader_call(tree):
        return SourceDependencyObservation(
            DependencyObservationStatus.NOT_VERIFIED,
            detail="NOT_VERIFIED: changed Python source uses unresolved dynamic loading",
        )

    imports: list[PythonImportObservation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                PythonImportObservation(PythonImportKind.MODULE, alias.name)
                for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            module_name = (
                node.module or ""
                if node.level == 0
                else _relative_module_name(source_path, node.level, node.module)
            )
            if module_name is None:
                return SourceDependencyObservation(
                    DependencyObservationStatus.NOT_VERIFIED,
                    detail="NOT_VERIFIED: relative import escapes its source package",
                )
            imports.append(
                PythonImportObservation(
                    PythonImportKind.FROM_MODULE,
                    module_name,
                    tuple(alias.name for alias in node.names),
                )
            )
    return SourceDependencyObservation(
        DependencyObservationStatus.OBSERVED,
        imports=tuple(imports),
    )


__all__ = ["observe_python_dependencies"]
