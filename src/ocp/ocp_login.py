
"""
Logging OKD/OCP
"""
from kubernetes import client
from openshift.dynamic import DynamicClient
from openshift.helper.userpassauth import OCPLoginConfiguration


def ocp_login(username, password, apihost):
    """
    Login OCP/OKD using creds
    """
    kube_config = OCPLoginConfiguration(ocp_username=username, ocp_password=password)
    kube_config.host = apihost
    kube_config.verify_ssl = False
    # Retrieve the auth token
    kube_config.get_token()

    print(f"OCP cluster: {apihost}" )
    print(f"Auth token: {kube_config.api_key}")
    print(f"Token expires: {kube_config.api_key_expires}")
    k8s_client = client.ApiClient(kube_config)
    dyn_client = DynamicClient(k8s_client)
    return dyn_client
        