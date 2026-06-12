"""
Tests for FMG Map Renderer

Validates SVG output generation from map data
"""

import pytest
pytest.importorskip("numpy")
import tempfile
import shutil
from pathlib import Path

from oracle_town.skills.map_generator_skill import MapGeneratorSkill
from oracle_town.skills.map_renderer_fmg import MapRendererFMG, render_conquest_map


class TestMapRendererBasics:
    """Test basic SVG rendering functionality"""

    def test_renderer_initialization(self):
        """Renderer should initialize with configurable tile size"""
        renderer = MapRendererFMG(tile_size=60, padding=40)

        assert renderer.tile_size == 60
        assert renderer.padding == 40

    def test_svg_generation_from_map_data(self, temp_skill):
        """Renderer should generate valid SVG from map data"""
        # Generate map
        result = temp_skill.generate_map(seed=111, game_id="test_render")
        assert result["status"] == "success"

        map_data = result["map_data"]

        # Create renderer
        renderer = MapRendererFMG()

        # Generate SVG
        svg_content = renderer.generate_svg(map_data)

        # Verify SVG structure
        assert svg_content.startswith('<svg')
        assert svg_content.endswith('</svg>')
        assert '<defs>' in svg_content
        assert '<title>' not in svg_content or 'CONQUEST MAP' in svg_content

    def test_svg_contains_tiles(self, temp_skill):
        """SVG should contain rect elements for each tile"""
        result = temp_skill.generate_map(seed=111, game_id="test_tiles")
        map_data = result["map_data"]

        renderer = MapRendererFMG()
        svg_content = renderer.generate_svg(map_data)

        # Should have 25 rectangles (one per tile)
        rect_count = svg_content.count('<rect')
        assert rect_count >= 25, f"Expected at least 25 rect elements, got {rect_count}"

    def test_svg_contains_territory_boundaries(self, temp_skill):
        """SVG should include territory boundary lines"""
        result = temp_skill.generate_map(seed=111, game_id="test_boundaries")
        map_data = result["map_data"]

        renderer = MapRendererFMG()
        svg_content = renderer.generate_svg(map_data)

        # Should have line elements for boundaries
        assert '<line' in svg_content, "SVG should contain line elements for boundaries"

    def test_svg_contains_climate_overlays(self, temp_skill):
        """SVG should include climate zone overlays"""
        result = temp_skill.generate_map(seed=111, game_id="test_climate")
        map_data = result["map_data"]

        renderer = MapRendererFMG()
        svg_content = renderer.generate_svg(map_data)

        # Should have circle elements for climate overlays
        assert '<circle' in svg_content, "SVG should contain circle elements for climate"

    def test_svg_contains_legend(self, temp_skill):
        """SVG should include legend with terrain types"""
        result = temp_skill.generate_map(seed=111, game_id="test_legend")
        map_data = result["map_data"]

        renderer = MapRendererFMG()
        svg_content = renderer.generate_svg(map_data)

        # Should contain legend
        assert 'Legend' in svg_content or 'legend' in svg_content.lower()
        assert 'plains' in svg_content.lower()
        assert 'water' in svg_content.lower()

    def test_svg_contains_terrain_colors(self, temp_skill):
        """SVG should use appropriate colors for terrain types"""
        result = temp_skill.generate_map(seed=111, game_id="test_colors")
        map_data = result["map_data"]

        renderer = MapRendererFMG()
        svg_content = renderer.generate_svg(map_data)

        # Should contain colors from palette
        assert '#1e90ff' in svg_content  # water (dodger blue)
        assert '#90ee90' in svg_content  # plains (light green)


class TestMapRendererOutput:
    """Test file output functionality"""

    def test_render_to_file(self, temp_skill):
        """Renderer should write SVG to file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate map
            result = temp_skill.generate_map(seed=111, game_id="test_file")
            map_data = result["map_data"]

            # Render to file
            renderer = MapRendererFMG()
            output_path = f"{temp_dir}/test_map.svg"
            saved_path = renderer.render_to_svg(map_data, output_path)

            # Verify file exists
            assert Path(saved_path).exists()

            # Verify file contains SVG
            with open(saved_path, "r") as f:
                content = f.read()

            assert content.startswith('<svg')
            assert '</svg>' in content

    def test_render_function_convenience(self, temp_skill):
        """Convenience function should render map"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate map
            result = temp_skill.generate_map(seed=111, game_id="conquest_001")
            map_data = result["map_data"]
            map_data["game_id"] = "conquest_001"  # Add game_id for filename

            # Use convenience function
            output_path = render_conquest_map(map_data, temp_dir)

            # Verify file exists
            assert Path(output_path).exists()

            # Verify filename contains seed and game_id
            assert "seed_111" in output_path
            assert "conquest_001" in output_path

    def test_output_directory_creation(self, temp_skill):
        """Renderer should create output directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested path that doesn't exist
            nested_dir = f"{temp_dir}/nested/deep/dir"

            result = temp_skill.generate_map(seed=111, game_id="test_nested")
            map_data = result["map_data"]

            # Render to nested path
            renderer = MapRendererFMG()
            output_path = f"{nested_dir}/map.svg"
            saved_path = renderer.render_to_svg(map_data, output_path)

            # Verify directory was created and file exists
            assert Path(saved_path).parent.exists()
            assert Path(saved_path).exists()


class TestMapRendererDeterminism:
    """Test that rendering is deterministic"""

    def test_same_map_produces_identical_svg(self, temp_skill):
        """Same map data should produce identical SVG"""
        # Generate same map twice
        result1 = temp_skill.generate_map(seed=111, game_id="render_test_1")
        result2 = temp_skill.generate_map(seed=111, game_id="render_test_2")

        map_data1 = result1["map_data"]
        map_data2 = result2["map_data"]

        # Render both
        renderer = MapRendererFMG()
        svg1 = renderer.generate_svg(map_data1)
        svg2 = renderer.generate_svg(map_data2)

        # Remove timestamp-dependent parts for comparison
        svg1_normalized = svg1.replace(map_data1['timestamp'], 'TIMESTAMP')
        svg2_normalized = svg2.replace(map_data2['timestamp'], 'TIMESTAMP')

        # Should be identical except for timestamps
        assert svg1_normalized == svg2_normalized


class TestMapRendererIntegration:
    """Integration tests with MapGeneratorSkill"""

    def test_full_pipeline_skill_to_svg(self, temp_skill):
        """Full pipeline: skill → map data → SVG file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Generate map with skill
            result = temp_skill.generate_map(seed=222, game_id="integration_test")
            assert result["status"] == "success"

            map_data = result["map_data"]

            # Step 2: Render to SVG
            renderer = MapRendererFMG(tile_size=60)
            output_file = f"{temp_dir}/integration_map.svg"
            saved_path = renderer.render_to_svg(map_data, output_file)

            # Step 3: Verify output
            assert Path(saved_path).exists()

            with open(saved_path, "r") as f:
                svg_content = f.read()

            # Verify SVG contains key elements
            assert '<svg' in svg_content
            assert '<rect' in svg_content  # Tiles
            assert '<circle' in svg_content  # Climate
            assert '<line' in svg_content  # Boundaries
            assert 'Legend' in svg_content or 'legend' in svg_content.lower()

    def test_multiple_maps_to_svg(self, temp_skill):
        """Should be able to render multiple maps"""
        with tempfile.TemporaryDirectory() as temp_dir:
            renderer = MapRendererFMG()

            for seed in [111, 222, 333]:
                # Generate map
                result = temp_skill.generate_map(seed=seed, game_id=f"map_{seed}")
                assert result["status"] == "success"

                # Render to SVG
                output_file = f"{temp_dir}/map_{seed}.svg"
                saved_path = renderer.render_to_svg(result["map_data"], output_file)

                # Verify each file exists
                assert Path(saved_path).exists()

                # Verify file has content
                with open(saved_path, "r") as f:
                    content = f.read()

                assert len(content) > 100  # Non-trivial SVG


class TestMapRendererVisualization:
    """Test visualization aspects"""

    def test_color_palette(self):
        """Renderer should have defined color palette"""
        renderer = MapRendererFMG()

        # Check terrain colors
        assert "water" in renderer.TERRAIN_COLORS
        assert "plains" in renderer.TERRAIN_COLORS
        assert "forest" in renderer.TERRAIN_COLORS
        assert "mountain" in renderer.TERRAIN_COLORS

        # Check climate overlays
        assert "temperate" in renderer.CLIMATE_OVERLAYS
        assert "tropical" in renderer.CLIMATE_OVERLAYS
        assert "arid" in renderer.CLIMATE_OVERLAYS
        assert "frozen" in renderer.CLIMATE_OVERLAYS

    def test_custom_tile_size(self, temp_skill):
        """Renderer should respect custom tile sizes"""
        result = temp_skill.generate_map(seed=111, game_id="tile_size_test")
        map_data = result["map_data"]

        # Render with different tile sizes
        for tile_size in [30, 60, 100]:
            renderer = MapRendererFMG(tile_size=tile_size)
            svg_content = renderer.generate_svg(map_data)

            # Verify SVG contains expected dimensions
            assert '<svg' in svg_content
            # SVG should scale based on tile size
            assert '5' in svg_content  # Grid is 5x5


# Fixtures

@pytest.fixture
def temp_skill():
    """Create temporary skill for rendering tests"""
    temp_dir = tempfile.mkdtemp()
    cache_dir = Path(temp_dir) / "map_cache"
    ledger_path = Path(temp_dir) / "ledger.jsonl"

    skill = MapGeneratorSkill(
        cache_dir=str(cache_dir),
        ledger_path=str(ledger_path)
    )

    yield skill

    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
