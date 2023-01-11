"""
Interact with openshift cluster with param sent from google chat message
"""
from collections import Counter


class HandlerOcp:
    """
    Handle the command get from google chat message
    """
    def __init__(self):
        pass

    def get_project(self, dyn_client):
        """
        List projects
        """
        v1_projects = dyn_client.resources.get(api_version='project.openshift.io/v1', kind='Project')
        project_list = v1_projects.get()
        projects = []
        for project in project_list.items:
            project = project.metadata.name
            projects.append(project)
        return projects

    def get_app_version(self, dyn_client, app_name, app_env):
        """
        /app_version command 
        """
        dc = dyn_client.resources.get(api_version='apps.openshift.io/v1', kind='DeploymentConfig')
        dc_details = dc.get(name=app_name, namespace=app_env)
        dc_details_appVersion = dc_details.metadata.labels.appVersion
        return dc_details_appVersion


    def get_app_version_all_envs(self, dyn_client, app_name, namespace):
        """
        /app_version  mms-report 
        /app_version  ami-mms-gateway 

        """
        dc = dyn_client.resources.get(api_version='apps.openshift.io/v1', kind='DeploymentConfig')
        app_version_env = self.app_version_util(dc, app_name, namespace)
        return app_version_env


    def app_version_util(self, dc, app_name, namespace):
        dc_details = dc.get(name=app_name, namespace=namespace)
        dc_details_appVersion = dc_details.metadata.labels.appVersion
        app_env = [namespace, dc_details_appVersion]
        return app_env

    def get_env_version(self, dyn_client, env_name):
        """
        /env_version command
        """
        pods = dyn_client.resources.get(api_version='v1', kind='Pod')
        all_pods = pods.get(namespace=env_name, label_selector='deployStrategy=rolling_update')
        app_detail_list = {}
        for pod in all_pods.items:
            app_name = pod.metadata.labels.appName
            app_version = pod.metadata.labels.appVersion[0:4]
            app_detail_list.update({app_name: app_version})
        version_list = list(app_detail_list.values())
        version = Counter(version_list)
        version_most_common = version.most_common(1)[0][0]
        if 'default' in env_name or 'sandbox' in env_name:
            app_name = "centralize-configuration"
        else:
            app_name = "mms-centralize-config"
        centralize_version = self.get_app_version(dyn_client, app_name, env_name)
        return version_most_common, centralize_version

    def get_route(self, dyn_client, app_name, env_name):
        """
        /get_route command
        """
        route = dyn_client.resources.get(api_version="route.openshift.io/v1", kind='Route')
        route_details = route.get(label_selector=f'appName={app_name}', namespace=env_name)
        route_details_url = route_details.items[0]["spec"]["host"]
        return route_details_url

    def restart_app(self, dyn_client, app_name, app_env):
        """
        /restart_app command
        """
        dc = dyn_client.resources.get(api_version='apps.openshift.io/v1', kind='DeploymentConfig')
        output = dc.delete(name=app_name, namespace=app_env)
        return output.status
    
    def app_status(self, dyn_client, app_name, app_env):
        """
        Get app version, running status
        """
        dc = dyn_client.resources.get(api_version='apps.openshift.io/v1', kind='DeploymentConfig')
        dc_details = dc.get(name=app_name, namespace=app_env)
        dc_details_appVersion = dc_details.metadata.labels.appVersion
        dc_details_availableReplicas = dc_details.status.availableReplicas
        dc_details_desired_replica = dc_details.status.replicas
        return (dc_details_appVersion, dc_details_availableReplicas, dc_details_desired_replica)

        