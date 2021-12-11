"""A DigitalOcean Python Pulumi program"""
import pulumi
import pulumi_digitalocean as do
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts
import pulumi_kubernetes as k8s

cluster = do.KubernetesCluster("k8s",
            region="fra1",
            version="1.21.5-do.0",
            node_pool=do.KubernetesClusterNodePoolArgs(
                name="front-end-pool",
                size="s-2vcpu-4gb",
                node_count=2,
            ))


cluster_config = do.get_kubernetes_cluster(cluster.name).kube_configs[0].raw_config

k8s_provider = k8s.Provider("k8s-provider", kube_config=cluster_config)

apache = Chart('apache-chart',
    ChartOpts(
        chart='apache',
        version='8.3.2',
        fetch_opts={'repo': 'https://charts.bitnami.com/bitnami'}),
    pulumi.ResourceOptions(provider=k8s_provider))

pulumi.export("kubeconfig",cluster_config)