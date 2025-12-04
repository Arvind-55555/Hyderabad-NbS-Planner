"""
3D Data Generator Module
Converts 2D geospatial data to 3D formats for 4D visualization
"""

import logging
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import geopandas as gpd
from shapely.geometry import Polygon, Point, MultiPolygon, mapping

logger = logging.getLogger(__name__)


class Data3DGenerator:
    """
    Generator for 3D data from 2D geospatial data
    
    Converts building footprints, NbS interventions, and urban features
    to 3D representations suitable for 4D visualization.
    """
    
    def __init__(self):
        """Initialize 3D data generator"""
        self.vertices = []
        self.vertex_index = {}
        logger.info("3D Data Generator initialized")
    
    def add_vertex(self, x: float, y: float, z: float) -> int:
        """
        Add a vertex to the vertex list and return its index
        
        Args:
            x, y, z: Coordinates
        
        Returns:
            int: Vertex index
        """
        vertex = (x, y, z)
        if vertex not in self.vertex_index:
            self.vertex_index[vertex] = len(self.vertices)
            self.vertices.append([x, y, z])
        return self.vertex_index[vertex]
    
    def create_building_solid(self, footprint_coords: List[Tuple], height: float) -> List:
        """
        Create a 3D solid from a 2D building footprint
        
        Args:
            footprint_coords: List of (x, y) coordinates defining the footprint
            height: Building height in meters
        
        Returns:
            list: Solid boundary definition for CityJSON
        """
        # Ground vertices (z=0)
        ground_vertices = []
        for x, y in footprint_coords[:-1]:  # Exclude last (duplicate) point
            idx = self.add_vertex(x, y, 0)
            ground_vertices.append(idx)
        
        # Roof vertices (z=height)
        roof_vertices = []
        for x, y in footprint_coords[:-1]:
            idx = self.add_vertex(x, y, height)
            roof_vertices.append(idx)
        
        # Create solid boundaries
        # Format: [[[ground], [roof], [wall1], [wall2], ...]]
        boundaries = []
        
        # Ground face (reverse order for correct normal)
        boundaries.append([ground_vertices[::-1]])
        
        # Roof face
        boundaries.append([roof_vertices])
        
        # Wall faces
        n = len(ground_vertices)
        for i in range(n):
            next_i = (i + 1) % n
            wall = [
                ground_vertices[i],
                ground_vertices[next_i],
                roof_vertices[next_i],
                roof_vertices[i]
            ]
            boundaries.append([wall])
        
        return [boundaries]
    
    def create_surface_from_polygon(self, polygon: Polygon, z: float = 0) -> List:
        """
        Create a 3D surface from a 2D polygon
        
        Args:
            polygon: Shapely Polygon
            z: Z-coordinate (height) of the surface
        
        Returns:
            list: Surface boundary definition
        """
        exterior_coords = list(polygon.exterior.coords)
        
        # Add exterior ring vertices
        exterior_indices = []
        for x, y in exterior_coords[:-1]:
            idx = self.add_vertex(x, y, z)
            exterior_indices.append(idx)
        
        # Handle holes (interior rings)
        hole_indices = []
        for interior in polygon.interiors:
            hole_coords = list(interior.coords)
            hole_ring = []
            for x, y in hole_coords[:-1]:
                idx = self.add_vertex(x, y, z)
                hole_ring.append(idx)
            hole_indices.append(hole_ring)
        
        # Return boundary: [exterior, hole1, hole2, ...]
        if hole_indices:
            return [[exterior_indices] + hole_indices]
        else:
            return [[exterior_indices]]
    
    def export_to_cityjson(self, buildings_gdf: gpd.GeoDataFrame, 
                          nbs_gdf: Optional[gpd.GeoDataFrame] = None,
                          state: str = 'BEFORE',
                          output_path: Path = None,
                          project_name: str = "Hyderabad NbS") -> Dict:
        """
        Export data to CityJSON format
        
        Args:
            buildings_gdf: Buildings GeoDataFrame with heights
            nbs_gdf: NbS interventions GeoDataFrame (optional)
            state: 'BEFORE' or 'AFTER'
            output_path: Output file path
            project_name: Project name for metadata
        
        Returns:
            dict: CityJSON data structure
        """
        logger.info(f"Generating CityJSON for {state} state...")
        
        # Reset vertices for this export
        self.vertices = []
        self.vertex_index = {}
        
        # Get bounds for reference point
        bounds = buildings_gdf.total_bounds
        ref_x, ref_y = bounds[0], bounds[1]
        
        # Initialize CityJSON structure
        cityjson = {
            "type": "CityJSON",
            "version": "1.1",
            "metadata": {
                "referenceSystem": "urn:ogc:def:crs:EPSG::4326",
                "geographicalExtent": bounds.tolist(),
                "referencePoint": [ref_x, ref_y, 0],
                "temporalState": state,
                "title": f"{project_name} - {state} State",
                "dataSource": "Hyderabad NbS Planner"
            },
            "CityObjects": {},
            "vertices": []
        }
        
        # Add buildings as 3D solids
        logger.info(f"Processing {len(buildings_gdf)} buildings...")
        for idx, building in buildings_gdf.iterrows():
            building_id = f"building_{idx}"
            
            try:
                # Get building geometry
                geom = building.geometry
                if geom.is_empty or not isinstance(geom, Polygon):
                    continue
                
                # Get building height
                height = building.get('avg_height', 6.0)
                if pd.isna(height) or height <= 0:
                    height = 6.0
                
                # Get footprint coordinates (convert to list)
                coords = list(geom.exterior.coords)
                
                # Create 3D solid
                solid_boundaries = self.create_building_solid(coords, height)
                
                # Add to CityJSON
                cityjson["CityObjects"][building_id] = {
                    "type": "Building",
                    "geometry": [{
                        "type": "Solid",
                        "lod": "1",
                        "boundaries": solid_boundaries
                    }],
                    "attributes": {
                        "measuredHeight": float(height),
                        "roofType": "flat",
                        "function": building.get('building', 'residential'),
                        "temporalState": state
                    }
                }
                
            except Exception as e:
                logger.warning(f"Failed to process building {idx}: {e}")
                continue
        
        # Add NbS interventions (if AFTER state)
        if state == 'AFTER' and nbs_gdf is not None:
            logger.info(f"Processing {len(nbs_gdf)} NbS interventions...")
            
            for idx, nbs in nbs_gdf.iterrows():
                nbs_id = f"nbs_{idx}"
                
                try:
                    # Get NbS geometry
                    geom = nbs.geometry
                    if geom.is_empty:
                        continue
                    
                    nbs_type = nbs.get('Proposed_NbS', 'None')
                    if nbs_type == 'None':
                        continue
                    
                    # Determine height based on NbS type
                    if nbs_type == 'Green Roof':
                        z_height = nbs.get('avg_height', 6.0) + 0.5  # On top of building
                    elif nbs_type == 'Urban Forest':
                        z_height = 8.0  # Average tree height
                    else:
                        z_height = 0.2  # Ground level (permeable pavement, rain gardens)
                    
                    # Create surface
                    if isinstance(geom, Polygon):
                        surface_boundaries = self.create_surface_from_polygon(geom, z_height)
                        
                        # Determine CityObject type
                        if 'Forest' in nbs_type or 'Tree' in nbs_type:
                            city_object_type = "PlantCover"
                        elif 'Wetland' in nbs_type or 'Water' in nbs_type:
                            city_object_type = "WaterBody"
                        else:
                            city_object_type = "LandUse"
                        
                        # Add to CityJSON
                        cityjson["CityObjects"][nbs_id] = {
                            "type": city_object_type,
                            "geometry": [{
                                "type": "MultiSurface",
                                "lod": "1",
                                "boundaries": surface_boundaries
                            }],
                            "attributes": {
                                "nbs_type": nbs_type,
                                "area_sqm": float(geom.area),
                                "cost_inr": float(nbs.get('cost_per_sqm', 0) * geom.area),
                                "temporalState": state
                            }
                        }
                        
                except Exception as e:
                    logger.warning(f"Failed to process NbS {idx}: {e}")
                    continue
        
        # Add vertices to CityJSON
        cityjson["vertices"] = self.vertices
        
        logger.info(f"CityJSON generated: {len(cityjson['CityObjects'])} objects, "
                   f"{len(self.vertices)} vertices")
        
        # Save to file if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(cityjson, f, indent=2)
            
            logger.info(f"✓ CityJSON saved to: {output_path}")
        
        return cityjson
    
    def export_to_geojson_3d(self, gdf: gpd.GeoDataFrame, 
                             height_column: str = 'avg_height',
                             output_path: Path = None) -> Dict:
        """
        Export to GeoJSON with 3D coordinates (height as third dimension)
        
        Args:
            gdf: GeoDataFrame
            height_column: Column name containing height values
            output_path: Output file path
        
        Returns:
            dict: GeoJSON data structure
        """
        logger.info("Generating 3D GeoJSON...")
        
        # Create GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        for idx, row in gdf.iterrows():
            try:
                geom = row.geometry
                if geom.is_empty:
                    continue
                
                # Get height
                height = row.get(height_column, 0)
                if pd.isna(height):
                    height = 0
                
                # Convert geometry to GeoJSON and add Z coordinate
                geom_dict = mapping(geom)
                
                # Add height to coordinates
                if geom_dict['type'] == 'Polygon':
                    coords_3d = []
                    for ring in geom_dict['coordinates']:
                        ring_3d = [[x, y, height] for x, y in ring]
                        coords_3d.append(ring_3d)
                    geom_dict['coordinates'] = coords_3d
                
                # Create feature
                properties = row.drop('geometry').to_dict()
                # Convert numpy types to Python types
                properties = {k: (float(v) if isinstance(v, (np.integer, np.floating)) else v) 
                             for k, v in properties.items()}
                
                feature = {
                    "type": "Feature",
                    "geometry": geom_dict,
                    "properties": properties
                }
                
                geojson["features"].append(feature)
                
            except Exception as e:
                logger.warning(f"Failed to process feature {idx}: {e}")
                continue
        
        logger.info(f"3D GeoJSON generated: {len(geojson['features'])} features")
        
        # Save to file if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            logger.info(f"✓ 3D GeoJSON saved to: {output_path}")
        
        return geojson
    
    def create_tree_3d_object(self, location: Point, height: float = 8.0, 
                             crown_radius: float = 3.0) -> Dict:
        """
        Create a simplified 3D tree object
        
        Args:
            location: Tree location (Point)
            height: Tree height
            crown_radius: Crown radius
        
        Returns:
            dict: 3D tree representation
        """
        x, y = location.x, location.y
        
        # Trunk (cylinder approximation)
        trunk_height = height * 0.3
        trunk_radius = 0.3
        
        # Crown (sphere approximation)
        crown_center_z = trunk_height + (height - trunk_height) / 2
        
        tree_object = {
            "type": "Tree",
            "location": [x, y, 0],
            "trunk": {
                "height": trunk_height,
                "radius": trunk_radius
            },
            "crown": {
                "center": [x, y, crown_center_z],
                "radius": crown_radius,
                "type": "spherical"
            },
            "species": "generic_deciduous"
        }
        
        return tree_object


def generate_3d_data_for_project(buildings_gdf: gpd.GeoDataFrame,
                                 nbs_gdf: gpd.GeoDataFrame,
                                 green_blue_gdf: gpd.GeoDataFrame,
                                 output_dir: Path,
                                 project_name: str = "Hyderabad NbS") -> Dict[str, Path]:
    """
    Generate all 3D data files for a project
    
    Args:
        buildings_gdf: Buildings GeoDataFrame
        nbs_gdf: NbS interventions GeoDataFrame
        green_blue_gdf: Existing green/blue spaces
        output_dir: Output directory
        project_name: Project name
    
    Returns:
        dict: Dictionary of generated file paths
    """
    logger.info("="*70)
    logger.info("GENERATING 3D DATA FOR SPATIALBOUND")
    logger.info("="*70)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator = Data3DGenerator()
    
    generated_files = {}
    
    # 1. BEFORE state (current buildings + existing green spaces)
    logger.info("\n1. Generating BEFORE state...")
    before_cityjson_path = output_dir / f"{project_name.replace(' ', '_')}_BEFORE.json"
    
    # Combine buildings and existing green spaces
    buildings_before = buildings_gdf.copy()
    
    generator.export_to_cityjson(
        buildings_before,
        green_blue_gdf,  # Include existing green spaces
        state='BEFORE',
        output_path=before_cityjson_path,
        project_name=project_name
    )
    
    generated_files['before_cityjson'] = before_cityjson_path
    
    # 2. AFTER state (buildings + NbS interventions)
    logger.info("\n2. Generating AFTER state...")
    after_cityjson_path = output_dir / f"{project_name.replace(' ', '_')}_AFTER.json"
    
    generator.export_to_cityjson(
        buildings_gdf,
        nbs_gdf,  # Include NbS interventions
        state='AFTER',
        output_path=after_cityjson_path,
        project_name=project_name
    )
    
    generated_files['after_cityjson'] = after_cityjson_path
    
    # 3. 3D GeoJSON exports
    logger.info("\n3. Generating 3D GeoJSON files...")
    
    buildings_3d_path = output_dir / f"{project_name.replace(' ', '_')}_buildings_3d.geojson"
    generator.export_to_geojson_3d(buildings_gdf, 'avg_height', buildings_3d_path)
    generated_files['buildings_3d_geojson'] = buildings_3d_path
    
    nbs_3d_path = output_dir / f"{project_name.replace(' ', '_')}_nbs_3d.geojson"
    generator.export_to_geojson_3d(nbs_gdf, 'avg_height', nbs_3d_path)
    generated_files['nbs_3d_geojson'] = nbs_3d_path
    
    logger.info("\n" + "="*70)
    logger.info("3D DATA GENERATION COMPLETE")
    logger.info("="*70)
    logger.info("\nGenerated files:")
    for key, path in generated_files.items():
        logger.info(f"  {key:25s}: {path}")
    
    return generated_files


# Import pandas at module level for type checking
import pandas as pd


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("3D Data Generator module loaded successfully.")

