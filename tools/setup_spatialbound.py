#!/usr/bin/env python3
"""
Setup SpatialBound Integration
Interactive script to configure SpatialBound API credentials
"""

import sys
import os
from pathlib import Path
import json
import getpass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.spatialbound_integration import create_spatialbound_config, SpatialBoundClient


def main():
    """Main setup function"""
    print("="*80)
    print("SPATIALBOUND 4D VISUALIZATION SETUP")
    print("="*80)
    print()
    print("This script will help you configure SpatialBound API credentials")
    print("for 4D visualization of your NbS planning results.")
    print()
    
    # Get API key
    print("Step 1: API Key")
    print("-" * 40)
    print("You can get your API key from: https://www.spatialbound.com/doc")
    print()
    
    api_key = getpass.getpass("Enter your SpatialBound API key: ").strip()
    
    if not api_key:
        print("\n❌ No API key provided. Exiting.")
        return 1
    
    # Optional: Custom base URL
    print("\nStep 2: API Configuration (Optional)")
    print("-" * 40)
    
    use_default = input("Use default API URL? (Y/n): ").strip().lower()
    
    if use_default in ['n', 'no']:
        base_url = input("Enter custom API URL: ").strip()
    else:
        base_url = "https://api.spatialbound.com/v1"
    
    print(f"\nUsing API URL: {base_url}")
    
    # Save configuration
    print("\nStep 3: Save Configuration")
    print("-" * 40)
    
    save_location = input("Save to home directory? (Y/n): ").strip().lower()
    
    if save_location in ['n', 'no']:
        config_path = input("Enter config file path: ").strip()
        config_path = Path(config_path)
    else:
        config_path = Path.home() / '.spatialbound_config'
    
    # Create config
    try:
        config_file = create_spatialbound_config(api_key, config_path)
        print(f"\n✓ Configuration saved to: {config_file}")
    except Exception as e:
        print(f"\n❌ Failed to save configuration: {e}")
        return 1
    
    # Test connection
    print("\nStep 4: Test Connection")
    print("-" * 40)
    
    test = input("Test connection to SpatialBound API? (Y/n): ").strip().lower()
    
    if test not in ['n', 'no']:
        print("\nTesting connection...")
        
        try:
            client = SpatialBoundClient(api_key=api_key, base_url=base_url)
            
            if client.test_connection():
                print("✓ Successfully connected to SpatialBound API!")
                
                # List existing projects
                print("\nFetching your projects...")
                projects = client.list_projects()
                
                if projects:
                    print(f"\nFound {len(projects)} existing project(s):")
                    for project in projects[:5]:  # Show first 5
                        print(f"  • {project.get('name')} (ID: {project.get('id')})")
                else:
                    print("No existing projects found.")
            else:
                print("❌ Failed to connect. Please check your API key.")
                return 1
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return 1
    
    # Setup environment variable
    print("\nStep 5: Environment Variable (Recommended)")
    print("-" * 40)
    print("\nFor convenience, you can set the API key as an environment variable:")
    print()
    
    shell = os.environ.get('SHELL', '/bin/bash')
    
    if 'bash' in shell:
        rc_file = Path.home() / '.bashrc'
    elif 'zsh' in shell:
        rc_file = Path.home() / '.zshrc'
    else:
        rc_file = None
    
    if rc_file:
        print(f"Add this line to your {rc_file.name}:")
        print()
        print(f'  export SPATIALBOUND_API_KEY="{api_key}"')
        print()
        
        auto_add = input(f"Automatically add to {rc_file.name}? (y/N): ").strip().lower()
        
        if auto_add in ['y', 'yes']:
            try:
                with open(rc_file, 'a') as f:
                    f.write(f'\n# SpatialBound API Key\n')
                    f.write(f'export SPATIALBOUND_API_KEY="{api_key}"\n')
                
                print(f"✓ Added to {rc_file}")
                print(f"Run: source {rc_file}")
            except Exception as e:
                print(f"❌ Failed to update {rc_file}: {e}")
    else:
        print("Add this to your shell configuration:")
        print(f'  export SPATIALBOUND_API_KEY="{api_key}"')
    
    # Summary
    print("\n" + "="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print()
    print("✓ Configuration saved")
    print("✓ Connection tested successfully")
    print()
    print("Next steps:")
    print("  1. Run analysis: python main.py")
    print("  2. Generate 3D data: python tools/generate_3d_data.py")
    print("  3. View in dashboard: streamlit run web_app.py")
    print()
    print("For help: python tools/generate_3d_data.py --help")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)

