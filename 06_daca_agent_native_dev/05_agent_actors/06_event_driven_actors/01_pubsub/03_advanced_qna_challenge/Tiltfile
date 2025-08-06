load('ext://helm_remote', 'helm_remote') # helm extension -> Dapr Helm Chart
load('ext://nerdctl', 'nerdctl_build') # nerdctl extension -> Docker Build

update_settings(k8s_upsert_timeout_secs=2400) # Increase apply timeout for Helm deployments

nerdctl_build(
    ref='learning-analytics-app',
    context='./learning_analytics_app',
    dockerfile='./learning_analytics_app/Dockerfile',
    live_update=[
        sync('./learning_analytics_app', '/code'),
    ]
)

nerdctl_build(
    ref='memory-app',
    context='./memory_app',
    dockerfile='./memory_app/Dockerfile',
    live_update=[
        sync('./memory_app', '/code'),
    ]
)

nerdctl_build(
    ref='student-interaction-app',
    context='./student_interaction_app',
    dockerfile='./student_interaction_app/Dockerfile',
    live_update=[
        sync('./student_interaction_app', '/code'),
    ]
)

nerdctl_build(
    ref='teacher-support-app',
    context='./teacher_support_app',
    dockerfile='./teacher_support_app/Dockerfile',
    live_update=[
        sync('./teacher_support_app', '/code'),
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
    set=['global.mtls.enabled=false', 'global.ha.enabled=false', 'dapr_scheduler.ha=true', 'dapr_placement.ha=true']
)

helm_remote(
    chart='dapr-dashboard',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    release_name='dapr-dashboard',
    namespace='dapr-system',
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

k8s_yaml(['./components/statestore.yaml', './components/pubsub.yaml'])

k8s_yaml(['./components/subscriptions/student-activity-topic.yaml', './components/subscriptions/teacher-notifications-topic.yaml'])

k8s_yaml(['./kubernetes/learning_analytics_app.yaml'])

k8s_yaml(['./kubernetes/memory_app.yaml'])

k8s_yaml(['./kubernetes/student_interaction_app.yaml'])

k8s_yaml(['./kubernetes/teacher_support_app.yaml'])

k8s_resource(
    'learning-analytics-app',
    port_forwards='8000:8000',
)

k8s_resource(
    'memory-app',
    port_forwards='8001:8000',
)

k8s_resource(
    'student-interaction-app',
    port_forwards='8002:8000',
)

k8s_resource(
    'teacher-support-app',
    port_forwards='8003:8000',
)


