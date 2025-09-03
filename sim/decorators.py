from dataclasses import field, fields as dataclass_fields, is_dataclass
from functools import wraps

class_registry = {}  # class name -> dict with "cls", "rotations", "talents", "talent_cls", "options_cls"


def _ensure_class_registry_entry(class_name):
    """Helper to ensure a class entry exists in the registry with default structure."""
    return class_registry.setdefault(class_name, {
        "cls": None,
        "rotations": [],
        "talents": {},  # For @simtalent registered talent classes
        "talent_cls": None,  # For the primary talent class via @simclass
        "options_cls": None  # For the options class via @simclass
    })


def simclass(talent_cls, options_cls):
    """
    Register a simulation class, requiring its primary talent class and options class.
    Usage: @simclass(MyPrimaryTalentClass, MyOptionsClass)
    """
    def decorator(decorated_cls):
        cls_name = decorated_cls.__name__
        entry = _ensure_class_registry_entry(cls_name)
        entry["cls"] = decorated_cls
        entry["talent_cls"] = talent_cls
        entry["options_cls"] = options_cls
        return decorated_cls
    return decorator


def get_rotations(class_name):
    """Get available rotations for a class."""
    return class_registry.get(class_name, {}).get("rotations", [])


def _collect_simoptions(cls):
    """Collect simoption metadata from dataclass fields."""
    if not cls or not is_dataclass(cls):
        return []
    result = []
    for f in dataclass_fields(cls):
        if "simoption" in f.metadata:
            # Include spec, defaulting to None if not present
            spec = f.metadata.get("spec")
            result.append((f.name, f.metadata["simoption"], f.default, spec))
    return result


def get_options(class_name):
    """Instantiate the class and return its options as (name, description, default, spec) tuples."""
    entry = class_registry.get(class_name, {})
    # This function might be simplified if options_cls is used directly from the registry:
    # options_cls = entry.get("options_cls")
    # if options_cls:
    #     return _collect_simoptions(options_cls)
    # Fallback to original behavior or adjust as needed:
    cls = entry.get("cls")
    if cls is None:
        return []
    try:
        try:
            instance = cls(tal=None)
        except TypeError:
            instance = cls()

        opts = getattr(instance, "opts", None)
        if opts is None:
            return []
        return _collect_simoptions(type(opts))
    except Exception:
        return []


def _collect_equipped_items(cls):
    """Collect simequipped metadata from dataclass fields."""
    if not cls or not is_dataclass(cls):
        return []
    result = []
    for f in dataclass_fields(cls):
        if "simequipped" in f.metadata:
            result.append((f.name, f.metadata["simequipped"], f.default))
    return result


def get_equipped_items(cls):
    """Return equipped items as (name, description, default) tuples using EquippedItems class."""
    return _collect_equipped_items(cls)


def get_talents(class_name):
    """Instantiate the class and return its talents."""
    entry = class_registry.get(class_name, {})
    cls = entry.get("cls")
    if cls is None:
        return None
    try:
        try:
            instance = cls(tal=None)
        except TypeError:
            instance = cls()
        return getattr(instance, "tal", None)
    except Exception:
        return None


def simrotation(name):
    """Register a rotation for a class with a human-readable name."""

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            return method(self, *args, **kwargs)

        cls_name = method.__qualname__.split('.')[0]
        entry = _ensure_class_registry_entry(cls_name)

        rotation_tuple = (name, method.__name__)
        if rotation_tuple not in entry["rotations"]:
            entry["rotations"].append(rotation_tuple)

        return wrapper

    return decorator


def simtalent(name):
    """Decorator to register a talent spec for a class with a human-readable name."""

    def decorator(talent_cls):
        base_class_name = None
        if hasattr(talent_cls, '_sim_target_class'):
            base_class_name = talent_cls._sim_target_class
        else:
            for base in talent_cls.__bases__:
                if base.__name__.endswith("Talents"):
                    base_class_name = base.__name__
                    base_class_name = base_class_name[:-7]
                    break

            if not base_class_name and "Talents" in talent_cls.__name__:
                for class_name_in_registry in class_registry:
                    if class_name_in_registry in talent_cls.__name__:
                        base_class_name = class_name_in_registry
                        break

        if base_class_name:
            entry = _ensure_class_registry_entry(base_class_name)
            entry["talents"][name] = talent_cls

        return talent_cls

    return decorator


def simoption(description, default=None, spec=None):
    """Field-level decorator for dataclass fields to add sim option metadata."""
    return field(default=default, metadata={"simoption": description, "spec": spec})


def simequipped(description, default=None):
    """Field-level decorator for dataclass fields to add equipped item metadata."""
    return field(default=default, metadata={"simequipped": description})
