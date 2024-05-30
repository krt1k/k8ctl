# k8ctl

k8ctl is a command line tool for managing Rancher multicluster Kubernetes environments. It provides a set of commands to manage clusters, environment variables, applications, and more.

## Installation

To install k8ctl, you can use pip:

```bash
pip install k8ctl
```

## Usage

Here are some of the commands you can use with k8ctl:

- `k8ctl`: Main command line tool.
- `cluster`: Switch, list and get the current cluster.
- `env`: Create, list and delete environment variables of an application.
- `list`: List applications, web, timers, workers.
- `console`: Connect to the application with railsconsole, psql, bash.
- `restart`: Restart the applications, web, timers, workers.
- `login`: Login to a cluster.
- `logs`: Get the logs of the application.

For more detailed usage instructions, you can use the `-h` or `--help` flag with any command.

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.
