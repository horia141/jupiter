"""Some utilities."""
import importlib
import pkgutil
from types import ModuleType


def find_all_modules(
    *module_roots: ModuleType,
) -> list[ModuleType]:
    all_modules = []

    def explore_module_tree(the_module: ModuleType) -> None:
        for _, name, is_pkg in pkgutil.iter_modules(the_module.__path__):
            full_name = the_module.__name__ + "." + name
            all_modules.append(importlib.import_module(full_name))
            if is_pkg:
                submodule = getattr(the_module, name)
                explore_module_tree(submodule)

    for mr in module_roots:
        explore_module_tree(mr)
    return all_modules
