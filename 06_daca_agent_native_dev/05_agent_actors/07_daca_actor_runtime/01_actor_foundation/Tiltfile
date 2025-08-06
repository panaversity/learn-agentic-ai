load('ext://helm_remote', 'helm_remote')
load('ext://nerdctl', 'nerdctl_build')

update_settings(k8s_upsert_timeout_secs=1800)

# 1. Build the FastAPI image using nerdctl
nerdctl_build(
    ref='ambient-agent',
    context='./ambient-actor',
    dockerfile='./ambient-actor/Dockerfile',
    live_update=[
        sync('./ambient-actor', '/code'),
    ]
)


helm_remote(
    chart='dapr',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    version='1.15',
    release_name='dapr',
    namespace='dapr-system',
    create_namespace=True,
    set=['global.mtls.enabled=false', 'global.ha.enabled=true']
)

helm_remote(
    chart='dapr-dashboard',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    release_name='dapr-dashboard',
    namespace='dapr-system',
)

helm_remote(
    chart='prometheus',
    repo_url='https://prometheus-community.github.io/helm-charts',
    repo_name='prometheus-community',
    release_name='dapr-prom',
    namespace='dapr-monitoring',
    create_namespace=True,
    values=['./kubernetes/monitoring/prometheus-values.yaml']
)

k8s_resource(
    'dapr-dashboard',
    port_forwards=[port_forward(local_port=8080, container_port=8080, name='dapr-dashboard-ui')],
    labels=['dapr-ui']
)

helm_remote(
    chart='redis',
    repo_url='https://charts.bitnami.com/bitnami',
    repo_name='bitnami',
    release_name='redis',
    namespace='default',
    set=['auth.enabled=false']
)

k8s_yaml(['./components/statestore.yaml'])
k8s_yaml(['./components/observability.yaml'])

# Above Dapr setup is Completed
k8s_yaml(['kubernetes/ambient-agent-deploy.yaml'])
k8s_yaml(['kubernetes/monitoring/jaeger.yaml'])

k8s_resource(
    'dapr-prom-prometheus-server',
    port_forwards=[port_forward(local_port=9090, container_port=9090, name='prometheus-server')],
    labels=['dapr-prom']
)

k8s_resource(
    'jaeger',
    port_forwards='16686:16686'
)