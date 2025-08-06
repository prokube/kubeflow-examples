from typing import List, Dict

from utils.debuggable_component import (
    lightweight_debuggable_component,
)


@lightweight_debuggable_component(base_image="hsteude/pipe-fiction:latest")
def generate_data_comp(debug: bool = False) -> List:
    from pipe_fiction.data_generator import DataGenerator

    generator = DataGenerator()
    lines = generator.create_sample_data()
    return lines


@lightweight_debuggable_component(
    base_image="hsteude/pipe-fiction:latest",
)
def process_data_comp(lines: List[str], debug: bool = False) -> List[str]:
    from pipe_fiction.data_processor import DataProcessor

    processor = DataProcessor()
    processed_lines = processor.process_lines(lines)  # Step into here!

    return processed_lines
