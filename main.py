from src import k8s
from termcolor import colored


def main():
    """
    Main function to list unused Kubernetes secrets in all namespaces.
    """
    namespaces = k8s.list_all_namespaces()
    for namespace in namespaces:
        secrets = k8s.list_unused_secrets_in_namespace(namespace)
        print("+ Namespace :", colored(namespace, "green"))
        if not secrets:
            print(colored("  - No unused secrets found", "yellow"))
            continue
        for secret in secrets:
            print(colored(f"  - {secret}", "red"))


if __name__ == "__main__":
    main()
