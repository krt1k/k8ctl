import subprocess

## helper functions

def check_token_validlity():
    '''
    Check if the token is still valid
    '''
    result = subprocess.run("kubectl get po", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return result.returncode

def list_env(app):
    '''
    List all environment variables
    '''
    cmd = """kubectl get secret {}""".format(app) + ''' -o jsonpath="{.data}" '''
    cmd2= cmd + """ | jq -r 'to_entries|map("\(.key)=\(.value | @base64d)")|.[]' """

    result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    # checking whether the secret exists
    if result.returncode != 0:
        print("Failed to list the environment variables. May be app not found")
        return 404
    
    result2 = subprocess.run(cmd2, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=result.stdout)

    return result2.stdout.decode('utf-8').strip()

def current_cluster():
    '''
    Get the current cluster
    '''
    cmd = "kubectl config current-context"
    result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return result.stdout.decode('utf-8').strip()


def hello_world():
    print("Hello World")