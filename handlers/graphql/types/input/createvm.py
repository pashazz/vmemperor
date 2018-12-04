import uuid

import graphene
import rethinkdb as r

from handlers.graphql.resolvers import with_connection
from authentication import with_authentication
from handlers.graphql.types.input.createvdi import NewVDI
from handlers.graphql.types.tasks.createvm import CreateVMTask
from xenadapter.template import Template
import tornado.ioloop

class NetworkConfiguration(graphene.InputObjectType):
    ip = graphene.InputField(graphene.String, required=True)
    gateway = graphene.InputField(graphene.String, required=True)
    netmask = graphene.InputField(graphene.String, required=True)

    dns0 = graphene.InputField(graphene.String, required=True)
    dns1 = graphene.InputField(graphene.String)


class AutoInstall(graphene.InputObjectType):
    hostname = graphene.InputField(graphene.String, description="VM hostname", required=True)
    mirror_url = graphene.InputField(graphene.String, description="Network installation URL")
    username = graphene.InputField(graphene.String, required=True, description="Name of the newly created user")
    password = graphene.InputField(graphene.String, required=True, description="User and root password")
    fullname = graphene.InputField(graphene.String, description="User's full name")
    partition = graphene.InputField(graphene.String, required=True, description="Partition scheme (TODO)")
    static_ip_config  = graphene.InputField(NetworkConfiguration, description="Static IP configuration, if needed")

def createvm(ctx, task_id, template, VCPUs, disks, ram, name_label, name_description, network, iso=None, install_params=None):
    with ctx.conn:



        tmpl = Template(ctx.user_authenticator, uuid=template)
        vm = tmpl.clone(name_label)

        ctx.set_task_status(
            **CreateVMTask(id=task_id, uuid=vm.uuid, state='cloned', message=f'cloned from {tmpl.uuid}'))
        vm.set_name_description(name_description)
        vm.create(
            insert_log_entry=lambda uuid, state, message: ctx.set_task_status(**CreateVMTask(id=task_id, uuid=uuid, state=state, message=message)),
            provision_config=disks,
            ram_size=ram

        )







class CreateVM(graphene.Mutation):
    task_id = graphene.Field(graphene.ID, required=True, description="Installation task ID")

    class Arguments:
        template = graphene.Argument(graphene.ID, required=True, description="Template ID")
        disks = graphene.Argument(graphene.List(NewVDI))
        ram = graphene.Argument(graphene.Float, required=True, description="RAM size in megabytes")
        name_label = graphene.Argument(graphene.String, required=True, description="VM human-readable name")
        name_description = graphene.Argument(graphene.String, required=True, description="VM human-readable description")
        network = graphene.Argument(graphene.ID, description="Network ID to connect to")
        iso = graphene.Argument(graphene.ID, description="ISO image mounted if conf parameter is null")
        install_params = graphene.Argument(AutoInstall, description="Automatic installation parameters, the installation is done via internet. Only available when template.os_kind is not empty")
        VCPUs = graphene.Argument(graphene.Int, default_value=1, description="Number of created virtual CPUs")


    @staticmethod
    @with_authentication
    @with_connection
    def mutate(root, info, *args, **kwargs):
        task_id  = str(uuid.uuid4())
        ctx = info.context
        ctx.set_task_status(**CreateVMTask(id=task_id, state='cloning'))
        tornado.ioloop.IOLoop.current().run_in_executor(ctx.executor,
                                                        lambda: createvm(ctx, task_id, *args, **kwargs))
        return CreateVM(task_id=task_id)


