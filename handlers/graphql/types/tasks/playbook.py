from enum import Enum

import graphene

from handlers.graphql.types.dicttype import ObjectType, GrapheneTaskList

class PlaybookTaskState(graphene.Enum):
    Preparing = 'preparing'
    ConfigurationWarning = 'configuration_warning' # this state is raised when we can't connect to one of VMs due to misconfiguration
    Error = 'error'
    Running = 'running'
    Finished = 'finished'
    Unknown = 'unknown'


class PlaybookTask(ObjectType):
    id = graphene.Field(graphene.ID, required=True, description="Playbook task ID")
    playbook_id = graphene.Field(graphene.ID, required=True, description="Playbook ID")
    state = graphene.Field(PlaybookTaskState, required=True, description="Playbook running state")
    message = graphene.Field(graphene.String, required=True, description="Human-readable message: error description or return code")

class PlaybookTaskList(GrapheneTaskList):

    @property
    def table_name(self):
        return 'tasks_playbooks'

    @property
    def task_type(self):
        return PlaybookTask