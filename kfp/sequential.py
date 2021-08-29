import kfp
from kfp import dsl


def gcs_download_op():
    return dsl.ContainerOp(
        name='Get Feature Microservice',
        image='bpc999/cat-dog:feature_ms',
    )


def echo_op():
    return dsl.ContainerOp(
        name='Training Microservice',
        image='bpc999/cat-dog:train_ms',
    )


@dsl.pipeline(
    name='cat-dog-pipeline',
    description='A pipeline with two sequential steps of extracting features and training.'
)
def sequential_pipeline():
    """A pipeline with two sequential steps."""

    download_task = gcs_download_op()
    echo_task = echo_op()


if __name__ == '__main__':
    kfp.compiler.Compiler().compile(sequential_pipeline, __file__ + '.yaml')
