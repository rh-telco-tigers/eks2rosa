# eks2rosa
Migrating an application from EKS to ROSA.



Migrating a Stateful Kubernetes Application from AWS EKS to ROSA using OpenShift Pipelines and Crane
This repository demonstrates how to migrate a stateful Kubernetes application (with PVCs) from AWS EKS to Red Hat OpenShift Service on AWS (ROSA) using OpenShift Pipelines (Tekton) with the upstream Crane project.
The migration is fully Kubernetes-native, automated, and repeatable.

Overview
What this does
Migrates Kubernetes workloads including Persistent Volume Claims


Uses Crane as the migration engine


Uses OpenShift Pipelines to orchestrate the migration


Supports EKS → ROSA cluster migration


High-level flow
Configure source (EKS) and destination (ROSA) access


Create a unified kubeconfig for Crane


Store kubeconfig as a Kubernetes Secret


Trigger a Tekton PipelineRun


Restore application and data on ROSA



Prerequisites
Clusters
AWS EKS cluster (source)


ROSA cluster (destination)


Tools
AWS CLI


oc CLI (logged into ROSA)


kubectl


OpenShift Pipelines Operator installed on ROSA


Verify access:
kubectl get nodes
oc get nodes

Install Crane Pipeline Tasks
Deploy the Crane Tekton tasks into the ROSA cluster.
oc apply -k config/default
This installs all required Tekton Tasks and supporting resources.

Create Target Namespace
Create a namespace for the migrated application.
oc new-project game-2048

Configure Kubernetes Contexts
Set ROSA as Destination Context
oc config use-context game-2048/api-myrosa-pyfx-p1-openshiftapps-com:6443/srikanth
oc config rename-context $(oc config current-context) dest

Configure AWS Credentials
Export AWS credentials so Crane can authenticate with EKS.
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION

Add EKS Cluster Context
Fetch the kubeconfig for EKS.
aws eks update-kubeconfig --region us-east-2 --name mycluster

Generate EKS Authentication Token
EKS tokens are short-lived (~15 minutes).
EKS_TOKEN=$(aws eks get-token \
  --cluster-name mycluster \
  --region us-east-2 \
  --query 'status.token' \
  --output text)

Collect Cluster Details
EKS
EKS_ENDPOINT="https://E7FD1F839313749F626E776C0B5D99EB.gr7.us-east-2.eks.amazonaws.com"
EKS_CA="xxxxxxx"
ROSA
ROSA_ENDPOINT="https://api.myrosa.pyfx.p1.openshiftapps.com:6443"
ROSA_TOKEN="sha256~abc"

Create Crane-Compatible Kubeconfig
Crane requires a kubeconfig containing both source and destination clusters.
cat > /tmp/kubeconfig-crane <<EOF
apiVersion: v1
kind: Config
clusters:
- name: src
  cluster:
    server: ${EKS_ENDPOINT}
    certificate-authority-data: ${EKS_CA}
- name: dest
  cluster:
    server: ${ROSA_ENDPOINT}
    insecure-skip-tls-verify: true
contexts:
- name: src
  context:
    cluster: src
    user: src
- name: dest
  context:
    cluster: dest
    user: dest
    namespace: game-2048
users:
- name: src
  user:
    token: ${EKS_TOKEN}
- name: dest
  user:
    token: ${ROSA_TOKEN}
current-context: src
EOF

Create Kubeconfig Secret
Crane pipeline tasks read the kubeconfig from a Kubernetes Secret.
kubectl delete secret kubeconfig -n game-2048
kubectl create secret generic kubeconfig \
  --from-file=kubeconfig=/tmp/kubeconfig-crane \
  -n game-2048

Grant Required Security Context Constraints
Some restored workloads require elevated privileges.
oc --context dest adm policy add-scc-to-user anyuid -z default -n game-2048
oc --context dest adm policy add-scc-to-user privileged -z default -n game-2048

Trigger the Migration Pipeline
Apply the PipelineRun definition.
oc --context dest apply -f app.yaml
Expected output:
pipelinerun.tekton.dev/stateful-guestbook-example created

Monitor Migration
Check pipeline status:
tkn pipelinerun list -n game-2048
tkn pipelinerun logs stateful-guestbook-example -n game-2048 -f

Result
After completion:
Application manifests are recreated on ROSA


PVCs are restored


Stateful workload runs on OpenShift



Notes & Limitations
EKS tokens expire quickly — regenerate if the pipeline fails


Ensure network access between clusters


SCC permissions may vary depending on workload


PVC migration speed depends on volume size and storage backend



Why This Approach
Kubernetes-native


Declarative & repeatable


No manual YAML rewriting


Works for CI/CD-style migrations


Enterprise-ready



References
OpenShift Pipelines (Tekton)


Crane (Upstream Kubernetes Migration Project)


AWS EKS


Red Hat OpenShift Service on AWS (ROSA)






Pre-requisities:

Setup AWS EKS
Setup ROSA
Setup Pipelines Operator on ROSA
Download AWS CLI
Download oc / kubectl for ROSA


Setup pipelines tasks for crane

oc apply -k config/default

oc new-project game-2048

Create src and dest kubeconfig contexts for EKS and ROSA

oc config use-context game-2048/api-myrosa-pyfx-p1-openshiftapps-com:6443/srikanth
oc config rename-context $(oc config current-context) dest

export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION

Add kube context for EKS
aws eks update-kubeconfig --region us-east-2 --name mycluster

# Get EKS token (valid ~15 min)
EKS_TOKEN=$(aws eks get-token --cluster-name mycluster --region us-east-2 --query 'status.token' --output text)

# Get EKS CA and endpoint
EKS_ENDPOINT="https://E7FD1F839313749F626E776C0B5D99EB.gr7.us-east-2.eks.amazonaws.com"

EKS_CA="xxxxxxx”

# ROSA details (from your existing config)
ROSA_ENDPOINT="https://api.myrosa.pyfx.p1.openshiftapps.com:6443"
ROSA_TOKEN="sha256~abc"


# Create simplified kubeconfig
cat > /tmp/kubeconfig-crane <<EOF
apiVersion: v1
kind: Config
clusters:
- name: src
  cluster:
    server: ${EKS_ENDPOINT}
    certificate-authority-data: ${EKS_CA}
- name: dest
  cluster:
    server: ${ROSA_ENDPOINT}
    insecure-skip-tls-verify: true
contexts:
- name: src
  context:
    cluster: src
    user: src
- name: dest
  context:
    cluster: dest
    user: dest
    namespace: game-2048
users:
- name: src
  user:
    token: ${EKS_TOKEN}
- name: dest
  user:
    token: ${ROSA_TOKEN}
current-context: src
EOF

# Update the secret
kubectl delete secret kubeconfig -n game-2048
kubectl create secret generic kubeconfig --from-file=kubeconfig=/tmp/kubeconfig-crane -n game-2048


oc --context dest adm policy add-scc-to-user anyuid -z default -n game-2048

oc --context dest adm policy add-scc-to-user privileged -z default -n game-2048


oc --context dest apply -f app.yaml
pipelinerun.tekton.dev/stateful-guestbook-example created


