import kfp
from kfp import dsl


def feature_op(project, mode, bucket, handle):
    return dsl.ContainerOp(
        name='Get Feature Microservice',
        image='bpc999/cat-dog:feature_microservice',
        arguments=[
            '--project', project,
            '--mode', mode,
            '--bucket', bucket,
            '--handle', handle
        ],
        file_outputs={'file_output': '/output.txt'}
    )


def training_op(feature_op_container):
    return dsl.ContainerOp(
        name='Training Microservice',
        image='bpc999/cat-dog:train_microservice',
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

    feature_task = feature_op('cat-dog', 'cloud', 'cat-dog-bucket-2', '104.198.180.139')
    training_task = training_op(feature_task)


if __name__ == '__main__':
    kfp.compiler.Compiler().compile(sequential_pipeline, __file__ + '.yaml')
