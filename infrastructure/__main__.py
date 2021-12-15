"""A DigitalOcean Python Pulumi program"""
import pulumi
import pulumi_digitalocean as do
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, LocalChartOpts
import pulumi_kubernetes as k8s
from pulumi import ResourceOptions

cluster = do.KubernetesCluster("k8s",
            region="fra1",
            version="1.21.5-do.0",
            node_pool=do.KubernetesClusterNodePoolArgs(
                name="k8s-node-pool-01",
                size="s-2vcpu-4gb",
                node_count=2,
            ))

kube_config = pulumi.Output.unsecret(cluster.kube_configs[0]).raw_config
k8s_provider = k8s.Provider("k8s-provider", kubeconfig=kube_config)

argocd_namespace = k8s.core.v1.Namespace("argocdNamespace", opts=ResourceOptions(provider=k8s_provider), metadata={"name": "argocd"})

argocd = Chart('argocd-chart',
    ChartOpts(
        chart='argo-cd',
        version='3.28.0',
        namespace=argocd_namespace.metadata["name"],
        fetch_opts={'repo': 'https://argoproj.github.io/argo-helm'},
        values= {
            "server": {
                "service": {
                    "type": "LoadBalancer"
                }
            }
        }
        ),
    opts=ResourceOptions(provider=k8s_provider))

argocd_setup = Chart(
    "argocd_setup",
    LocalChartOpts(
        path="../argocd/setup",
        namespace=argocd_namespace.metadata["name"],
    ),opts=ResourceOptions(provider=k8s_provider, depends_on=[argocd])
)

pulumi.export("kubeconfig",kube_config)