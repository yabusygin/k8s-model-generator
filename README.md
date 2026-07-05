k8s-model-generator
===================

Generate Kubernetes data models from OpenAPI v3.0.

Models generation example:

```sh
curl --remote-name https://raw.githubusercontent.com/kubernetes/kubernetes/v1.36.2/api/openapi-spec/v3/api__v1_openapi.json
curl --remote-name https://raw.githubusercontent.com/kubernetes/kubernetes/v1.36.2/api/openapi-spec/v3/apis__apps__v1_openapi.json
mkdir mymodels
touch mymodels/__init__.py
uv run k8s-model-generator api__v1_openapi.json apis__apps__v1_openapi.json mymodels
```

The generated models usage example:

```python
from pydantic import BaseModel

from mymodels.io.k8s.api.core.v1 import Pod
from mymodels.io.k8s.api.apps.v1 import Deployment

assert issubclass(Pod, BaseModel)
assert issubclass(Deployment, BaseModel)

pod = Pod.model_validate(
    {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "example-pod",
        },
        "spec": {
            "containers": [
                {
                    "name": "example-container",
                    "image": "nginx",
                },
            ],
        },
    }
)
print(pod.kind, pod.metadata.name)
```
