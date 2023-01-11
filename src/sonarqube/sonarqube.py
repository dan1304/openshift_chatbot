import os
import requests
from requests.auth import HTTPBasicAuth
import picologging as logging

SONAR_TOKEN = os.environ.get('SONAR_TOKEN', 'Your_sonarqube_token')
SONAR_BASE_URL = os.environ.get('SONAR_BASE_URL', 'https://scs.security.ascendmoney.io')


def get_project_report(app_name):
    project_key_prefix = "OCP-equator"
    project_key = f"{project_key_prefix}-{app_name}"
    BRANCH_QUALITY_GATE_URL = f"{SONAR_BASE_URL}/api/project_branches/list?project={project_key}"
    HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.request("GET", BRANCH_QUALITY_GATE_URL, headers=HEADERS, data="", verify=False, auth=HTTPBasicAuth(SONAR_TOKEN,""))
    data = response.json()
    result = []
    for i in range(len(data["branches"])):
        if data["branches"][i]["status"] == {}:
            data["branches"][i]["status"] = {'qualityGateStatus': 'Not scan yet'}
        result.append([data["branches"][i].get("name"), data["branches"][i].get("status"),data["branches"][i].get("analysisDate", "N/A")])
    return result


def get_all_app(portfolio_name):
    """
    Get app project list from portfolio name
    """
    PORTFOLIO_URL = f"{SONAR_BASE_URL}/api/measures/component_tree?metricKeys=violations&component={portfolio_name}"
    HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.request("GET", PORTFOLIO_URL, headers=HEADERS, data="", verify=False, auth=HTTPBasicAuth(SONAR_TOKEN,""))
    data = response.json()
    sonar_project_list = []
    for i in range(len(data["components"])):
        logging.debug(data["components"][i]['name'])
        if "demo" not in data["components"][i]['name']:
            sonar_project_list.append(data["components"][i]['name'])
    return sonar_project_list


def get_status_by_branch(project_key):
    # project_key_prefix = "OCP-equator"
    # project_key = f"{project_key_prefix}-{app_name}"
    BRANCH_QUALITY_GATE_URL = f"{SONAR_BASE_URL}/api/project_branches/list?project={project_key}"
    HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.request("GET", BRANCH_QUALITY_GATE_URL, headers=HEADERS, data="", verify=False, auth=HTTPBasicAuth(SONAR_TOKEN,""))
    data = response.json()
    result_master_branch = []
    result_develop_branch = []
    for i in range(len(data["branches"])):
        if data["branches"][i]["status"] == {}:
            data["branches"][i]["status"] = {'qualityGateStatus': 'Not scan yet'}
        if data["branches"][i]["name"] == "master":
            result_master_branch.append([project_key, data["branches"][i].get("name"), data["branches"][i].get("status"),data["branches"][i].get("analysisDate", "N/A")])
        else:
            result_develop_branch.append([project_key, data["branches"][i].get("name"), data["branches"][i].get("status"),data["branches"][i].get("analysisDate", "N/A")])
    return result_master_branch, result_develop_branch


def get_report_by_portfolio(data_master_branch, data_develop_branch):
    not_ok_status_count_master = 0
    not_ok_status_count_develop = 0
    list_not_ok_master = []
    list_not_ok_develop = []

    for i in range(len(data_master_branch)):
        if "OK" not in str(data_master_branch[i][0][2]):
            not_ok_status_count_master = not_ok_status_count_master + 1
            list_not_ok_master.append(data_master_branch[i][0][0])

    for i in range(len(data_develop_branch)):
        if  "OK" not in str(data_develop_branch[i][0][2]):
            not_ok_status_count_develop = not_ok_status_count_develop + 1
            list_not_ok_develop.append(data_develop_branch[i][0][0])
    total_count = len(data_master_branch)
    master_ok_count = total_count - not_ok_status_count_master
    develop_ok_count = total_count - not_ok_status_count_develop
    
    return list_not_ok_master, list_not_ok_develop, total_count, master_ok_count, develop_ok_count, not_ok_status_count_master, not_ok_status_count_develop






