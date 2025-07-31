from kfp.dsl import pipeline
from components import generate_data_comp, process_data_comp


@pipeline
def example_pipeline():
    data_gen_task = generate_data_comp(remote_debugging=True)
    process_data_task = process_data_comp(lines=data_gen_task.output, remote_debugging=False)
