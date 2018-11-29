from graphene_tornado.tornado_graphql_handler import TornadoGraphQLHandler

import graphene

from graphene import ObjectType, Schema

from tornado.escape import to_unicode

from handlers.graphql.types.input.createvm import CreateVM
from handlers.graphql.types.iso import ISO
from handlers.graphql.types.template import Template
from handlers.graphql.types.vm import VM
from handlers.graphql.types.sr import SR
from handlers.graphql.types.network import Network
from handlers.graphql.types.vdi import VDI



class QueryRoot(ObjectType):

    vms = graphene.List(VM, required=True, resolver=VM.all(), description="All VMs available to user")
    vm = graphene.Field(VM, required=True, uuid=graphene.ID(), resolver=VM.one())

    networks = graphene.List(Network, required=True, resolver=Network.all(), description="All Networks available to user")
    network = graphene.Field(Network, required=True, uuid=graphene.ID(), resolver=Network.one(), description="Information about a single network")

    srs = graphene.List(SR, required=True, resolver=SR.all(),
                             description="All Storage repositories available to user")
    sr = graphene.Field(SR, required=True, uuid=graphene.ID(), resolver=SR.one(), description="Information about a single storage repository")


    vdis = graphene.List(VDI,required=True, resolver=VDI.all(), description="All Virtual Disk Images (hard disks), available for user")
    vdi = graphene.Field(VDI, required=True, uuid=graphene.ID(), resolver=VDI.one(), description="Information about a single virtual disk image (hard disk)")

    isos = graphene.List(ISO, required=True, resolver=ISO.all(), description="All ISO images available for user")
    iso = graphene.Field(VDI, required=True, uuid=graphene.ID(), resolver=ISO.one(),
                         description="Information about a single ISO image")

    templates = graphene.List(Template,required=True, resolver=Template.all(), description="All templates")




class MutationRoot(ObjectType):
    create_VM = CreateVM.Field()


schema = Schema(query=QueryRoot, mutation=MutationRoot, types=[ISO, VDI])