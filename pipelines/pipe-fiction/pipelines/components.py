from kfp.dsl import Output, Dataset, Input, component
from typing import List, Dict
import debugpy


@component(base_image="hsteude/pipe-fiction:latest", packages_to_install=["debugpy"])
def generate_data_comp(remote_debugging: bool = False) -> List:
    if remote_debugging:
        import debugpy

        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()

    from pipe_fiction.data_generator import DataGenerator

    generator = DataGenerator()
    lines = generator.create_sample_data()
    return lines


@component(
    base_image="hsteude/pipe-fiction:latest",
    packages_to_install=["debugpy"],
)
def process_data_comp(lines: List[str], remote_debugging: bool = False) -> List[str]:
    if remote_debugging:
        import debugpy

        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()

    from pipe_fiction.data_processor import DataProcessor

    processor = DataProcessor()
    processed_lines = processor.process_lines(lines)  # Step into here!

    return processed_lines
