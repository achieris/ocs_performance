# Synthetic benchmark tool for block and file persistent volumes in OpenShift Container Storage
- [Introduction](#Introduction)
- [Requirements](#Requirements)
- [Environment configuration](#environment-configuration)
    - [Openshift cluster information](#openshift-cluster-information)
    - [OpenShift nodes configuration](#openshift-nodes-configuration)
    - [OCS node resources](#ocs-node-resources)
    - [OCS SW tested versions](#ocs-sw-tested-versions)
    - [OCS local storage pvs available](#ocs-local-storage-pvs-available)
    - [OCS osds pods](#ocs-osds-pods)
    - [Label OCS nodes as infra nodes](#label-ocs-nodes-as-infra-nodes)
- [Performance testing](#performance-testing)
    - [Clone the repo](#clone-the-repo)
    - [Deploy the environment with the fio statefulsets](#deploy-the-environment-with-the-fio-statefulsets)

## Introduction 
This is in an interactive ansible role for performance testing with synthetic benchmarking workloads, the purpose is to simulate different workload profiles based on your inputs.  
If you already deployed an OCS cluster you can move to [Performance testing](#performance-testing)

## Requirements
- OpenShift Container Platform v4.2+ 
- OpenShift Container Storage v4.2+ (AKA OCS)
- Local Storage Operator
- Supported infrastructures: AWS IPI, VMware UPI (Other platforms have not been tested yet but the tool should work)
- OpenShift management node with admin serviceaccount
- `oc` client with kubeconfig file authentication
- `git` client
- Ansible at least v2.8 

## Environment configuration
### Openshift cluster information
```bash
[ctorres-redhat.com@bastion ~]$ oc version
Client Version: 4.5.7
Server Version: 4.6.3
Kubernetes Version: v1.19.0+9f84db3
```
### OpenShift nodes configuration
```bash
[ctorres-redhat.com@bastion machinesets]$ oc get nodes -L kubernetes.io/hostname -L node.kubernetes.io/instance-type -L failure-domain.beta.kubernetes.io/region -L failure-domain.beta.kubernetes.io/zone
NAME                                            STATUS   ROLES    AGE   VERSION           HOSTNAME          INSTANCE-TYPE   REGION         ZONE
ip-10-0-140-220.eu-central-1.compute.internal   Ready    worker   72s   v1.19.0+9f84db3   ip-10-0-140-220   i3.16xlarge     eu-central-1   eu-central-1a
ip-10-0-145-177.eu-central-1.compute.internal   Ready    worker   12h   v1.19.0+9f84db3   ip-10-0-145-177   m5.4xlarge      eu-central-1   eu-central-1a
ip-10-0-151-216.eu-central-1.compute.internal   Ready    master   12h   v1.19.0+9f84db3   ip-10-0-151-216   c5d.2xlarge     eu-central-1   eu-central-1a
ip-10-0-182-17.eu-central-1.compute.internal    Ready    worker   12h   v1.19.0+9f84db3   ip-10-0-182-17    m5.4xlarge      eu-central-1   eu-central-1b
ip-10-0-183-7.eu-central-1.compute.internal     Ready    worker   74s   v1.19.0+9f84db3   ip-10-0-183-7     i3.16xlarge     eu-central-1   eu-central-1b
ip-10-0-186-76.eu-central-1.compute.internal    Ready    master   12h   v1.19.0+9f84db3   ip-10-0-186-76    c5d.2xlarge     eu-central-1   eu-central-1b
ip-10-0-192-170.eu-central-1.compute.internal   Ready    master   12h   v1.19.0+9f84db3   ip-10-0-192-170   c5d.2xlarge     eu-central-1   eu-central-1c
ip-10-0-212-27.eu-central-1.compute.internal    Ready    worker   12h   v1.19.0+9f84db3   ip-10-0-212-27    m5.4xlarge      eu-central-1   eu-central-1c
ip-10-0-213-116.eu-central-1.compute.internal   Ready    worker   69s   v1.19.0+9f84db3   ip-10-0-213-116   i3.16xlarge     eu-central-1   eu-central-1c
```
### OCS node resources 
```bash
[ctorres-redhat.com@bastion machinesets]$ oc get nodes -l cluster.ocs.openshift.io/openshift-storage=  -o=custom-columns=NAME:.metadata.name,CPU:.status.capacity.cpu,RAM:.status.capacity.memory
NAME                                            CPU   RAM
ip-10-0-140-220.eu-central-1.compute.internal   64    503586776Ki
ip-10-0-183-7.eu-central-1.compute.internal     64    503586776Ki
ip-10-0-213-116.eu-central-1.compute.internal   64    503587072Ki
```
### OCS SW tested versions
```bash
[ctorres-redhat.com@bastion discovery]$ oc get csv -n openshift-local-storage
NAME                                           DISPLAY         VERSION                 REPLACES   PHASE
local-storage-operator.4.5.0-202010301114.p0   Local Storage   4.5.0-202010301114.p0              Succeeded
[ctorres-redhat.com@bastion discovery]$ oc get csv -n openshift-storage
NAME                         DISPLAY                       VERSION        REPLACES   PHASE
ocs-operator.v4.6.0-156.ci   OpenShift Container Storage   4.6.0-156.ci              Succeeded
```
### OCS local storage pvs available
```bash
[ctorres-redhat.com@bastion discovery]$  oc get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                        STORAGECLASS   REASON   AGE
local-pv-130a2b46                          1769Gi     RWO            Delete           Available                                localblock              17s
local-pv-14b33970                          1769Gi     RWO            Delete           Available                                localblock              12s
local-pv-18243a3                           1769Gi     RWO            Delete           Available                                localblock              11s
local-pv-2589f91f                          1769Gi     RWO            Delete           Available                                localblock              11s
local-pv-26f72b87                          1769Gi     RWO            Delete           Available                                localblock              17s
local-pv-3c25a874                          1769Gi     RWO            Delete           Available                                localblock              11s
local-pv-581418b3                          1769Gi     RWO            Delete           Available                                localblock              12s
local-pv-58e52e78                          1769Gi     RWO            Delete           Available                                localblock              17s
local-pv-591f61ef                          1769Gi     RWO            Delete           Available                                localblock              12s
local-pv-5e9378eb                          1769Gi     RWO            Delete           Available                                localblock              17s
local-pv-5f496d8a                          1769Gi     RWO            Delete           Available                                localblock              11s
local-pv-6a593306                          1769Gi     RWO            Delete           Available                                localblock              11s
local-pv-8c4fc950                          1769Gi     RWO            Delete           Available                                localblock              11s
local-pv-8ebd12d1                          1769Gi     RWO            Delete           Available                                localblock              11s
local-pv-90db8d4a                          1769Gi     RWO            Delete           Available                                localblock              16s
local-pv-9931edf4                          1769Gi     RWO            Delete           Available                                localblock              12s
local-pv-9ee290f4                          1769Gi     RWO            Delete           Available                                localblock              17s
local-pv-a17a3e75                          1769Gi     RWO            Delete           Available                                localblock              11s
local-pv-bf64cf6                           1769Gi     RWO            Delete           Available                                localblock              12s
local-pv-c60ccd5d                          1769Gi     RWO            Delete           Available                                localblock              12s
local-pv-c96581a5                          1769Gi     RWO            Delete           Available                                localblock              17s
local-pv-d16ba471                          1769Gi     RWO            Delete           Available                                localblock              12s
local-pv-ecac9549                          1769Gi     RWO            Delete           Available                                localblock              17s
local-pv-eff870f2                          1769Gi     RWO            Delete           Available                                localblock              12s
pvc-59353490-6a69-4a80-a6c6-8e559a501538   1Gi        RWO            Delete           Bound       terminal/terminal-hub-data   gp2                     15h
```
### OCS osds pods
```bash
[ctorres-redhat.com@bastion ocs_performance]$ oc get pods -l app=rook-ceph-osd
NAME                                READY   STATUS    RESTARTS   AGE
rook-ceph-osd-0-5546dbc98f-s9c4f    1/1     Running   0          6m47s
rook-ceph-osd-1-bd4f95845-d66zb     1/1     Running   0          6m46s
rook-ceph-osd-10-589c45bd5c-pwgt5   1/1     Running   0          6m39s
rook-ceph-osd-11-94568d7cd-gwbfs    1/1     Running   0          6m37s
rook-ceph-osd-12-7f6d5dd9fb-mhqpw   1/1     Running   0          6m38s
rook-ceph-osd-13-5ddc6f8d66-v7jsd   1/1     Running   0          6m36s
rook-ceph-osd-14-6bf99c4df8-m2fs9   1/1     Running   0          6m35s
rook-ceph-osd-15-788fd77885-cvd8c   1/1     Running   0          6m34s
rook-ceph-osd-16-655bbcc447-vtfbr   1/1     Running   0          6m32s
rook-ceph-osd-17-6949cd6ff7-scvdn   1/1     Running   0          6m31s
rook-ceph-osd-18-856b7858bc-z5wms   1/1     Running   0          6m33s
rook-ceph-osd-19-6d988f75dd-m42c8   1/1     Running   0          6m30s
rook-ceph-osd-2-77769ddcf4-vbp4m    1/1     Running   0          6m47s
rook-ceph-osd-20-77d8ff8dbc-d58qb   1/1     Running   0          6m28s
rook-ceph-osd-21-fb69fdf7d-srsgs    1/1     Running   0          6m29s
rook-ceph-osd-22-6c97568856-5qdmg   1/1     Running   0          6m27s
rook-ceph-osd-23-868f4995f6-7f78h   1/1     Running   0          6m26s
rook-ceph-osd-3-697847c554-cmkdv    1/1     Running   0          6m46s
rook-ceph-osd-4-cdc44c467-zdcxm     1/1     Running   0          6m44s
rook-ceph-osd-5-5d54cd6cfc-ddtvw    1/1     Running   0          6m43s
rook-ceph-osd-6-59c6fb6664-2lbnv    1/1     Running   0          6m45s
rook-ceph-osd-7-7bb6bf55c-r28jd     1/1     Running   0          6m42s
rook-ceph-osd-8-6f5c5786f9-s9f2g    1/1     Running   0          6m41s
rook-ceph-osd-9-7bd5597b77-wqtbb    1/1     Running   0          6m40s
```
### Label OCS nodes as infra nodes
```bash
[ctorres-redhat.com@bastion ocs_performance]$ oc label nodes ip-10-0-140-220.eu-central-1.compute.internal node-role.kubernetes.io/infra=''
node/ip-10-0-140-220.eu-central-1.compute.internal labeled
[ctorres-redhat.com@bastion ocs_performance]$ oc label nodes ip-10-0-183-7.eu-central-1.compute.internal node-role.kubernetes.io/infra=''
node/ip-10-0-183-7.eu-central-1.compute.internal labeled
[ctorres-redhat.com@bastion ocs_performance]$ oc label nodes ip-10-0-213-116.eu-central-1.compute.internal node-role.kubernetes.io/infra=''
node/ip-10-0-213-116.eu-central-1.compute.internal labeled
```
## Performance testing
### Clone the repo
```bash
[ctorres-redhat.com@bastion ~]$ git clone https://github.com/ctorres80/ocs_performance.git
Cloning into 'ocs_performance'...
remote: Enumerating objects: 394, done.
remote: Counting objects: 100% (394/394), done.
remote: Compressing objects: 100% (215/215), done.
remote: Total 394 (delta 138), reused 374 (delta 118), pack-reused 0
Receiving objects: 100% (394/394), 56.47 KiB | 713.00 KiB/s, done.
Resolving deltas: 100% (138/138), done.
```
### Deploy the environment with the fio statefulsets
1. The ansible role is interactive, you will see a list of options where the option ``1`` is the environment deployment.  
   - It will create a namespace `` testing-ocs-storage ``
   - Deploy two statefulsets:
        - fio-block-ceph-tools -> for cephrbd pvcs consumed by fio pods
        - fio-file-ceph-tools  -> for cephfs pvcs consumed by fio pods
```bash
[ctorres-redhat.com@bastion ocs_performance]$ oc get statefulsets.apps -n testing-ocs-storage
NAME                   READY   AGE
fio-block-ceph-tools   24/24   3h2m
fio-file-ceph-tools    24/24   3h2m
```
In the interactive menu, the ansible role will ask you what's the OCS deployment `` internal `` or `` externl `` please you need to select the right deployment accordinlgy.  
For every fio pod the ansible role will waiting for 10 seconds, that means if you deploy for example 12 pods it will wait for 120 seconds.   
Following an example about how to run the option 1. 
```bash
[ctorres-redhat.com@bastion ocs_performance]$ ansible-playbook use_playbook.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Using ansible rbd_ceph_performance role] ******************************************************************************************************************************************************************

TASK [Gathering Facts] ******************************************************************************************************************************************************************************************
ok: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
Select the task number:
    - 1 -> deploy fio file and block statefulset and pods (project=testing-ocs-storage)
    - 2 -> fio workloads
    - 3 -> clean-fio-tests
    - 4 -> s3cmd-sync
    - 5 -> s3cmd-delete
    - 6 -> delete-fio-pods
:
1
ok: [localhost]

TASK [rbd_ceph_performance : create environment test] ***********************************************************************************************************************************************************
included: /home/ctorres-redhat.com/ocs_performance/roles/rbd_ceph_performance/tasks/deploy_test_env.yml for localhost

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
OCS cluster:
- internal
- external
:
internal
ok: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
How many fio pods ?
:
6
ok: [localhost]

TASK [rbd_ceph_performance : Create the statefulset external] ***************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : Create the statefulset internal] ***************************************************************************************************************************************************
fatal: [localhost]: FAILED! => {"changed": true, "cmd": "export KUBECONFIG=$HOME/.kube/config\noc create -f roles/rbd_ceph_performance/templates/fio-block.yml\noc create -f roles/rbd_ceph_performance/templates/fio-file.yml\n", "delta": "0:00:00.622137", "end": "2020-11-12 11:01:31.196085", "msg": "non-zero return code", "rc": 1, "start": "2020-11-12 11:01:30.573948", "stderr": "Error from server (AlreadyExists): error when creating \"roles/rbd_ceph_performance/templates/fio-block.yml\": namespaces \"testing-ocs-storage\" already exists\nError from server (AlreadyExists): error when creating \"roles/rbd_ceph_performance/templates/fio-file.yml\": namespaces \"testing-ocs-storage\" already exists", "stderr_lines": ["Error from server (AlreadyExists): error when creating \"roles/rbd_ceph_performance/templates/fio-block.yml\": namespaces \"testing-ocs-storage\" already exists", "Error from server (AlreadyExists): error when creating \"roles/rbd_ceph_performance/templates/fio-file.yml\": namespaces \"testing-ocs-storage\" already exists"], "stdout": "statefulset.apps/fio-block-ceph-tools created\nstatefulset.apps/fio-file-ceph-tools created", "stdout_lines": ["statefulset.apps/fio-block-ceph-tools created", "statefulset.apps/fio-file-ceph-tools created"]}
...ignoring

TASK [rbd_ceph_performance : Scale fio for OCS internal to 6 pods in namespace testing-ocs-storage] *************************************************************************************************************
changed: [localhost]

TASK [rbd_ceph_performance : debug] *****************************************************************************************************************************************************************************
ok: [localhost] => {
    "msg": "Waiting for 60 seconds"
}

TASK [rbd_ceph_performance : Waiting for fio pods ready] ********************************************************************************************************************************************************
Pausing for 60 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [localhost]

TASK [rbd_ceph_performance : Print fio available pods] **********************************************************************************************************************************************************
changed: [localhost]

TASK [rbd_ceph_performance : fio pods avaialble for OCS testing internal in namespace testing-ocs-storage] ******************************************************************************************************
ok: [localhost] => {
    "msg": [
        "NAME                     READY   STATUS              RESTARTS   AGE",
        "fio-block-ceph-tools-0   1/1     Running             0          61s",
        "fio-block-ceph-tools-1   1/1     Running             0          47s",
        "fio-block-ceph-tools-2   1/1     Running             0          38s",
        "fio-block-ceph-tools-3   1/1     Running             0          24s",
        "fio-block-ceph-tools-4   1/1     Running             0          17s",
        "fio-block-ceph-tools-5   0/1     ContainerCreating   0          8s",
        "fio-file-ceph-tools-0    1/1     Running             0          61s",
        "fio-file-ceph-tools-1    1/1     Running             0          46s",
        "fio-file-ceph-tools-2    1/1     Running             0          35s",
        "fio-file-ceph-tools-3    1/1     Running             0          26s",
        "fio-file-ceph-tools-4    1/1     Running             0          17s",
        "fio-file-ceph-tools-5    0/1     ContainerCreating   0          7s"
    ]
}

TASK [rbd_ceph_performance : fio benchmark] *********************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : clean-fio-test] ********************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : s3cmd testing] *********************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : s3cmd delete] **********************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : fio delete environment test] *******************************************************************************************************************************************************
skipping: [localhost]

PLAY RECAP ******************************************************************************************************************************************************************************************************
localhost                  : ok=11   changed=3    unreachable=0    failed=0    skipped=6    rescued=0    ignored=1
```
| WARNING: If the project or the statefulset already existing ansible will return warnings and ignore errors.|
| --- |    
I recommended to check if statefulset and fio pods replicas have been created, in our previous example ``6``, you can check from the last output or you can run `` oc get pods -n testing-ocs-storage ``
```bash
[ctorres-redhat.com@bastion ocs_performance]$ oc get pods -n testing-ocs-storage
NAME                     READY   STATUS    RESTARTS   AGE
fio-block-ceph-tools-0   1/1     Running   0          3m17s
fio-block-ceph-tools-1   1/1     Running   0          3m3s
fio-block-ceph-tools-2   1/1     Running   0          2m54s
fio-block-ceph-tools-3   1/1     Running   0          2m40s
fio-block-ceph-tools-4   1/1     Running   0          2m33s
fio-block-ceph-tools-5   1/1     Running   0          2m24s
fio-file-ceph-tools-0    1/1     Running   0          3m17s
fio-file-ceph-tools-1    1/1     Running   0          3m2s
fio-file-ceph-tools-2    1/1     Running   0          2m51s
fio-file-ceph-tools-3    1/1     Running   0          2m42s
fio-file-ceph-tools-4    1/1     Running   0          2m33s
fio-file-ceph-tools-5    1/1     Running   0          2m23s
```

```bash
[ctorres-redhat.com@bastion ocs_performance]$ ansible-playbook use_playbook.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Using ansible rbd_ceph_performance role] ******************************************************************************************************************************************************************

TASK [Gathering Facts] ******************************************************************************************************************************************************************************************
ok: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
Select the task number:
    - 1 -> deploy fio file and block statefulset and pods (project=testing-ocs-storage)
    - 2 -> fio workloads
    - 3 -> clean-fio-tests
    - 4 -> s3cmd-sync
    - 5 -> s3cmd-delete
    - 6 -> delete-fio-pods
:
2
ok: [localhost]

TASK [rbd_ceph_performance : create environment test] ***********************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : fio benchmark] *********************************************************************************************************************************************************************
included: /home/ctorres-redhat.com/ocs_performance/roles/rbd_ceph_performance/tasks/fio-tests.yml for localhost

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
Storage interface:
- file
- block
:
block
ok: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
Valid I/O type:
- read
- write
- randwrite
- randread
- readwrite
- randrw
:
randwrite
ok: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
Valid I/O size in KB example:
- 4, 8, 16, 32, 64, 128, 256, 1024, 2048, 4096 ?
:
4
ok: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
Valid io_threads example:
- 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096
:
128
ok: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
[rbd_ceph_performance : pause]
IO in GB total in GB (max 100):
:
10
ok: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : pause] *****************************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : Collect fio-block-ceph-tool pod names] *********************************************************************************************************************************************
changed: [localhost]

TASK [rbd_ceph_performance : fio bench mixed rbd rw] ************************************************************************************************************************************************************
skipping: [localhost] => (item=fio-block-ceph-tools-0)
skipping: [localhost] => (item=fio-block-ceph-tools-1)
skipping: [localhost] => (item=fio-block-ceph-tools-2)
skipping: [localhost] => (item=fio-block-ceph-tools-3)
skipping: [localhost] => (item=fio-block-ceph-tools-4)
skipping: [localhost] => (item=fio-block-ceph-tools-5)

TASK [rbd_ceph_performance : Wait for fio mixed rw jobs to finish] **********************************************************************************************************************************************
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-0', 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-1', 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-2', 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-3', 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-4', 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-5', 'ansible_loop_var': 'item'})

TASK [rbd_ceph_performance : Print benchmarks stats] ************************************************************************************************************************************************************
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': {'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-0', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': {'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-1', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': {'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-2', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': {'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-3', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': {'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-4', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'})
skipping: [localhost] => (item={'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': {'changed': False, 'skipped': True, 'skip_reason': 'Conditional result was False', 'item': 'fio-block-ceph-tools-5', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'})
skipping: [localhost]

TASK [rbd_ceph_performance : fio bench read, write, randwrite] **************************************************************************************************************************************************
changed: [localhost] => (item=fio-block-ceph-tools-0)
changed: [localhost] => (item=fio-block-ceph-tools-1)
changed: [localhost] => (item=fio-block-ceph-tools-2)
changed: [localhost] => (item=fio-block-ceph-tools-3)
changed: [localhost] => (item=fio-block-ceph-tools-4)
changed: [localhost] => (item=fio-block-ceph-tools-5)

TASK [rbd_ceph_performance : Wait for fio jobs to finish] *******************************************************************************************************************************************************
FAILED - RETRYING: Wait for fio jobs to finish (360 retries left).
......
changed: [localhost] => (item={'started': 1, 'finished': 0, 'ansible_job_id': '732418265582.75886', 'results_file': '/root/.ansible_async/732418265582.75886', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-0', 'ansible_loop_var': 'item'})
changed: [localhost] => (item={'started': 1, 'finished': 0, 'ansible_job_id': '176077182395.75910', 'results_file': '/root/.ansible_async/176077182395.75910', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-1', 'ansible_loop_var': 'item'})
changed: [localhost] => (item={'started': 1, 'finished': 0, 'ansible_job_id': '828924818616.75944', 'results_file': '/root/.ansible_async/828924818616.75944', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-2', 'ansible_loop_var': 'item'})
changed: [localhost] => (item={'started': 1, 'finished': 0, 'ansible_job_id': '203338656611.75979', 'results_file': '/root/.ansible_async/203338656611.75979', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-3', 'ansible_loop_var': 'item'})
changed: [localhost] => (item={'started': 1, 'finished': 0, 'ansible_job_id': '890658462562.76013', 'results_file': '/root/.ansible_async/890658462562.76013', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-4', 'ansible_loop_var': 'item'})
changed: [localhost] => (item={'started': 1, 'finished': 0, 'ansible_job_id': '152204994145.76048', 'results_file': '/root/.ansible_async/152204994145.76048', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-5', 'ansible_loop_var': 'item'})

TASK [rbd_ceph_performance : Print benchmarks stats] ************************************************************************************************************************************************************
ok: [localhost] => (item={'cmd': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-0 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', 'stdout': 'test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128\nfio-3.19\nStarting 1 process\ntest: Laying out IO files (2560 files / total 10240MiB)\n\ntest: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:49 2020\n  write: IOPS=7935, BW=30.0MiB/s (32.5MB/s)(10.0GiB/330339msec); 0 zone resets\n   bw (  KiB/s): min= 2137, max=79216, per=100.00%, avg=31782.67, stdev=3843.83, samples=659\n   iops        : min=  534, max=19804, avg=7945.66, stdev=960.96, samples=659\n  cpu          : usr=3.18%, sys=12.57%, ctx=1619576, majf=0, minf=7\n  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%\n     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%\n     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%\n     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0\n     latency   : target=0, window=0, percentile=100.00%, depth=128\n\nRun status group 0 (all jobs):\n  WRITE: bw=30.0MiB/s (32.5MB/s), 30.0MiB/s-30.0MiB/s (32.5MB/s-32.5MB/s), io=10.0GiB (10.7GB), run=330339-330339msec\n\nDisk stats (read/write):\n  rbd0: ios=0/2626896, merge=0/343827, ticks=0/41686719, in_queue=40368466, util=98.26%', 'stderr': 'Unable to use a TTY - input is not a terminal or the right kind of file', 'rc': 0, 'start': '2020-11-12 11:19:18.003390', 'end': '2020-11-12 11:24:50.010639', 'delta': '0:05:32.007249', 'changed': True, 'invocation': {'module_args': {'_raw_params': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-0 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', '_uses_shell': True, 'warn': True, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'finished': 1, 'ansible_job_id': '732418265582.75886', 'stdout_lines': ['test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128', 'fio-3.19', 'Starting 1 process', 'test: Laying out IO files (2560 files / total 10240MiB)', '', 'test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:49 2020', '  write: IOPS=7935, BW=30.0MiB/s (32.5MB/s)(10.0GiB/330339msec); 0 zone resets', '   bw (  KiB/s): min= 2137, max=79216, per=100.00%, avg=31782.67, stdev=3843.83, samples=659', '   iops        : min=  534, max=19804, avg=7945.66, stdev=960.96, samples=659', '  cpu          : usr=3.18%, sys=12.57%, ctx=1619576, majf=0, minf=7', '  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%', '     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%', '     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%', '     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0', '     latency   : target=0, window=0, percentile=100.00%, depth=128', '', 'Run status group 0 (all jobs):', '  WRITE: bw=30.0MiB/s (32.5MB/s), 30.0MiB/s-30.0MiB/s (32.5MB/s-32.5MB/s), io=10.0GiB (10.7GB), run=330339-330339msec', '', 'Disk stats (read/write):', '  rbd0: ios=0/2626896, merge=0/343827, ticks=0/41686719, in_queue=40368466, util=98.26%'], 'stderr_lines': ['Unable to use a TTY - input is not a terminal or the right kind of file'], 'failed': False, 'attempts': 34, 'item': {'started': 1, 'finished': 0, 'ansible_job_id': '732418265582.75886', 'results_file': '/root/.ansible_async/732418265582.75886', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-0', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'}) => {
    "msg": [
        "test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128",
        "fio-3.19",
        "Starting 1 process",
        "test: Laying out IO files (2560 files / total 10240MiB)",
        "",
        "test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:49 2020",
        "  write: IOPS=7935, BW=30.0MiB/s (32.5MB/s)(10.0GiB/330339msec); 0 zone resets",
        "   bw (  KiB/s): min= 2137, max=79216, per=100.00%, avg=31782.67, stdev=3843.83, samples=659",
        "   iops        : min=  534, max=19804, avg=7945.66, stdev=960.96, samples=659",
        "  cpu          : usr=3.18%, sys=12.57%, ctx=1619576, majf=0, minf=7",
        "  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%",
        "     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%",
        "     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%",
        "     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0",
        "     latency   : target=0, window=0, percentile=100.00%, depth=128",
        "",
        "Run status group 0 (all jobs):",
        "  WRITE: bw=30.0MiB/s (32.5MB/s), 30.0MiB/s-30.0MiB/s (32.5MB/s-32.5MB/s), io=10.0GiB (10.7GB), run=330339-330339msec",
        "",
        "Disk stats (read/write):",
        "  rbd0: ios=0/2626896, merge=0/343827, ticks=0/41686719, in_queue=40368466, util=98.26%"
    ]
}
ok: [localhost] => (item={'cmd': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-1 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', 'stdout': 'test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128\nfio-3.19\nStarting 1 process\ntest: Laying out IO files (2560 files / total 10240MiB)\n\ntest: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:53 2020\n  write: IOPS=7868, BW=30.7MiB/s (32.2MB/s)(10.0GiB/333173msec); 0 zone resets\n   bw (  KiB/s): min=  970, max=103376, per=100.00%, avg=31530.30, stdev=5079.24, samples=665\n   iops        : min=  242, max=25844, avg=7882.57, stdev=1269.82, samples=665\n  cpu          : usr=3.21%, sys=12.32%, ctx=1641713, majf=0, minf=7\n  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%\n     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%\n     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%\n     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0\n     latency   : target=0, window=0, percentile=100.00%, depth=128\n\nRun status group 0 (all jobs):\n  WRITE: bw=30.7MiB/s (32.2MB/s), 30.7MiB/s-30.7MiB/s (32.2MB/s-32.2MB/s), io=10.0GiB (10.7GB), run=333173-333173msec\n\nDisk stats (read/write):\n  rbd0: ios=0/2628894, merge=0/337434, ticks=0/42108279, in_queue=40792918, util=98.16%', 'stderr': 'Unable to use a TTY - input is not a terminal or the right kind of file', 'rc': 0, 'start': '2020-11-12 11:19:18.372157', 'end': '2020-11-12 11:24:53.409659', 'delta': '0:05:35.037502', 'changed': True, 'invocation': {'module_args': {'_raw_params': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-1 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', '_uses_shell': True, 'warn': True, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'finished': 1, 'ansible_job_id': '176077182395.75910', 'stdout_lines': ['test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128', 'fio-3.19', 'Starting 1 process', 'test: Laying out IO files (2560 files / total 10240MiB)', '', 'test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:53 2020', '  write: IOPS=7868, BW=30.7MiB/s (32.2MB/s)(10.0GiB/333173msec); 0 zone resets', '   bw (  KiB/s): min=  970, max=103376, per=100.00%, avg=31530.30, stdev=5079.24, samples=665', '   iops        : min=  242, max=25844, avg=7882.57, stdev=1269.82, samples=665', '  cpu          : usr=3.21%, sys=12.32%, ctx=1641713, majf=0, minf=7', '  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%', '     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%', '     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%', '     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0', '     latency   : target=0, window=0, percentile=100.00%, depth=128', '', 'Run status group 0 (all jobs):', '  WRITE: bw=30.7MiB/s (32.2MB/s), 30.7MiB/s-30.7MiB/s (32.2MB/s-32.2MB/s), io=10.0GiB (10.7GB), run=333173-333173msec', '', 'Disk stats (read/write):', '  rbd0: ios=0/2628894, merge=0/337434, ticks=0/42108279, in_queue=40792918, util=98.16%'], 'stderr_lines': ['Unable to use a TTY - input is not a terminal or the right kind of file'], 'failed': False, 'attempts': 1, 'item': {'started': 1, 'finished': 0, 'ansible_job_id': '176077182395.75910', 'results_file': '/root/.ansible_async/176077182395.75910', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-1', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'}) => {
    "msg": [
        "test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128",
        "fio-3.19",
        "Starting 1 process",
        "test: Laying out IO files (2560 files / total 10240MiB)",
        "",
        "test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:53 2020",
        "  write: IOPS=7868, BW=30.7MiB/s (32.2MB/s)(10.0GiB/333173msec); 0 zone resets",
        "   bw (  KiB/s): min=  970, max=103376, per=100.00%, avg=31530.30, stdev=5079.24, samples=665",
        "   iops        : min=  242, max=25844, avg=7882.57, stdev=1269.82, samples=665",
        "  cpu          : usr=3.21%, sys=12.32%, ctx=1641713, majf=0, minf=7",
        "  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%",
        "     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%",
        "     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%",
        "     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0",
        "     latency   : target=0, window=0, percentile=100.00%, depth=128",
        "",
        "Run status group 0 (all jobs):",
        "  WRITE: bw=30.7MiB/s (32.2MB/s), 30.7MiB/s-30.7MiB/s (32.2MB/s-32.2MB/s), io=10.0GiB (10.7GB), run=333173-333173msec",
        "",
        "Disk stats (read/write):",
        "  rbd0: ios=0/2628894, merge=0/337434, ticks=0/42108279, in_queue=40792918, util=98.16%"
    ]
}
ok: [localhost] => (item={'cmd': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-2 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', 'stdout': 'test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128\nfio-3.19\nStarting 1 process\ntest: Laying out IO files (2560 files / total 10240MiB)\n\ntest: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:50 2020\n  write: IOPS=7947, BW=31.0MiB/s (32.6MB/s)(10.0GiB/329858msec); 0 zone resets\n   bw (  KiB/s): min= 4080, max=37552, per=100.00%, avg=31831.09, stdev=3457.44, samples=658\n   iops        : min= 1020, max= 9388, avg=7957.77, stdev=864.38, samples=658\n  cpu          : usr=3.14%, sys=12.10%, ctx=1653156, majf=0, minf=7\n  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%\n     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%\n     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%\n     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0\n     latency   : target=0, window=0, percentile=100.00%, depth=128\n\nRun status group 0 (all jobs):\n  WRITE: bw=31.0MiB/s (32.6MB/s), 31.0MiB/s-31.0MiB/s (32.6MB/s-32.6MB/s), io=10.0GiB (10.7GB), run=329858-329858msec\n\nDisk stats (read/write):\n  rbd0: ios=0/2627439, merge=0/338167, ticks=0/41674342, in_queue=40357321, util=98.39%', 'stderr': 'Unable to use a TTY - input is not a terminal or the right kind of file', 'rc': 0, 'start': '2020-11-12 11:19:18.758941', 'end': '2020-11-12 11:24:50.180721', 'delta': '0:05:31.421780', 'changed': True, 'invocation': {'module_args': {'_raw_params': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-2 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', '_uses_shell': True, 'warn': True, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'finished': 1, 'ansible_job_id': '828924818616.75944', 'stdout_lines': ['test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128', 'fio-3.19', 'Starting 1 process', 'test: Laying out IO files (2560 files / total 10240MiB)', '', 'test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:50 2020', '  write: IOPS=7947, BW=31.0MiB/s (32.6MB/s)(10.0GiB/329858msec); 0 zone resets', '   bw (  KiB/s): min= 4080, max=37552, per=100.00%, avg=31831.09, stdev=3457.44, samples=658', '   iops        : min= 1020, max= 9388, avg=7957.77, stdev=864.38, samples=658', '  cpu          : usr=3.14%, sys=12.10%, ctx=1653156, majf=0, minf=7', '  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%', '     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%', '     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%', '     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0', '     latency   : target=0, window=0, percentile=100.00%, depth=128', '', 'Run status group 0 (all jobs):', '  WRITE: bw=31.0MiB/s (32.6MB/s), 31.0MiB/s-31.0MiB/s (32.6MB/s-32.6MB/s), io=10.0GiB (10.7GB), run=329858-329858msec', '', 'Disk stats (read/write):', '  rbd0: ios=0/2627439, merge=0/338167, ticks=0/41674342, in_queue=40357321, util=98.39%'], 'stderr_lines': ['Unable to use a TTY - input is not a terminal or the right kind of file'], 'failed': False, 'attempts': 1, 'item': {'started': 1, 'finished': 0, 'ansible_job_id': '828924818616.75944', 'results_file': '/root/.ansible_async/828924818616.75944', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-2', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'}) => {
    "msg": [
        "test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128",
        "fio-3.19",
        "Starting 1 process",
        "test: Laying out IO files (2560 files / total 10240MiB)",
        "",
        "test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:50 2020",
        "  write: IOPS=7947, BW=31.0MiB/s (32.6MB/s)(10.0GiB/329858msec); 0 zone resets",
        "   bw (  KiB/s): min= 4080, max=37552, per=100.00%, avg=31831.09, stdev=3457.44, samples=658",
        "   iops        : min= 1020, max= 9388, avg=7957.77, stdev=864.38, samples=658",
        "  cpu          : usr=3.14%, sys=12.10%, ctx=1653156, majf=0, minf=7",
        "  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%",
        "     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%",
        "     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%",
        "     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0",
        "     latency   : target=0, window=0, percentile=100.00%, depth=128",
        "",
        "Run status group 0 (all jobs):",
        "  WRITE: bw=31.0MiB/s (32.6MB/s), 31.0MiB/s-31.0MiB/s (32.6MB/s-32.6MB/s), io=10.0GiB (10.7GB), run=329858-329858msec",
        "",
        "Disk stats (read/write):",
        "  rbd0: ios=0/2627439, merge=0/338167, ticks=0/41674342, in_queue=40357321, util=98.39%"
    ]
}
ok: [localhost] => (item={'cmd': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-3 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', 'stdout': 'test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128\nfio-3.19\nStarting 1 process\ntest: Laying out IO files (2560 files / total 10240MiB)\n\ntest: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:51 2020\n  write: IOPS=7920, BW=30.9MiB/s (32.4MB/s)(10.0GiB/330977msec); 0 zone resets\n   bw (  KiB/s): min=11848, max=59360, per=100.00%, avg=31692.43, stdev=3394.67, samples=660\n   iops        : min= 2962, max=14840, avg=7923.11, stdev=848.67, samples=660\n  cpu          : usr=3.24%, sys=12.47%, ctx=1625475, majf=0, minf=7\n  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%\n     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%\n     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%\n     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0\n     latency   : target=0, window=0, percentile=100.00%, depth=128\n\nRun status group 0 (all jobs):\n  WRITE: bw=30.9MiB/s (32.4MB/s), 30.9MiB/s-30.9MiB/s (32.4MB/s-32.4MB/s), io=10.0GiB (10.7GB), run=330977-330977msec\n\nDisk stats (read/write):\n  rbd1: ios=0/2628845, merge=0/340914, ticks=0/41969673, in_queue=40650242, util=98.43%', 'stderr': 'Unable to use a TTY - input is not a terminal or the right kind of file', 'rc': 0, 'start': '2020-11-12 11:19:19.140472', 'end': '2020-11-12 11:24:51.899206', 'delta': '0:05:32.758734', 'changed': True, 'invocation': {'module_args': {'_raw_params': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-3 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', '_uses_shell': True, 'warn': True, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'finished': 1, 'ansible_job_id': '203338656611.75979', 'stdout_lines': ['test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128', 'fio-3.19', 'Starting 1 process', 'test: Laying out IO files (2560 files / total 10240MiB)', '', 'test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:51 2020', '  write: IOPS=7920, BW=30.9MiB/s (32.4MB/s)(10.0GiB/330977msec); 0 zone resets', '   bw (  KiB/s): min=11848, max=59360, per=100.00%, avg=31692.43, stdev=3394.67, samples=660', '   iops        : min= 2962, max=14840, avg=7923.11, stdev=848.67, samples=660', '  cpu          : usr=3.24%, sys=12.47%, ctx=1625475, majf=0, minf=7', '  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%', '     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%', '     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%', '     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0', '     latency   : target=0, window=0, percentile=100.00%, depth=128', '', 'Run status group 0 (all jobs):', '  WRITE: bw=30.9MiB/s (32.4MB/s), 30.9MiB/s-30.9MiB/s (32.4MB/s-32.4MB/s), io=10.0GiB (10.7GB), run=330977-330977msec', '', 'Disk stats (read/write):', '  rbd1: ios=0/2628845, merge=0/340914, ticks=0/41969673, in_queue=40650242, util=98.43%'], 'stderr_lines': ['Unable to use a TTY - input is not a terminal or the right kind of file'], 'failed': False, 'attempts': 1, 'item': {'started': 1, 'finished': 0, 'ansible_job_id': '203338656611.75979', 'results_file': '/root/.ansible_async/203338656611.75979', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-3', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'}) => {
    "msg": [
        "test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128",
        "fio-3.19",
        "Starting 1 process",
        "test: Laying out IO files (2560 files / total 10240MiB)",
        "",
        "test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:51 2020",
        "  write: IOPS=7920, BW=30.9MiB/s (32.4MB/s)(10.0GiB/330977msec); 0 zone resets",
        "   bw (  KiB/s): min=11848, max=59360, per=100.00%, avg=31692.43, stdev=3394.67, samples=660",
        "   iops        : min= 2962, max=14840, avg=7923.11, stdev=848.67, samples=660",
        "  cpu          : usr=3.24%, sys=12.47%, ctx=1625475, majf=0, minf=7",
        "  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%",
        "     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%",
        "     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%",
        "     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0",
        "     latency   : target=0, window=0, percentile=100.00%, depth=128",
        "",
        "Run status group 0 (all jobs):",
        "  WRITE: bw=30.9MiB/s (32.4MB/s), 30.9MiB/s-30.9MiB/s (32.4MB/s-32.4MB/s), io=10.0GiB (10.7GB), run=330977-330977msec",
        "",
        "Disk stats (read/write):",
        "  rbd1: ios=0/2628845, merge=0/340914, ticks=0/41969673, in_queue=40650242, util=98.43%"
    ]
}
ok: [localhost] => (item={'cmd': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-4 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', 'stdout': 'test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128\nfio-3.19\nStarting 1 process\ntest: Laying out IO files (2560 files / total 10240MiB)\n\ntest: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:52 2020\n  write: IOPS=7904, BW=30.9MiB/s (32.4MB/s)(10.0GiB/331633msec); 0 zone resets\n   bw (  KiB/s): min= 4696, max=70528, per=100.00%, avg=31641.37, stdev=3643.48, samples=662\n   iops        : min= 1174, max=17632, avg=7910.35, stdev=910.87, samples=662\n  cpu          : usr=3.26%, sys=12.33%, ctx=1650876, majf=0, minf=7\n  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%\n     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%\n     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%\n     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0\n     latency   : target=0, window=0, percentile=100.00%, depth=128\n\nRun status group 0 (all jobs):\n  WRITE: bw=30.9MiB/s (32.4MB/s), 30.9MiB/s-30.9MiB/s (32.4MB/s-32.4MB/s), io=10.0GiB (10.7GB), run=331633-331633msec\n\nDisk stats (read/write):\n  rbd1: ios=0/2627940, merge=0/340415, ticks=0/42014540, in_queue=40698541, util=98.38%', 'stderr': 'Unable to use a TTY - input is not a terminal or the right kind of file', 'rc': 0, 'start': '2020-11-12 11:19:19.541724', 'end': '2020-11-12 11:24:52.782596', 'delta': '0:05:33.240872', 'changed': True, 'invocation': {'module_args': {'_raw_params': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-4 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', '_uses_shell': True, 'warn': True, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'finished': 1, 'ansible_job_id': '890658462562.76013', 'stdout_lines': ['test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128', 'fio-3.19', 'Starting 1 process', 'test: Laying out IO files (2560 files / total 10240MiB)', '', 'test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:52 2020', '  write: IOPS=7904, BW=30.9MiB/s (32.4MB/s)(10.0GiB/331633msec); 0 zone resets', '   bw (  KiB/s): min= 4696, max=70528, per=100.00%, avg=31641.37, stdev=3643.48, samples=662', '   iops        : min= 1174, max=17632, avg=7910.35, stdev=910.87, samples=662', '  cpu          : usr=3.26%, sys=12.33%, ctx=1650876, majf=0, minf=7', '  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%', '     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%', '     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%', '     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0', '     latency   : target=0, window=0, percentile=100.00%, depth=128', '', 'Run status group 0 (all jobs):', '  WRITE: bw=30.9MiB/s (32.4MB/s), 30.9MiB/s-30.9MiB/s (32.4MB/s-32.4MB/s), io=10.0GiB (10.7GB), run=331633-331633msec', '', 'Disk stats (read/write):', '  rbd1: ios=0/2627940, merge=0/340415, ticks=0/42014540, in_queue=40698541, util=98.38%'], 'stderr_lines': ['Unable to use a TTY - input is not a terminal or the right kind of file'], 'failed': False, 'attempts': 1, 'item': {'started': 1, 'finished': 0, 'ansible_job_id': '890658462562.76013', 'results_file': '/root/.ansible_async/890658462562.76013', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-4', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'}) => {
    "msg": [
        "test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128",
        "fio-3.19",
        "Starting 1 process",
        "test: Laying out IO files (2560 files / total 10240MiB)",
        "",
        "test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:52 2020",
        "  write: IOPS=7904, BW=30.9MiB/s (32.4MB/s)(10.0GiB/331633msec); 0 zone resets",
        "   bw (  KiB/s): min= 4696, max=70528, per=100.00%, avg=31641.37, stdev=3643.48, samples=662",
        "   iops        : min= 1174, max=17632, avg=7910.35, stdev=910.87, samples=662",
        "  cpu          : usr=3.26%, sys=12.33%, ctx=1650876, majf=0, minf=7",
        "  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%",
        "     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%",
        "     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%",
        "     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0",
        "     latency   : target=0, window=0, percentile=100.00%, depth=128",
        "",
        "Run status group 0 (all jobs):",
        "  WRITE: bw=30.9MiB/s (32.4MB/s), 30.9MiB/s-30.9MiB/s (32.4MB/s-32.4MB/s), io=10.0GiB (10.7GB), run=331633-331633msec",
        "",
        "Disk stats (read/write):",
        "  rbd1: ios=0/2627940, merge=0/340415, ticks=0/42014540, in_queue=40698541, util=98.38%"
    ]
}
ok: [localhost] => (item={'cmd': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-5 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', 'stdout': 'test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128\nfio-3.19\nStarting 1 process\ntest: Laying out IO files (2560 files / total 10240MiB)\n\ntest: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:50 2020\n  write: IOPS=7964, BW=31.1MiB/s (32.6MB/s)(10.0GiB/329124msec); 0 zone resets\n   bw (  KiB/s): min= 8024, max=39424, per=100.00%, avg=31889.48, stdev=3339.72, samples=656\n   iops        : min= 2006, max= 9856, avg=7972.37, stdev=834.93, samples=656\n  cpu          : usr=3.16%, sys=12.15%, ctx=1663703, majf=0, minf=9\n  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%\n     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%\n     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%\n     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0\n     latency   : target=0, window=0, percentile=100.00%, depth=128\n\nRun status group 0 (all jobs):\n  WRITE: bw=31.1MiB/s (32.6MB/s), 31.1MiB/s-31.1MiB/s (32.6MB/s-32.6MB/s), io=10.0GiB (10.7GB), run=329124-329124msec\n\nDisk stats (read/write):\n  rbd1: ios=0/2627562, merge=0/335564, ticks=0/41746494, in_queue=40429005, util=98.43%', 'stderr': 'Unable to use a TTY - input is not a terminal or the right kind of file', 'rc': 0, 'start': '2020-11-12 11:19:19.945194', 'end': '2020-11-12 11:24:50.844633', 'delta': '0:05:30.899439', 'changed': True, 'invocation': {'module_args': {'_raw_params': 'export KUBECONFIG=$HOME/.kube/config\noc exec -n testing-ocs-storage fio-block-ceph-tools-5 -it -- fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --directory=/usr/share/ocs-pvc --bs=4K --iodepth=128 --size=10G --rw=randwrite --nrfiles=2560.0 --refill_buffers=1\n', '_uses_shell': True, 'warn': True, 'stdin_add_newline': True, 'strip_empty_ends': True, 'argv': None, 'chdir': None, 'executable': None, 'creates': None, 'removes': None, 'stdin': None}}, 'finished': 1, 'ansible_job_id': '152204994145.76048', 'stdout_lines': ['test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128', 'fio-3.19', 'Starting 1 process', 'test: Laying out IO files (2560 files / total 10240MiB)', '', 'test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:50 2020', '  write: IOPS=7964, BW=31.1MiB/s (32.6MB/s)(10.0GiB/329124msec); 0 zone resets', '   bw (  KiB/s): min= 8024, max=39424, per=100.00%, avg=31889.48, stdev=3339.72, samples=656', '   iops        : min= 2006, max= 9856, avg=7972.37, stdev=834.93, samples=656', '  cpu          : usr=3.16%, sys=12.15%, ctx=1663703, majf=0, minf=9', '  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%', '     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%', '     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%', '     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0', '     latency   : target=0, window=0, percentile=100.00%, depth=128', '', 'Run status group 0 (all jobs):', '  WRITE: bw=31.1MiB/s (32.6MB/s), 31.1MiB/s-31.1MiB/s (32.6MB/s-32.6MB/s), io=10.0GiB (10.7GB), run=329124-329124msec', '', 'Disk stats (read/write):', '  rbd1: ios=0/2627562, merge=0/335564, ticks=0/41746494, in_queue=40429005, util=98.43%'], 'stderr_lines': ['Unable to use a TTY - input is not a terminal or the right kind of file'], 'failed': False, 'attempts': 1, 'item': {'started': 1, 'finished': 0, 'ansible_job_id': '152204994145.76048', 'results_file': '/root/.ansible_async/152204994145.76048', 'changed': True, 'failed': False, 'item': 'fio-block-ceph-tools-5', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'}) => {
    "msg": [
        "test: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=128",
        "fio-3.19",
        "Starting 1 process",
        "test: Laying out IO files (2560 files / total 10240MiB)",
        "",
        "test: (groupid=0, jobs=1): err= 0: pid=30: Thu Nov 12 11:24:50 2020",
        "  write: IOPS=7964, BW=31.1MiB/s (32.6MB/s)(10.0GiB/329124msec); 0 zone resets",
        "   bw (  KiB/s): min= 8024, max=39424, per=100.00%, avg=31889.48, stdev=3339.72, samples=656",
        "   iops        : min= 2006, max= 9856, avg=7972.37, stdev=834.93, samples=656",
        "  cpu          : usr=3.16%, sys=12.15%, ctx=1663703, majf=0, minf=9",
        "  IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%",
        "     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%",
        "     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%",
        "     issued rwts: total=0,2621440,0,0 short=0,0,0,0 dropped=0,0,0,0",
        "     latency   : target=0, window=0, percentile=100.00%, depth=128",
        "",
        "Run status group 0 (all jobs):",
        "  WRITE: bw=31.1MiB/s (32.6MB/s), 31.1MiB/s-31.1MiB/s (32.6MB/s-32.6MB/s), io=10.0GiB (10.7GB), run=329124-329124msec",
        "",
        "Disk stats (read/write):",
        "  rbd1: ios=0/2627562, merge=0/335564, ticks=0/41746494, in_queue=40429005, util=98.43%"
    ]
}

TASK [rbd_ceph_performance : clean-fio-test] ********************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : s3cmd testing] *********************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : s3cmd delete] **********************************************************************************************************************************************************************
skipping: [localhost]

TASK [rbd_ceph_performance : fio delete environment test] *******************************************************************************************************************************************************
skipping: [localhost]

PLAY RECAP ******************************************************************************************************************************************************************************************************
localhost                  : ok=12   changed=3    unreachable=0    failed=0    skipped=10   rescued=0    ignored=0
```
### Using toolbox for cephrbd monitoring
```bash
[ctorres-redhat.com@bastion ~]$ oc -n openshift-storage rsh rook-ceph-tools-85dc5f7bc8-mj6xk
sh-4.4# rbd perf image iostat
NAME                                                                               WR   RD  WR_BYTES  RD_BYTES    WR_LAT   RD_LAT
ocs-storagecluster-cephblockpool/csi-vol-8b8ef8da-24d6-11eb-afdf-0a580a82020d 8.29k/s  0/s  32 MiB/s     0 B/s  12.84 ms  0.00 ns
ocs-storagecluster-cephblockpool/csi-vol-8608dbbf-24d6-11eb-afdf-0a580a82020d 8.18k/s  0/s  32 MiB/s     0 B/s  12.68 ms  0.00 ns
ocs-storagecluster-cephblockpool/csi-vol-6be9bc87-24d6-11eb-afdf-0a580a82020d 8.18k/s  0/s  32 MiB/s     0 B/s  12.78 ms  0.00 ns
ocs-storagecluster-cephblockpool/csi-vol-79a4e26b-24d6-11eb-afdf-0a580a82020d 8.16k/s  0/s  32 MiB/s     0 B/s  12.90 ms  0.00 ns
ocs-storagecluster-cephblockpool/csi-vol-8197574a-24d6-11eb-afdf-0a580a82020d 8.15k/s  0/s  32 MiB/s     0 B/s  12.81 ms  0.00 ns
ocs-storagecluster-cephblockpool/csi-vol-741f501c-24d6-11eb-afdf-0a580a82020d 8.07k/s  0/s  32 MiB/s     0 B/s  12.85 ms  0.00 ns
ocs-storagecluster-cephblockpool/csi-vol-7c021d1f-248c-11eb-afdf-0a580a82020d     2/s  0/s  24 KiB/s     0 B/s   7.78 ms  0.00 ns
```