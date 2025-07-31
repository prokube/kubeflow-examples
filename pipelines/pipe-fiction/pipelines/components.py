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


# works:
# connect with telnet localhost 4444
# @component(base_image="pipe-fiction:latest")
# def greeter_component(names: List = ["Laura", "Malte", "Paul"]):
#     import remote_pdb
#
#     # Remote debugger auf Port 4444
#     remote_pdb.set_trace(host='0.0.0.0', port=4444)
#
#     from pipe_fiction.hello_world import HelloWorld
#     greeter = HelloWorld("Python Entwickler")
#     greetings = greeter.say_hello_multiple(names)
#
#     for i, greeting in enumerate(greetings, 1):
#         print(f"   {i}. {greeting}")
#


@component(base_image="hsteude/kfp-hello-world:latest", packages_to_install=["debugpy"])
def greeter_component(names: List = ["Laura", "Malte", "Paula"]):
    import os

    # Check environment variable for debug mode
    if os.getenv("KFP_DEBUG") == "true":
        import debugpy

        debug_port = int(os.getenv("KFP_DEBUG_PORT", "5678"))
        debugpy.listen(("0.0.0.0", debug_port))
        debugpy.wait_for_client()
        debugpy.breakpoint()

    # Your actual component logic
    from pipe_fiction.hello_world import HelloWorld

    greeter = HelloWorld("Python Developer")
    greetings = greeter.say_hello_multiple(names)
    for i, greeting in enumerate(greetings, 1):
        print(f"   {i}. {greeting}")
    print()


# @component(base_image="pipe-fiction:latest", packages_to_install=['pudb'])
# def greeter_component(names: List = ["Laura", "Malte", "Paul"]):
#     import pudb.remote
#
#     # PuDB Remote-Debugger
#     pudb.remote.set_trace(term_size=(120, 40), host='0.0.0.0', port=6899)
#
#     from pipe_fiction.hello_world import HelloWorld
#     greeter = HelloWorld("Python Entwickler")
#     greetings = greeter.say_hello_multiple(names)
#
#     for i, greeting in enumerate(greetings, 1):
#         print(f"   {i}. {greeting}")
