import kfp
from kfp import dsl


def feature_op(project, mode, bucket):
    return dsl.ContainerOp(
        name='Get Feature Microservice',
        image='bpc999/cat-dog:feature_ms',
        arguments=[
            '--project', project,
            '--mode', mode,
            '--bucket', bucket
        ],
        file_outputs={'file_output': '/output.txt'}
    )


def training_op(feature_op_container):
    return dsl.ContainerOp(
        name='Training Microservice',
        image='bpc999/cat-dog:train_ms',
        arguments=[
            '--file', feature_op_container.outputs['file_output']
        ]
    )


@dsl.pipeline(
    name='cat-dog-pipeline',
    description='A pipeline with two sequential steps of extracting features and training.'
)
def sequential_pipeline():
    """A pipeline with two sequential steps."""

    download_task = feature_op('cat-dog', 'cloud', 'cat-dog-bucket-2')
    echo_task = training_op(download_task)


if __name__ == '__main__':
    kfp.compiler.Compiler().compile(sequential_pipeline, __file__ + '.yaml')
