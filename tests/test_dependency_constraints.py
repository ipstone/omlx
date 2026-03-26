from pathlib import Path
import tomllib
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
VENVSTACKS_PATH = REPO_ROOT / "packaging" / "venvstacks.toml"


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def _dependency_versions(requirements: list[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for requirement in requirements:
        if " @ " in requirement:
            name = requirement.split(" @ ", 1)[0]
            versions[name] = requirement
            continue
        if ">=" in requirement:
            name, version = requirement.split(">=", 1)
            versions[name] = version
            continue
        versions[requirement] = ""
    return versions


class DependencyConstraintTests(unittest.TestCase):
    def test_security_sensitive_dependency_floors_are_patched(self) -> None:
        pyproject = _load_toml(PYPROJECT_PATH)
        runtime_versions = _dependency_versions(pyproject["project"]["dependencies"])
        optional_versions = {
            group: _dependency_versions(requirements)
            for group, requirements in pyproject["project"]["optional-dependencies"].items()
        }
        dev_group_versions = _dependency_versions(pyproject["dependency-groups"]["dev"])

        self.assertEqual(runtime_versions["fastapi"], "0.109.1")
        self.assertEqual(runtime_versions["Pillow"], "10.2.0")
        self.assertEqual(optional_versions["mcp"]["mcp"], "1.23.0")
        self.assertEqual(optional_versions["dev"]["black"], "26.3.1")
        self.assertEqual(optional_versions["dev"]["mcp"], "1.23.0")
        self.assertEqual(dev_group_versions["black"], "26.3.1")
        self.assertEqual(dev_group_versions["mcp"], "1.23.0")

    def test_packaging_dependency_floors_match_pyproject_for_patched_packages(self) -> None:
        venvstacks = _load_toml(VENVSTACKS_PATH)
        framework_versions = _dependency_versions(venvstacks["frameworks"][0]["requirements"])

        self.assertEqual(framework_versions["fastapi"], "0.109.1")
        self.assertEqual(framework_versions["Pillow"], "10.2.0")
        self.assertEqual(framework_versions["mcp"], "1.23.0")


if __name__ == "__main__":
    unittest.main()
