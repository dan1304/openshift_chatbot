
"""
main function
"""
import os
from flask import request, json, render_template, jsonify, abort, redirect, url_for
# from flask_login import login_required
 
import picologging as logging
from ocp.ocp import HandlerOcp
from ocp import ocp_login
from sonarqube import sonarqube
from kbs.knowledgebase import KnowledgeBase
from app import app
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

logging.basicConfig()
logger = logging.getLogger()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

OKD_HOST = os.environ.get('OKD_HOST', 'https://api.c-th1n.ascendmoney.io:6443')
OCP_HOST = os.environ.get('OCP_HOST', 'https://api.a-th1n.ascendmoney.io:6443')
USERNAME = os.environ.get('USERNAME', 'tuyen.tranduy')
PASSWORD = os.environ.get('PASSWORD', '')


def renew_session():
  global okd_dyn_client
  global ocp_dyn_client
  okd_dyn_client = ocp_login.ocp_login(USERNAME, PASSWORD, OKD_HOST)
  ocp_dyn_client = ocp_login.ocp_login(USERNAME, PASSWORD, OCP_HOST)


@app.route('/', methods=['GET'])
def home():
  """
  GET - Homepage
  """
  res = "ACT Bot Homepage"
  return json.jsonify({'text': str(res)})


@app.route('/api/v2/data', methods=['GET', 'POST'])
def get_kbs_json_data():
  if request.method == 'GET':
    data = KnowledgeBase.fetch_kbs_json()
    # search filter
    search = request.args.get('search')
    if search:
      search = search.split("?limit=")[0]
      data = KnowledgeBase.filter_kbs(search)
    # pagination
    # start_page = request.args.get('offset', type=int, default=-1)
    # length_offset = request.args.get('limit', type=int, default=-1)
    # pagination = KnowledgeBase.pagination(start_page, length_offset)
    return jsonify(data)  
  
  if request.method == 'POST':
    data = request.get_json()
    if 'id' not in data:
      abort(400)
    update_kb = KnowledgeBase.update_kb(data)
    return data, 200


@app.route('/kbs/', methods=['GET', 'POST'])
# @login_required
def kbs():
  """
  Manage Knowledgebase
  """
  if request.method == 'POST':
    try:
      kb_desc = request.form.get('kb_desc')
      kb_resolution = request.form.get('kb_resolution')
      kb_tag = request.form.get('kb_tag')
      new_kbs = KnowledgeBase.create_new_kbs(kb_desc, kb_resolution, kb_tag)
      # flash("Thank you! Your KB is successfully added" )
      return redirect(url_for('kbs'))   

    except:
      logger.error("Verify if all required data are filled")
      return "Failed to add new kb"

  if request.method == 'GET':
    kbs = KnowledgeBase.fetch_kbs_json()
    return render_template('kbs.html', kbs=kbs)


@app.route('/api/v1/', methods=['POST'])
def on_event():
  """
  POST - Handles an event from Google Chat.   
  """
  event = request.get_json()
  print(event)
  if event['type'] == 'ADDED_TO_SPACE':
    text = 'Thanks for adding me to "%s", to get started: `/help`' % (event['space']['displayName'] if event['space']['displayName'] else 'this chat')
  elif event['type'] == 'MESSAGE':    
    text = ""
    slash_command_id = int(event['message']['annotations'][0]['slashCommand']['commandId'])
    try: 
      match slash_command_id:
        case 1: # help command
            text = """
                    ```
/help                               Show this menu
/app_status {app_name} {env_name}  (ex: /app_status agent equator-default-performance)
/env_version {env_name}            (ex: /env_version equator-default-staging)
/app_version {app_name}            (ex: /app_version agent 
/get_route {app_name} {env_name}   (ex: /get_route ami-operation-portal equator-default-staging)
/restart_app {app_name} {env_name} (ex: /restart_app report equator-default-dev)
/hotfix_env                        (ex: /hotfix_env)
/kbs {kbs_keywords}                (ex: /error Could not resolve placeholder)
/sonarqube {app_name}              (ex: /sonarqube agent)
/sonarqube equator                 (Get Sonarqube report for whole MMS/EQ project)
/faq                               Some useful resources
```
                    """
        case 2: #app_ver mms-report
          input_args = event['message']['argumentText'].split()
          app_name = input_args[0]
          eq_namespace_okd = ["equator-default-dev","equator-default-qa", 
                            "equator-default-release1", "equator-default-release2",
                            "equator-default-release3", "equator-sandbox-dev"]
          eq_namespace_ocp = ["equator-default-performance", "equator-default-staging"]
          mms_namespace_okd = ["equator-mms-dev", "equator-mms-qa"]
          mms_namespace_ocp = ["equator-mms-performance", "equator-mms-staging"]
          app_version_details = []

          if "mms-" in app_name and "ami-" not in app_name: # avoid case like ami-mms-gateway
            for namespace in mms_namespace_okd:
              app_version = HandlerOcp().get_app_version_all_envs(okd_dyn_client, app_name, namespace)
              app_version_details.append(app_version)
            for namespace in mms_namespace_ocp:
              app_version = HandlerOcp().get_app_version_all_envs(ocp_dyn_client, app_name, namespace)
              app_version_details.append(app_version)
          else:
            for namespace in eq_namespace_okd:
              app_version = HandlerOcp().get_app_version_all_envs(okd_dyn_client, app_name, namespace)
              app_version_details.append(app_version)
            for namespace in eq_namespace_ocp:
              app_version = HandlerOcp().get_app_version_all_envs(ocp_dyn_client, app_name, namespace)
              app_version_details.append(app_version)

          text = []
          for app_info in app_version_details:
            app_env = app_info[0]
            app_ver = app_info[1]
            msg = f"{app_name} in {app_env}: *{app_ver}*"
            text.append(msg)
          text = ' \n\n'.join(map(str, text))
        case 3: # get env version
            input_args = event['message']['argumentText'].split()
            if 'staging' in event['message']['argumentText'] or 'performance' in event['message']['argumentText'] :
                env_info = HandlerOcp().get_env_version(ocp_dyn_client, input_args[0])
                most_common_version = env_info[0]
                cen_app_version = env_info[1]
                text = f"Most common version in `{input_args[0]}`: `{most_common_version}` \nCentralize app version: `{cen_app_version}`"
            else:
                env_info = HandlerOcp().get_env_version(okd_dyn_client, input_args[0])
                most_common_version = env_info[0]
                cen_app_version = env_info[1]
                text = f"Most common version in `{input_args[0]}`: `{most_common_version}` \nCentralize app version: `{cen_app_version}`"
        case 4: 
            text = """
KBs: https://truemoney.atlassian.net/wiki/spaces/EQ/pages/102498588/How+to+forward+mock+mountebank+port+from+Openshift+to+local+PC
Wiki: https://truemoney.atlassian.net/wiki/spaces/EQ/
Others: ...
            """
        case 5: # get route
            input_args = event['message']['argumentText'].split()
            if 'staging' in event['message']['argumentText'] or 'performance' in event['message']['argumentText'] :
                route_details_url = HandlerOcp().get_route(ocp_dyn_client, input_args[0], input_args[1])
                route_details_short_url = str(route_details_url).replace("a-th1n", "thn")
                text = f"Short: https://{route_details_short_url}/{input_args[0]}/ \nLong: https://{route_details_url}/{input_args[0]}/ "
            else:
                route_details_url = HandlerOcp().get_route(okd_dyn_client, input_args[0], input_args[1])
                route_details_short_url = str(route_details_url).replace("c-th1n", "thn")
                text = f"Short: https://{route_details_short_url}/{input_args[0]}/ \nLong: https://{route_details_url}/{input_args[0]}/ "
        case 6: # restart app
          input_args = event['message']['argumentText'].split()
          if 'staging' in event['message']['argumentText'] or 'performance' in event['message']['argumentText'] :
            std_output = HandlerOcp().restart_app(ocp_dyn_client, input_args[0], input_args[1])
            text = f"{std_output} - {input_args[0]} in {input_args[1]} is restarting"
          else:
            std_output = HandlerOcp().restart_app(okd_dyn_client, input_args[0], input_args[1])
            text = f"{std_output} - {input_args[0]} in {input_args[1]} is restarting"
        case 7: # app status 
          input_args = event['message']['argumentText'].split()
          if 'staging' in event['message']['argumentText'] or 'performance' in event['message']['argumentText'] :
              app_status = HandlerOcp().app_status(ocp_dyn_client, input_args[0], input_args[1])
              text = f"App Name: {input_args[0]} \nEnv Name: {input_args[1]} \nApp Version: {app_status[0]} \nAvailable Replicas: {app_status[1]} \nDesired Replicas: {app_status[2]} "          
          else:
              app_status = HandlerOcp().app_status(okd_dyn_client, input_args[0], input_args[1])
              text = f"App Name: {input_args[0]} \nEnv Name: {input_args[1]} \nApp Version: {app_status[0]} \nAvailable Replicas: {app_status[1]} \nDesired Replicas: {app_status[2]} "          
        case 8: # get hotfix env version /hotfix_env
            hotfix_envs = ['equator-default-release1', 'equator-default-release2', 'equator-default-release3']
            hotfix_envs_version_list = []
            for hotfix_env in hotfix_envs:
              hotfix_env_info = HandlerOcp().get_env_version(okd_dyn_client, hotfix_env)
              hotfix_envs_version = [hotfix_env, hotfix_env_info[0], hotfix_env_info[1]]
              hotfix_envs_version_list.append(hotfix_envs_version)
            
            text = f"Most common version in `{hotfix_envs_version_list[0][0]}`: `{hotfix_envs_version_list[0][1]}` (`cen app`: `{hotfix_envs_version_list[0][2]}`)\n\
Most common version in `{hotfix_envs_version_list[1][0]}`: `{hotfix_envs_version_list[1][1]}` (`cen app`: `{hotfix_envs_version_list[1][2]}`)\n\
Most common version in `{hotfix_envs_version_list[2][0]}`: `{hotfix_envs_version_list[2][1]}` (`cen app`: `{hotfix_envs_version_list[2][2]}`)\n\
            "      
        case 9: # sonarqube report 
          input_args = event['message']['argumentText'].split()
          app_name = input_args[0]
          if app_name == "equator":
              sonar_app_project = sonarqube.get_all_app("OCP_Equator")
              data_master_branch = []
              data_develop_branch = []
              for app_project in sonar_app_project:
                result_master_branch, result_develop_branch = sonarqube.get_status_by_branch(app_project)
                data_master_branch.append(result_master_branch)
                data_develop_branch.append(result_develop_branch)
          
              list_not_ok_master, list_not_ok_develop, total_count, master_ok_count, develop_ok_count, not_ok_status_count_master, not_ok_status_count_develop = sonarqube.get_report_by_portfolio(data_master_branch, data_develop_branch)
              
              print(list_not_ok_master, list_not_ok_develop, total_count, master_ok_count, develop_ok_count, not_ok_status_count_master, not_ok_status_count_develop)
              text = f"Sonarqube Quality Gate report for EQ and MMS project: \n\
Branch *Master*: \n\
  OK: {master_ok_count}/{total_count} \n\
  Failed: {not_ok_status_count_master}/{total_count}\n\
  Failed list: {list_not_ok_master} \n\
  \n\
Branch *Develop*: \n\
  OK: {develop_ok_count}/{total_count}\n\
  Failed: {not_ok_status_count_develop}/{total_count}\n\
  Failed list: {list_not_ok_develop} \n\
(Develop = Jenkins dev/sandbox pipeline. Master = Jenkins qa/hotfix pipeline)\n\
              "
              print(text)
          else:
            result = sonarqube.get_project_report(app_name)
            logger.info(result)
            # [['master', {'qualityGateStatus': 'OK'}, '2022-10-20T03:35:46+0000'], ['develop', {'qualityGateStatus': 'OK'}, '2022-11-04T06:29:26+0000']]
            text = f"Sonarqube status for *{app_name}*: \n\
  Branch: *{result[0][0]}*. QualityGate status: *{result[0][1]['qualityGateStatus']}*. Last scan: {result[0][2]} \n\
  Branch: *{result[1][0]}*. QualityGate status: *{result[1][1]['qualityGateStatus']}*. Last scan: {result[1][2]} \n\
  (Develop = Jenkins dev/sandbox pipeline. Master = Jenkins qa/hotfix pipeline)\n\
  Details: https://scs.security.ascendmoney.io/dashboard?id=OCP-equator-{app_name}"


        case 15: # reponse proposed resolution to the error
          input_args = event['message']['argumentText']
          most_matched_resolution = KnowledgeBase.get_kbs(input_args)
          text = f" Most matched resolution found (if any): {most_matched_resolution}"
    except KeyError:
        logger.error("[KeyError] annotations not exist")
        text = "Bot failed to process this request, please check the input data"
    except IndexError:
        logger.error("[IndexError] list index out of range")
        text = "Bot failed to process this request, please check the input data"
  else:
    return
  return json.jsonify({'text': str(text)})


@app.route('/api/v1/filter/', methods=['POST'])
def filter():
  input = request.form.get('input')
  result = KnowledgeBase.filter_panda(input)
  return "OK"


if __name__ == '__main__':
  renew_session()
  scheduler.add_job(renew_session, 'interval', minutes=1430)
  scheduler.start()
  app.run(port=8080, debug=True, host='0.0.0.0')
