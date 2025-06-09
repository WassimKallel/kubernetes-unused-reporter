from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()


def list_unused_secrets_in_namespace(namespace: str) -> set[str]:
    """
    List unused secrets in a given namespace.
    This function retrieves all secrets in the specified namespace and compares them against the secrets used in pod specifications.
    It returns a set of secrets that are not used in any pod specifications, excluding certain default secrets.

    Arguments:
        namespace {str} -- The namespace in which to search for unused secrets.

    Returns:
        set[str] -- A set of unused secrets in the specified namespace, excluding default secrets.
    """    
    all_used_secrets = set()
    secrets = _list_all_secrets(namespace)
    pod_specs = _get_all_pod_specs(namespace)
    for pod_spec in pod_specs:
        used_secrets = _get_used_secrets_in_pod_spec(pod_spec)
        all_used_secrets.update(used_secrets)
    unused_secrets = secrets - all_used_secrets
    final_unused_secrets = set()
    for secret in unused_secrets:
        if secret.startswith("default-token-") or secret.startswith("kubernetes.io/service-account") or secret.startswith("sh.helm.release.v1"):
            continue
        else:
            final_unused_secrets.add(secret)
    return final_unused_secrets


def list_all_namespaces() -> list[str]:
    """
    List all namespaces in the Kubernetes cluster.
    This function retrieves all namespaces in the cluster and returns their names as a list.
    Arguments:
        None

    Returns:
        list[str] -- A list of all namespace names in the Kubernetes cluster.
    """    
    namespaces_list: client.V1NamespaceList = v1.list_namespace(watch=False)
    return [namespace.metadata.name for namespace in namespaces_list.items]


def _list_all_secrets(namespace: str) -> set[str]:
    """
    List all secrets in a given namespace.
    This function retrieves all secrets in the specified namespace and returns their names as a set.

    Arguments:
        namespace {str} -- The namespace in which to search for secrets.

    Returns:
        set[str] -- A set of all secret names in the specified namespace.
    """    
    secrets_list: client.V1SecretList = v1.list_namespaced_secret(
        namespace=namespace,
        watch=False)
    if not secrets_list.items:
        return set()
    return set([item.metadata.name for item in secrets_list.items])


def _get_all_pod_specs(namespace: str) -> list[client.V1PodSpec]:
    """
    Get all pod specifications in a given namespace.
    This function retrieves all pod specifications from deployments, statefulsets, daemonsets, pods, and replicasets in the specified namespace.
    It returns a list of pod specifications.

    Arguments:
        namespace {str} -- The namespace from which to retrieve pod specifications.

    Returns:
        list[client.V1PodSpec] -- A list of pod specifications from the specified namespace.
    """
    deployments_list: client.V1DeploymentList = apps_v1.list_namespaced_deployment(
        namespace=namespace,
        watch=False)
    statefulsets_list: client.V1StatefulSetList = apps_v1.list_namespaced_deployment(
        namespace=namespace,
        watch=False)
    daemonsets_list: client.V1DaemonSetList = apps_v1.list_namespaced_daemon_set(
        namespace=namespace,
        watch=False)
    pods_list: client.V1PodList = v1.list_namespaced_pod(
        namespace=namespace,
        watch=False)
    replicasets_list: client.V1ReplicaSetList = apps_v1.list_namespaced_replica_set(
        namespace=namespace,
        watch=False)
    pod_specs = []
    for deployment in deployments_list.items + statefulsets_list.items + daemonsets_list.items + replicasets_list.items:
        if deployment.spec.template and deployment.spec.template.spec:
            pod_specs.append(deployment.spec.template.spec)
    for pod in pods_list.items:
        if pod.spec:
            pod_specs.append(pod.spec)
    return pod_specs


def _get_used_secrets_in_pod_spec(pod_template: client.V1PodSpec) -> set[str]:
    """
    Get used secrets in a pod specification.
    This function checks the pod template for volumes and environment variables that reference secrets.
    It returns a set of secret names that are used in the pod specification.

    Arguments:
        pod_template {client.V1PodSpec} -- The pod specification to check for used secrets.

    Returns:
        set[str] -- A set of secret names that are used in the pod specification.
    """    
    used_secrets = set()
    if pod_template.volumes:
        for volume in pod_template.volumes:
            if volume.secret and volume.secret.secret_name:
                used_secrets.add(volume.secret.secret_name)
    containers = pod_template.containers.copy()
    containers.extend(pod_template.init_containers or [])
    for container in containers:
        container_used_secrets = _get_used_secrets_in_container(container)
        used_secrets = used_secrets.union(container_used_secrets)
    return used_secrets


def _get_used_secrets_in_container(container: client.V1Container) -> set[str]:
    """
    Get used secrets in a container.
    This function checks the container for environment variables and volume mounts that reference secrets.
    It returns a set of secret names that are used in the container.

    Arguments:
        container {client.V1Container} -- The container to check for used secrets.

    Returns:
        set[str] -- A set of secret names that are used in the container.
    """
    used_secrets = set()
    if container.env:
        for env in container.env:
            if env.value_from and env.value_from.secret_key_ref:
                used_secrets.add(env.value_from.secret_key_ref.name)
    if container.env_from:
        for env_from in container.env_from:
            if env_from.secret_ref and env_from.secret_ref.name:
                used_secrets.add(env_from.secret_ref.name)
    if container.volume_mounts:
        for volume_mount in container.volume_mounts:
            if volume_mount.name in used_secrets:
                used_secrets.add(volume_mount.name)
    return used_secrets
