import boto3
import botocore
import click

session = boto3.Session(profile_name='profile')
ec2 = session.resource('ec2')

#############FILTRAR INSTANCIAS#################################################
def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return(instances)
#############VER SI EL VOLUMEN TIENE SNAPSHOTS PENDIENTES#######################
def has_pending_snapshots(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'
################################################################################
################################################################################
@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('instances')
def instances():
    """Commands for instances"""

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""
#############LISTAR INSTANCIAS (LIST)###########################################
@instances.command('list')
@click.option('--project', default=None,
    help='Only instances for project (tag project:<name>)')

def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.instance_id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            tags.get('project', '<no project>')
        )))
    return
################################################################################
#############LISTAR VOLUMES (LIST)##############################################
@volumes.command('list')
@click.option('--project', default=None,
    help='Only volumes for project (tag project:<name>)')

def list_volumes(project):
    "List EC2 Volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
            i.id,
            v.id,
            v.state,
            str(v.size) + "GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return
################################################################################
#############LISTAR SNAPSHOTS (LIST)############################################
@snapshots.command('list')
@click.option('--project', default=None,
    help='Only snapshots for project (tag project:<name>)')
@click.option('--all', 'list_all', default=False, is_flag=True,
    help='List all the snapshots for each volume, not just the most recent one')

def list_snapshots(project, list_all):
    "List EC2 Snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                i.id,
                v.id,
                s.id,
                s.state,
                s.progress,
                s.start_time.strftime("%c")
                )))
                if s.state == 'completed' and not list_all: break

    return
################################################################################
#############INICIAR INSTANCIAS (START)#########################################
@instances.command('start')
@click.option('--project', default=None,
    help='Only instances for project (tag project:<name>)')

def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print('Starting {0}....'.format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not start {0}. ".format(i.id) + str(e))
            continue

    return
################################################################################
#############DETENER INSTANCIAS (STOP)##########################################
@instances.command('stop')
@click.option('--project', default=None,
    help='Only instances for project (tag project:<name>)')

def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print('Stopping {0}....'.format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not Stop {0}. ".format(i.id) + str(e))
            continue
    return
################################################################################
#########CREAR SNAPSHOTS DE VOLUMENES ASOCIADOS A LAS INSTANCIAS (LIST)#########
@instances.command('snapshot', help='create snapshots of all volumes')
@click.option('--project', default=None,
    help='Only instances for project (tag project:<name>)')

def create_snapshots(project):
    "Create snapshot from volumes from EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping{0}.... ".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print(" Skipping {0}, snapshot already in progress".format(v.id))
                continue
            print("  Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by SnapshotAlyzer")

        print("Starting {0}.... ".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job's done!")
    return
################################################################################

if __name__ == '__main__':
    cli()
