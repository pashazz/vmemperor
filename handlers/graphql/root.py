from graphene_tornado.tornado_graphql_handler import TornadoGraphQLHandler
from rx import Observable
import graphene

from graphene import ObjectType, Schema

from tornado.escape import to_unicode

from handlers.graphql.types.input.createvm import CreateVM
from handlers.graphql.types.input.vm import VMMutation, VMStartMutation, VMShutdownMutation, VMRebootMutation, \
    VMPauseMutation
from xenadapter.disk import GISO, GVDI, ISO, VDI
from xenadapter.task import GTask
from xenadapter.template import Template, GTemplate
from xenadapter.sr import SR, GSR
from xenadapter.vm import VM, GVM
from xenadapter.network import Network, GNetwork

from handlers.graphql.types.input.template import TemplateMutation

class QueryRoot(ObjectType):

    vms = graphene.List(GVM, required=True, resolver=VM.resolve_all(), description="All VMs available to user")
    vm = graphene.Field(GVM, required=True, uuid=graphene.ID(), resolver=VM.resolve_one())

    networks = graphene.List(GNetwork, required=True, resolver=Network.resolve_all(), description="All Networks available to user")
    network = graphene.Field(GNetwork, required=True, uuid=graphene.ID(), resolver=Network.resolve_one(), description="Information about a single network")

    srs = graphene.List(GSR, required=True, resolver=SR.resolve_all(),
                             description="All Storage repositories available to user")
    sr = graphene.Field(GSR, required=True, uuid=graphene.ID(), resolver=SR.resolve_one(), description="Information about a single storage repository")


    vdis = graphene.List(GVDI, required=True, resolver=VDI.resolve_all(), description="All Virtual Disk Images (hard disks), available for user")
    vdi = graphene.Field(GVDI, required=True, uuid=graphene.ID(), resolver=VDI.resolve_one(), description="Information about a single virtual disk image (hard disk)")

    isos = graphene.List(GISO, required=True, resolver=ISO.resolve_all(), description="All ISO images available for user")
    iso = graphene.Field(GVDI, required=True, uuid=graphene.ID(), resolver=ISO.resolve_one(),
                         description="Information about a single ISO image")

    templates = graphene.List(GTemplate,required=True, resolver=Template.resolve_all(), description="All templates")






class MutationRoot(ObjectType):
    create_VM = CreateVM.Field(description="Create a new VM")
    template = TemplateMutation.Field(description="Edit template options")
    vm = VMMutation.Field(description="Edit VM options")
    vm_start = VMStartMutation.Field(description="Start VM")
    vm_shutdown = VMShutdownMutation.Field(description="Shut down VM")
    vm_reboot = VMRebootMutation.Field(description="Reboot VM")
    vm_pause = VMPauseMutation.Field(description="If VM is Running, pause VM. If Paused, unpause VM")




def MakeSubscriptionWithChangeType(_class : type) -> type:
    #class Subscription(ObjectType):
    #    changeType = graphene.Field(graphene.String, required=True, description="Change type: one of")
    #    value = graphene.Field(_class, required=True)

    #Subscription.__name__ = f'{_class.__name__}sSubscription'
    #return Subscription

    return type(f'{_class.__name__}sSubscription',
                (ObjectType, ),
                {
                    'change_type': graphene.Field(graphene.String, required=True, description="Change type"),
                    'value': graphene.Field(_class, required=True)
                })


def MakeSubscription(_class : type) -> type:
    return type(f'{_class.__name__}Subscription',
                (ObjectType, ),
                {
                    _class.__name__: graphene.Field(_class)
                })



class SubscriptionRoot(ObjectType):
    '''
    All subscriptions must return  Observable
    '''
    vms = graphene.Field(MakeSubscriptionWithChangeType(GVM), required=True)
    task = graphene.Field(MakeSubscription(GTask), required=True, uuid=graphene.ID())

    def resolve_task(root, info, uuid):
        async def iterable_to_task():
            from  rethinkdb import RethinkDB
            r = RethinkDB()

            r.set_loop_type("asyncio")
            db = r.db('vmemperor')
            conn = await r.connect()
            changes = await db.table('tasks').get(uuid).changes(include_types=True, include_initial=True).run(conn)
            while True:
                change = await changes.next()
                if not change:
                    break
                if change['type'] == 'remove':
                    yield MakeSubscription(GTask)(GTask=None)
                    continue
                else:
                    value = change['new_val']

                value = GTask(**value)
                yield MakeSubscription(GTask)(GTask=value)

        return Observable.from_future(iterable_to_task())



    def resolve_vms(root, info): #temp
        async def iterable_to_vm():
            from rethinkdb import RethinkDB
            r = RethinkDB()

            r.set_loop_type("asyncio")
            db = r.db('vmemperor')
            conn = await r.connect()
            changes = await db.table('vms').changes(include_types=True, include_initial=True).run(conn)
            while True:
                change = await changes.next()
                if not change:
                    break
                if change['type'] == 'remove':
                    value = change['old_val']
                else:
                    value = change['new_val']

                value = GVM(**value)
                yield MakeSubscriptionWithChangeType(GVM)(changeType=change['type'], value=value)

        return Observable.from_future(iterable_to_vm())












schema = Schema(query=QueryRoot, mutation=MutationRoot, types=[GISO, GVDI], subscription=SubscriptionRoot)