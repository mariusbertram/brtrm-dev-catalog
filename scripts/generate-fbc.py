#!/usr/bin/env python3
"""
Generate FBC per operator sequentially.

This script processes each operator independently:
1. Load operator.yaml template
2. Render FBC for that operator
3. Write to operator-specific directory

No combining/splitting needed!
"""

import os
import sys
import yaml
import subprocess
import base64
from pathlib import Path
from typing import Dict, Any, Optional


class SequentialFBCGenerator:
    """Generator that processes operators sequentially."""

    def __init__(self, catalog_dir: str = "catalog", output_dir: str = "catalog/fbc"):
        self.catalog_dir = Path(catalog_dir)
        self.output_dir = Path(output_dir)

    def find_operator_dirs(self) -> Dict[str, Path]:
        """Find all operator directories with operator.yaml."""
        operators = {}

        for operator_dir in self.catalog_dir.iterdir():
            if not operator_dir.is_dir() or operator_dir.name == 'fbc':
                continue

            operator_yaml = operator_dir / "operator.yaml"
            if operator_yaml.exists():
                operators[operator_dir.name] = operator_yaml

        return operators

    def encode_logo(self, logo_path: Path) -> Optional[str]:
        """Encode logo file to base64."""
        if not logo_path.exists():
            return None

        try:
            with open(logo_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"  ⚠ Failed to encode logo: {e}", file=sys.stderr)
            return None

    def process_template(self, template_path: Path, base_path: Path) -> Dict[str, Any]:
        """Load and process operator template."""
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)

        if not template:
            return None

        schema = template.get('schema', '')

        # Process logo for semver templates
        if schema == 'olm.semver' and 'icon' in template:
            logo_ref = template['icon'].get('base64data', '')
            if logo_ref and logo_ref.endswith('.svg'):
                logo_path = base_path / logo_ref
                encoded = self.encode_logo(logo_path)
                if encoded:
                    template['icon']['base64data'] = encoded
                else:
                    del template['icon']

        # Process logo for basic templates
        elif schema == 'olm.template.basic' and 'entries' in template:
            for entry in template['entries']:
                if entry.get('schema') == 'olm.package' and 'icon' in entry:
                    logo_ref = entry['icon'].get('base64data', '')
                    if logo_ref and logo_ref.endswith('.svg'):
                        logo_path = base_path / logo_ref
                        encoded = self.encode_logo(logo_path)
                        if encoded:
                            entry['icon']['base64data'] = encoded
                        else:
                            del entry['icon']

        return template

    def render_template(self, template: Dict[str, Any], operator_name: str) -> Optional[str]:
        """Render template using opm."""
        schema = template.get('schema', '')

        # Determine template type
        if schema == 'olm.semver':
            template_type = 'semver'
        elif schema == 'olm.template.basic':
            template_type = 'basic'
        else:
            print(f"  ⚠ Unknown schema: {schema}", file=sys.stderr)
            return None

        # Write template to temp file
        temp_file = f"/tmp/operator-{operator_name}.yaml"
        with open(temp_file, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)

        # Render with opm
        try:
            result = subprocess.run(
                ['opm', 'alpha', 'render-template', template_type, temp_file, '-o', 'yaml'],
                capture_output=True,
                text=True,
                check=True
            )
            os.remove(temp_file)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"  ✗ opm render failed: {e.stderr}", file=sys.stderr)
            os.remove(temp_file)
            return None
        except FileNotFoundError:
            print(f"  ✗ opm not found", file=sys.stderr)
            os.remove(temp_file)
            return None

    def generate_fbc(self) -> bool:
        """Generate FBC for all operators sequentially."""
        operators = self.find_operator_dirs()

        if not operators:
            print("Error: No operator.yaml files found", file=sys.stderr)
            return False

        print(f"Found {len(operators)} operator(s)")
        print("=" * 60)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        failed_operators = []

        # Process each operator sequentially
        for operator_name, template_path in operators.items():
            print(f"\nProcessing: {operator_name}")
            base_path = template_path.parent

            # 1. Load template
            template = self.process_template(template_path, base_path)
            if not template:
                print(f"  ✗ Failed to load template")
                failed_operators.append(operator_name)
                continue

            schema = template.get('schema', '')
            print(f"  → Template type: {schema}")

            # 2. Render FBC
            rendered_fbc = self.render_template(template, operator_name)
            if not rendered_fbc:
                print(f"  ✗ Failed to render FBC")
                failed_operators.append(operator_name)
                continue

            # Count objects
            doc_count = rendered_fbc.count('\n---\n') + 1
            print(f"  → Rendered {doc_count} object(s)")

            # 3. Write to operator directory
            operator_dir = self.output_dir / operator_name
            operator_dir.mkdir(parents=True, exist_ok=True)

            index_file = operator_dir / 'index.yaml'
            with open(index_file, 'w') as f:
                f.write(rendered_fbc)

            print(f"  ✓ Written to {operator_dir.relative_to(self.catalog_dir)}/index.yaml")
            success_count += 1

        # Summary
        print("\n" + "=" * 60)
        print(f"✓ Successfully processed: {success_count}/{len(operators)} operator(s)")

        if failed_operators:
            print(f"✗ Failed operators: {', '.join(failed_operators)}")
            return False

        print(f"\nFBC generated in: {self.output_dir}")
        return True


def main():
    """Main entry point."""
    generator = SequentialFBCGenerator()
    success = generator.generate_fbc()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
