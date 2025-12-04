"""
SpatialBound 4D Visualization Integration Module
Handles interaction with SpatialBound API for 4D visualization
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import requests
import json

logger = logging.getLogger(__name__)


class SpatialBoundClient:
    """
    Client for SpatialBound 4D visualization API
    
    This client handles authentication, data upload, and 4D visualization
    generation using the SpatialBound platform.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.spatialbound.com/v1"):
        """
        Initialize SpatialBound client
        
        Args:
            api_key: SpatialBound API key (defaults to SPATIALBOUND_API_KEY env var)
            base_url: Base URL for SpatialBound API
        """
        self.api_key = api_key or os.getenv("SPATIALBOUND_API_KEY")
        self.base_url = base_url
        
        if not self.api_key:
            logger.warning("No SpatialBound API key provided. Set SPATIALBOUND_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        logger.info(f"SpatialBound client initialized with base URL: {base_url}")
    
    def test_connection(self) -> bool:
        """
        Test connection to SpatialBound API
        
        Returns:
            bool: True if connection successful
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                logger.info("✓ Successfully connected to SpatialBound API")
                return True
            else:
                logger.error(f"✗ Connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Connection error: {e}")
            return False
    
    def create_project(self, project_name: str, location: Tuple[float, float], 
                      description: str = None) -> Optional[str]:
        """
        Create a new 4D visualization project
        
        Args:
            project_name: Name of the project
            location: (latitude, longitude) tuple
            description: Optional project description
        
        Returns:
            str: Project ID if successful, None otherwise
        """
        payload = {
            "name": project_name,
            "location": {
                "latitude": location[0],
                "longitude": location[1]
            },
            "description": description or f"NbS Planning for {project_name}",
            "type": "urban_planning",
            "visualization_type": "4d_temporal"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/projects", json=payload)
            
            if response.status_code == 201:
                project_data = response.json()
                project_id = project_data.get('id')
                logger.info(f"✓ Project created successfully: {project_id}")
                return project_id
            else:
                logger.error(f"✗ Failed to create project: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Error creating project: {e}")
            return None
    
    def upload_3d_data(self, project_id: str, data_file: Path, 
                       data_type: str = "cityjson", timestamp: str = "BEFORE") -> bool:
        """
        Upload 3D data to a project
        
        Args:
            project_id: Project ID
            data_file: Path to 3D data file (CityJSON, 3D Tiles, etc.)
            data_type: Type of data file ('cityjson', '3dtiles', 'geojson3d')
            timestamp: Temporal state ('BEFORE' or 'AFTER')
        
        Returns:
            bool: True if successful
        """
        if not data_file.exists():
            logger.error(f"✗ Data file not found: {data_file}")
            return False
        
        # Read file content
        with open(data_file, 'r') as f:
            data_content = json.load(f)
        
        payload = {
            "project_id": project_id,
            "data_type": data_type,
            "timestamp": timestamp,
            "data": data_content
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects/{project_id}/data",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✓ Successfully uploaded {data_type} data for {timestamp} state")
                return True
            else:
                logger.error(f"✗ Failed to upload data: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error uploading data: {e}")
            return False
    
    def upload_buildings_before(self, project_id: str, buildings_file: Path) -> bool:
        """
        Upload BEFORE state (current buildings and infrastructure)
        
        Args:
            project_id: Project ID
            buildings_file: Path to buildings CityJSON file
        
        Returns:
            bool: True if successful
        """
        logger.info("Uploading BEFORE state (current infrastructure)...")
        return self.upload_3d_data(project_id, buildings_file, "cityjson", "BEFORE")
    
    def upload_nbs_after(self, project_id: str, nbs_file: Path) -> bool:
        """
        Upload AFTER state (with NbS interventions)
        
        Args:
            project_id: Project ID
            nbs_file: Path to NbS interventions CityJSON file
        
        Returns:
            bool: True if successful
        """
        logger.info("Uploading AFTER state (with NbS interventions)...")
        return self.upload_3d_data(project_id, nbs_file, "cityjson", "AFTER")
    
    def generate_4d_visualization(self, project_id: str, 
                                  config: Optional[Dict] = None) -> Optional[str]:
        """
        Generate 4D visualization for a project
        
        Args:
            project_id: Project ID
            config: Optional visualization configuration
        
        Returns:
            str: Visualization URL if successful
        """
        default_config = {
            "transition_duration": 2.0,  # seconds
            "camera_angle": "bird_eye",
            "lighting": "natural",
            "show_labels": True,
            "color_scheme": "nbs_standard",
            "quality": "high"
        }
        
        visualization_config = {**default_config, **(config or {})}
        
        payload = {
            "project_id": project_id,
            "config": visualization_config
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/projects/{project_id}/visualize",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                viz_url = result.get('viewer_url')
                logger.info(f"✓ 4D visualization generated: {viz_url}")
                return viz_url
            else:
                logger.error(f"✗ Failed to generate visualization: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Error generating visualization: {e}")
            return None
    
    def get_project_info(self, project_id: str) -> Optional[Dict]:
        """
        Get project information
        
        Args:
            project_id: Project ID
        
        Returns:
            dict: Project information
        """
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"✗ Failed to get project info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Error getting project info: {e}")
            return None
    
    def get_embed_code(self, project_id: str, width: int = 1200, height: int = 800) -> str:
        """
        Get embeddable HTML code for 4D viewer
        
        Args:
            project_id: Project ID
            width: Viewer width in pixels
            height: Viewer height in pixels
        
        Returns:
            str: HTML embed code
        """
        viewer_url = f"https://viewer.spatialbound.com/embed/{project_id}"
        
        embed_code = f'''
        <iframe 
            src="{viewer_url}" 
            width="{width}" 
            height="{height}" 
            frameborder="0" 
            allowfullscreen
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
        </iframe>
        '''
        
        return embed_code.strip()
    
    def list_projects(self) -> Optional[list]:
        """
        List all projects for the authenticated user
        
        Returns:
            list: List of projects
        """
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                logger.info(f"Found {len(projects)} projects")
                return projects
            else:
                logger.error(f"✗ Failed to list projects: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Error listing projects: {e}")
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project
        
        Args:
            project_id: Project ID
        
        Returns:
            bool: True if successful
        """
        try:
            response = self.session.delete(f"{self.base_url}/projects/{project_id}")
            
            if response.status_code == 204:
                logger.info(f"✓ Project deleted: {project_id}")
                return True
            else:
                logger.error(f"✗ Failed to delete project: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error deleting project: {e}")
            return False


def create_spatialbound_config(api_key: str, output_path: Path = None) -> Path:
    """
    Create SpatialBound configuration file
    
    Args:
        api_key: SpatialBound API key
        output_path: Path to save config file (defaults to .spatialbound_config)
    
    Returns:
        Path: Path to created config file
    """
    if output_path is None:
        output_path = Path.home() / '.spatialbound_config'
    
    config = {
        "api_key": api_key,
        "base_url": "https://api.spatialbound.com/v1",
        "viewer_url": "https://viewer.spatialbound.com"
    }
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set restrictive permissions
    os.chmod(output_path, 0o600)
    
    logger.info(f"✓ SpatialBound config saved to: {output_path}")
    return output_path


def load_spatialbound_config(config_path: Path = None) -> Optional[Dict]:
    """
    Load SpatialBound configuration
    
    Args:
        config_path: Path to config file
    
    Returns:
        dict: Configuration dictionary
    """
    if config_path is None:
        config_path = Path.home() / '.spatialbound_config'
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return None
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    logger.info(f"✓ Loaded SpatialBound config from: {config_path}")
    return config


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Test connection
    client = SpatialBoundClient()
    
    if client.api_key:
        print("\n=== Testing SpatialBound Connection ===")
        client.test_connection()
        
        print("\n=== Listing Projects ===")
        projects = client.list_projects()
        if projects:
            for project in projects:
                print(f"  - {project.get('name')} ({project.get('id')})")
    else:
        print("\n⚠️  No API key configured.")
        print("Set the SPATIALBOUND_API_KEY environment variable:")
        print("  export SPATIALBOUND_API_KEY='your-api-key-here'")

