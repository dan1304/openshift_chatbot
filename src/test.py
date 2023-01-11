from kubernetes import client, config
from openshift.dynamic import DynamicClient


# login
from openshift.helper.userpassauth import OCPLoginConfiguration
 
apihost = 'https://api.c-th1n.ascendmoney.io:6443'
username = 'tuyen.tranduy'
password = 'H0djna_m3nuwnksd8'
 
kubeConfig = OCPLoginConfiguration(ocp_username=username, ocp_password=password)
kubeConfig.host = apihost
kubeConfig.verify_ssl = False
# kubeConfig.ssl_ca_cert = './ocp.pem' # use a certificate bundle for the TLS validation
# Retrieve the auth token
kubeConfig.get_token()
 
print(f"OCP cluster: {apihost}" )
print('Auth token: {0}'.format(kubeConfig.api_key))
print('Token expires: {0}'.format(kubeConfig.api_key_expires))
 
k8s_client = client.ApiClient(kubeConfig)
dyn_client = DynamicClient(k8s_client)



v1_projects = dyn_client.resources.get(api_version='project.openshift.io/v1', kind='Project')

project_list = v1_projects.get()

for project in project_list.items:
    print(project.metadata.name)

# v1_services = dyn_client.resources.get(api_version='v1', kind='Service')
# # v1_dc = dyn_client.resources.get(api_version='apps.openshift.io/v1', kind='DeploymentConfig')
# for services in v1_services.items:
#     print(services.metadata.name)


# Gets the specific Service named 'example' from the 'test' namespace
# v1_services = dyn_client.resources.get(api_version='v1', kind='Service')
# svc = v1_services.get(name='agent', namespace='equator-sandbox-dev')
# print(svc)

# dc = v1_dc.get(name='merchant', namespace='equator-sandbox-dev')
# print(dc)
# print(dc.items().labels)
# print(type(dc))



# # v1_projects = dyn_client.resources.get(api_version='v1', kind='Pod', namespace='equator-sandbox-dev')
# v1_services = dyn_client.resources.get(api_version='project.openshift.io/v1', kind='Service', namespace='equator-sandbox-dev')


# services_list = v1_services.get()

# for services in services_list.items:
#     print(services.metadata.name)

def restart_app(app_name, app_env):
    """
    /restart_app command
    """
    pod = dyn_client.resources.get(api_version='v1', kind='Pod')
    print("_________________________")
    pod_details = pod.get(label_selector=f'appName={app_name}', namespace=app_env)
    print(pod_details)
    # dc_details_appVersion = dc_details.metadata.labels.appVersion
    output = pod.delete(label_selector=f'appName={app_name}', namespace=app_env)
    import ipdb; ipdb.set_trace()
    print(output.status)

def check_pod_status(app_name, app_env):
    # /check_pod_status: return pod status, version
    dc = dyn_client.resources.get(api_version='apps.openshift.io/v1', kind='DeploymentConfig')
    dc_details = dc.get(name=app_name, namespace=app_env)
    dc_details_appVersion = dc_details.metadata.labels.appVersion
    dc_details_availableReplicas = dc_details.status.availableReplicas
    dc_details_desired_replica = dc_details.status.replicas
    # dc_details_running_status = dc_details.status.conditions[0]['status']
    # import ipdb; ipdb.set_trace()
    print(dc_details_appVersion, dc_details_availableReplicas, dc_details_desired_replica)

    
    # dc_details_appVersion = dc_details.metadata.labels.appVersion
    # output = dc.delete(name=app_name, namespace=app_env)
    # import ipdb; ipdb.set_trace()
    # print(output.status)


def get_app_version_all_envs(app_name):
    """
    /app_version  mms-report 
    /app_version  ami-mms-gateway 

    """
    dc = dyn_client.resources.get(api_version='apps.openshift.io/v1', kind='DeploymentConfig')
    eq_namespace_okd = ["equator-default-dev","equator-default-qa", 
                        "equator-default-release1", "equator-default-release2",
                        "equator-default-release3", "equator-sandbox-dev"]
    eq_namespace_ocp = ["equator-default-performance", "equator-default-staging"]
    mms_namespace_okd = ["equator-mms-dev", "equator-mms-qa"]
    mms_namespace_ocp = ["equator-mms-qa", "equator-mms-qa"] # test

    app_version_details = []
    if "mms-" in app_name and "ami-" not in app_name:
        for namespace in mms_namespace_okd:
            app_env = app_version_util(dc, app_name, namespace)
            app_version_details.append(app_env)
        for namespace in mms_namespace_ocp:
            app_env = app_version_util(dc, app_name, namespace)
            app_version_details.append(app_env)
    else:
        for namespace in eq_namespace_okd:
            dc_details = dc.get(name=app_name, namespace=namespace)
            dc_details_appVersion = dc_details.metadata.labels.appVersion
            app_env = [namespace, dc_details_appVersion]
            app_version_details.append(app_env)

    return app_version_details

def get_app_version_all_envs_test(app_name, namespace):
    """
    /app_version  mms-report 
    /app_version  ami-mms-gateway 

    """
    dc = dyn_client.resources.get(api_version='apps.openshift.io/v1', kind='DeploymentConfig')
    app_version_env = app_version_util(dc, app_name, namespace)
    return app_version_env

def app_version_util(dc, app_name, namespace):
    dc_details = dc.get(name=app_name, namespace=namespace)
    dc_details_appVersion = dc_details.metadata.labels.appVersion
    app_env = [namespace, dc_details_appVersion]
    return app_env

result = get_app_version_all_envs_test("mms-report", "equator-mms-dev")
print(result)
# [['equator-mms-dev', '1.5.1-18'], ['equator-mms-qa', '1.6.0-22']]
# [['equator-mms-dev', '1.5.1-18'], ['equator-mms-qa', '1.6.0-22'], ['equator-mms-qa', '1.6.0-22'], ['equator-mms-qa', '1.6.0-22']]



# restart_app("report", "equator-sandbox-dev")
# check_pod_status("report", "equator-sandbox-dev")


