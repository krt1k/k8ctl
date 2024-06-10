import click
import subprocess
import os
from . import helper
# import logging

rancher_url = os.getenv("RANCHER_URL")
rancher_token = os.getenv("RANCHER_TOKEN")

# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
# log.addHandler(logging.StreamHandler())

## Program starts here

@click.group()
def k8ctl():
    '''
    k8ctl is a command line tool for managing rancher multicluster kubernetes environments
    '''
    pass

@k8ctl.group()
def cluster():
    '''
    Switch, list and get the current cluster
    '''
    pass

@k8ctl.group()
def env():
    '''
    Create, list and delete environment variables of a application
    '''
    pass

@k8ctl.group()
def list():
    '''
    List applications, web, timers, workers
    '''
    pass

@k8ctl.group()
def console():
    '''
    Connect to the application with railsconsole, psql, bash
    '''
    pass

@k8ctl.group()
def restart():
    '''
    Restart the applications, web, timers, workers
    '''
    pass

## Main group
@k8ctl.command()
@click.option('--token', '-t', help='The Rancher bearer token to login to the cluster', required=True, default=rancher_token)
@click.option('--url', '-u', help='The Rancher URL', default=rancher_url, required=True)
@click.option('--cluster', '-c', help='The cluster name to login to')
def login(token, cluster, url):
    '''
    Login to a cluster
    '''
    if cluster is None:
        result = subprocess.run(f"rancher login {url} --token {token} --skip-verify", shell=True, check=True, stderr=subprocess.PIPE)
    else:
        result = subprocess.run(f"rancher login {url} -c {cluster} --token {token} --skip-verify", shell=True, check=True, stderr=subprocess.PIPE)

    if result.returncode == 0:
        click.echo("Successfully logged in to the rancher")

@k8ctl.command(name='logs')
@click.option('--app', '-a', help='The application name to get the logs', required=False)
@click.option('--pod', '-p', help='The pod name to get the logs', required=False)
@click.option('--follow', '-f', is_flag=True, help='Follow the logs')
def get_logs(app, pod, follow):
    '''
    Get the logs of the application
    '''
    if pod is None:
        if follow:
            result = subprocess.run(f"kubectl logs -l app={app} -f --max-log-requests 20", shell=True, check=True, stderr=subprocess.DEVNULL)
        else:
            result = subprocess.run(f"kubectl logs -l app={app} --max-log-requests 20", shell=True, check=True, stderr=subprocess.DEVNULL)
    else:
        if follow:
            result = subprocess.run(f"kubectl logs {pod} -f --max-log-requests 20", shell=True, check=True, stderr=subprocess.DEVNULL)
        else:
            result = subprocess.run(f"kubectl logs {pod} --max-log-requests 20", shell=True, check=True, stderr=subprocess.DEVNULL)

    if result.stdout is None:
        click.echo("Type -h or --help for more details.\nPlease specify a app or pod name")
        return

## Cluster group
@cluster.command(name='current')
def current_cluster():
    '''
    Show the current cluster
    '''
    result = subprocess.run("kubectl config current-context", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    click.echo(result.stdout.decode('utf-8').strip())


@cluster.command(name='list')
def list_clusters():
    '''
    List all clusters
    '''
    result = subprocess.run("rancher clusters", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    click.echo(result.stdout.decode('utf-8'))

@cluster.command(name='switch')
@click.option('--cluster', '-c', required=True, prompt=True, help='The cluster name to switch to')
def switch_cluster(cluster):
    '''
    Switch to a cluster
    '''
    # if cluster == "aura":
    #     cluster = "dev"

    ## file present but expired token

    result = subprocess.run(f"ls ~/.kube/{cluster}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    dummy = None
    # current_cluster = subprocess.run(f'''cat ~/.kube/config | grep -iw "{cluster}"''', shell=True, stdout=dummy, stderr=subprocess.PIPE)
    current_cluster = subprocess.run(f'''kubectl config current-context''', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # current cluster output to a variable
    dummy = current_cluster.stdout.decode('utf-8').strip()
    
    if dummy is None:
        click.echo(f"No")
        return 1
    elif dummy == cluster:
        current_cluster.returncode = 0
    else:
        current_cluster.returncode = 1

    if current_cluster.returncode == 0 and helper.check_token_validlity() == 0:
        click.echo(f"Already logged into {cluster}")
        return 0
    
    elif result.returncode != 0:
        click.echo(f"Cluster {cluster} config not found")

        subprocess.run(f"touch ~/.kube/{cluster}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with open(os.path.expanduser(f"~/.kube/{cluster}"), "w") as f:
            config_write = subprocess.run(f"rancher cluster kf {cluster}", shell=True, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if config_write.returncode != 0:
            click.echo("Failed to switch to the cluster")
            return 1
        else:
            click.echo(f"{cluster} config is stored in ~/.kube/")
            
    copy_config = subprocess.run(f"cp ~/.kube/{cluster} ~/.kube/config", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if helper.check_token_validlity() != 0:
        click.echo("Token has expired. So, logging in again")

        subprocess.run(f"> ~/.kube/{cluster}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with open(os.path.expanduser(f"~/.kube/{cluster}"), "w") as f:
            config_write = subprocess.run(f"rancher cluster kf {cluster}", shell=True, stdout=f, stderr=subprocess.PIPE, text=True)
        
        copy_config = subprocess.run(f"cp ~/.kube/{cluster} ~/.kube/config", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if config_write.returncode != 0:
            click.echo(f"Failed to refresh config to the {cluster}")
            return 1
        else:
            click.echo(f"{cluster} config refreshed in ~/.kube/")

    if copy_config.returncode != 0:
        click.echo("Failed to copy cluster config!")
        return 1
    
    # if cluster == "dev":
    #     subprocess.run("kubectl config set-context --current --namespace=protons", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    # else:
    #     subprocess.run("kubectl config set-context --current --namespace=default", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    subprocess.run("kubectl config set-context --current --namespace=default", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    click.echo(f"Switched to {cluster}")

## Env group
@env.command(name='list')
# @click.option('--vim ', '-v', is_flag=True, help='Edit the environment variables in vim')
@click.option('--app', '-a', prompt=True, help='The application name to list the environment variables', required=True)
def list_env(app):
    '''
    List all environment variables
    '''
    cmd = """kubectl get secret {}""".format(app) + ''' -o jsonpath="{.data}" '''
    cmd2= cmd + """ | jq -r 'to_entries|map("\(.key)=\(.value | @base64d)")|.[]' """

    # if vim:
    #     cmd2 = cmd2 + """ | vim - """

    result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    # checking whether the secret exists
    if result.returncode != 0:
        click.echo("Failed to list the environment variables. May be app not found")
        return
    
    result2 = subprocess.run(cmd2, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=result.stdout)

    return click.echo(result2.stdout.decode('utf-8').strip())

@env.command(name='set')
@click.option('--app', '-a', prompt=True, help='The application name to set the environment variables', required=True)
@click.argument('env_vars', nargs=-1, required=False)
def set_env(app, env_vars):
    '''
    Set environment variables
    '''
    if len(env_vars) == 0:
        click.echo("Enter the env line by line. Press Ctrl+D to save")
        env_vars = []
        while True:
            try:
                env_vars.append(input())
            except EOFError:
                break

    env_vars = dict([env_var.split('=', 1) for env_var in env_vars])

    last_env = helper.list_env(app).strip()
    last_env = dict([env.split('=', 1) for env in last_env.split('\n')])

    for key, value in env_vars.items():
        last_env[key] = value

    with open("/tmp/env_{}.env".format(app), "w") as f:
        for key, value in last_env.items():
            f.write(f"{key}={value}\n")

    if subprocess.run(f"kubectl create secret generic {app} --from-env-file=/tmp/env_{app}.env --dry-run=client -o yaml > /tmp/secret_{app}.yaml",
                    shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
        click.echo("Generated the secret file with the environment variables")
    
    if subprocess.run(f"kubectl apply -f /tmp/secret_{app}.yaml", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
        click.echo("Successfully set the environment variables")
    
    os.remove(f"/tmp/env_{app}.env")
    os.remove(f"/tmp/secret_{app}.yaml")


## List group
@list.command(name='apps')
def list_apps():
    '''
    List all applications
    '''
    deployments = subprocess.run("kubectl get deploy -l isapp=True", shell=True, check=True, capture_output=True, text=True)
    sts = subprocess.run("kubectl get sts -l isapp=True", shell=True, check=True, capture_output=True, text=True)

    if deployments.stdout+sts.stdout == "":
        click.echo("No applications found")
        return
    
    click.echo(deployments.stdout.strip())

    # remove the first line of the sts output
    click.echo(sts.stdout.strip().split('\n', 1)[1])


@list.command(name='web')
@click.option('--app', '-a', help='The application name to list the web services', required=False)
def list_web(app):
    '''
    List all web services
    '''
    if app is None:
        result = subprocess.run("kubectl get po -l type=web", shell=True, check=True, capture_output=True, text=True)
    else:
        result = subprocess.run(f"kubectl get po -l type=web -l app={app}", shell=True, check=True, capture_output=True, text=True)

    if result.stdout == "":
        click.echo("No web services found")
        return
    
    click.echo(result.stdout)

@list.command(name='timers')
@click.option('--app', '-a', help='The application name to list the timers', required=False)
def list_timers(app):
    '''
    List all timers
    '''
    if app is None:
        result = subprocess.run("kubectl get cronjobs -l type=timers", shell=True, check=True, capture_output=True, text=True)
    else:
        result = subprocess.run(f"kubectl get cronjobs -l type=timers -l app={app}", shell=True, check=True, capture_output=True, text=True)

    if result.stdout == "":
        click.echo("No timers found")
        return
    
    click.echo(result.stdout)

@list.command(name='workers')
@click.option('--app', '-a', help='The application name to list the workers', required=False)
def list_workers(app):
    '''
    List all workers
    '''
    if app is None:
        result = subprocess.run("kubectl get pods -l type=worker", shell=True, check=True, capture_output=True, text=True)
    else:
        result = subprocess.run(f"kubectl get pods -l type=worker -l app={app}", shell=True, check=True, capture_output=True, text=True)

    if result.stdout == "":
        click.echo("No workers found")
        return
    
    click.echo(result.stdout)


## Console group
@console.command(name='psql')
@click.option('--app', '-a', prompt=True, help='The application name to deploy', required=True)
def psql(app):
    '''
    Connect to the application database
    '''

    # get the db url
    env_vars = helper.list_env(app)
    if env_vars == 404:
        return

    # split with first '='
    env_vars = dict([env_var.split('=', 1) for env_var in env_vars.split('\n')])

    if "DASHBOARD_DB_URL" not in env_vars and "DB_URL" not in env_vars and "DATABASE_URL" not in env_vars:
        db_user = env_vars["DATABASE_USERNAME"]
        db_pass = env_vars["DATABASE_PASSWORD"]
        db_host = env_vars["DATABASE_HOST"]
        db_port = env_vars["DATABASE_PORT"]
        db_name = env_vars["DATABASE_NAME"]
        db_url = f"postgres://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        # print(db_url)
    elif "DASHBOARD_DB_URL" in env_vars:
        db_url = env_vars["DASHBOARD_DB_URL"]
    elif "DB_URL" in env_vars:
        db_url = env_vars["DB_URL"]
    elif "DATABASE_URL" in env_vars:
        db_url = env_vars["DATABASE_URL"]
    else:
        click.echo("DB URL not found")
        return

    os.system(f"kubectl exec -it pg-backup-0 -- psql {db_url}")

@console.command(name='rails')
@click.option('--app', '-a', prompt=True, help='The application name to deploy', required=True)
def rails(app):
    '''
    Connect to the application with rails console
    '''
    result = os.system(f"kubectl exec -it $(kubectl get po --sort-by='.status.startTime' --field-selector=status.phase==Running -l app={app}"+" | awk 'NR ==2 {print $1}' ) -- rails c")

    if result != 0:
        click.echo("Failed to connect to the rails console")

@console.command(name='bash')
@click.option('--app', '-a', prompt=True, help='The application name to deploy', required=True)
def bash(app):
    '''
    Connect to the application with bash
    '''
    result = os.system(f"kubectl exec -it $(kubectl get po --sort-by='.status.startTime' --field-selector=status.phase==Running -l app={app}"+" | awk 'NR ==2 {print $1}' ) -- bash")

    if result != 0:
        click.echo("Failed to connect to the bash")
    elif result == 530:
        click.echo("Exited from the bash")

## Restart group
@restart.command(name='web')
@click.option('--app', '-a', prompt=True, help='The application name to restart the web services', required=True)
def restart_app(app):
    '''
    Restart the application
    '''
    result = subprocess.run(f"kubectl delete pods -l app={app} -l type=web", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    click.echo(result.stdout.decode('utf-8').strip())

@restart.command(name='timers')
@click.option('--app', '-a', prompt=True, help='The application name to restart the timers', required=True)
def restart_timers(app):
    '''
    Restart the timers
    '''
    result = subprocess.run(f"kubectl delete pods -l app={app} -l type=timers", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    click.echo(result.stdout.decode('utf-8').strip())

@restart.command(name='workers')
@click.option('--app', '-a', prompt=True, help='The application name to restart the workers', required=True)
def restart_workers(app):
    '''
    Restart the workers
    '''
    result = subprocess.run(f"kubectl delete pods -l app={app} -l type=worker", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    click.echo(result.stdout.decode('utf-8').strip())

@restart.command(name='all')
@click.option('--app', '-a', prompt=True, help='The application name to restart the application', required=True)
def restart_all(app):
    '''
    Restart the application
    '''
    result = subprocess.run(f"kubectl delete pods -l app={app}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    click.echo(result.stdout.decode('utf-8').strip())

