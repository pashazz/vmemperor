import React from 'react';
import {useSubscription} from "../../hooks/subscription";
import {
  Change,
  VmList,
  VmListFragment,
  VmListUpdate,
  VmTableSelect,
  VmTableSelectAll,
  VmTableSelection,
  ShutdownVm, VmStateForButtonToolbar, StartVm, DeleteVm
} from '../../generated-models';
import StatefulTable, {ColumnType} from "../StatefulTable";
import {RouteComponentProps} from "react-router";
import filterFactory, {textFilter} from 'react-bootstrap-table2-filter'
import tableStyle from "./table.css";
import {useMutation, useQuery} from "react-apollo-hooks";

import {ButtonGroup, ButtonToolbar} from "reactstrap";
import {dataIdFromObject} from "../../../cacheUtils";
import StartButton from "../../components/StartButton";
import StopButton from "../../components/StopButton";
import RecycleBinButton from "../../components/RecycleBinButton";

function nameFormatter(column, colIndex, {sortElement, filterElement })
{
  return (
    <div style={ { display: 'flex', flexDirection: 'column' } }>
      { column.text }
      { filterElement }
      { sortElement }
    </div>
  );
}
function plainFormatter(column, colIndex, {sortElement, filterElement})
{
  return (
    <div style={ { display: 'flex', flexDirection: 'column' } }>
      { column.text }
      { filterElement }
      { sortElement }
    </div>
  );
}

type VmColumnType = ColumnType<VmList.Vms>;

const columns : VmColumnType[] = [
  {
    dataField: 'nameLabel' ,
    text: 'Name',
    filter: textFilter(),
    headerFormatter: nameFormatter,
    headerClasses: 'align-self-baseline'

  },
  {
    dataField: "powerState",
    text: 'Status',
    headerFormatter: plainFormatter,
    headerClasses: 'align-self-baseline'

  }
];


function  rowClasses(row: VmList.Vms, rowIndex)
{
  switch (row.powerState)
  {
    case 'Halted':
      return 'table-danger';
    case 'Running':
      return 'table-success';
    default:
      return "";
  }
}

export default function ({history}:  RouteComponentProps) {
  const {
    data: { vms },
  } = useQuery<VmList.Query>(VmList.Document);

  useSubscription<VmListUpdate.Subscription>(VmListUpdate.Document,
    {
      onSubscriptionData ({client, subscriptionData}) {
        const change = subscriptionData.vms;
        switch (change.changeType) {
          case Change.Add:
          case Change.Change:
            client.writeFragment<VmListFragment.Fragment>({
              id: dataIdFromObject(change.value),
              fragment: VmListFragment.FragmentDoc,
              data: change.value
            });
            break;
          case Change.Remove:
            console.log("Removal of value: ", change.value.uuid);
            const query = client.readQuery<VmList.Query>({
              query: VmList.Document
            });
            const newQuery: typeof query = {
              ...query,
              vms: query.vms.filter(vm => vm.uuid !== change.value.uuid)
            };
            client.writeQuery<VmList.Query>({
              query: VmList.Document,
              data: newQuery
            });
            break;
          default:
            break;
        }
      }
    });


  const { data : { vmSelectedReadyFor } }
      = useQuery<VmStateForButtonToolbar.Query>(VmStateForButtonToolbar.Document);


  const startVm = useMutation<StartVm.Mutation, StartVm.Variables>(
    StartVm.Document);
  const onStartVm =  ()  => {
    console.log("Staring...", vmSelectedReadyFor.start);
    for (const id of vmSelectedReadyFor.start) {
      startVm({
        variables: {
          uuid: id
        },
        refetchQueries: [{query: VmStateForButtonToolbar.Document}]
      });

    }
  }

  const onStopVm = () => {

    for (const id of vmSelectedReadyFor.stop) {
      console.log("Stopping...",id);
      const execute = useMutation<ShutdownVm.Mutation, ShutdownVm.Variables>(
        ShutdownVm.Document,
        {
          variables: {
            uuid: id
          },
          refetchQueries : [{ query: VmStateForButtonToolbar.Document }]
        }
      );
      execute();
    }
  };

  const onDeleteVm = () => {
    for (const id of vmSelectedReadyFor.trash) {
      const execute = useMutation<DeleteVm.Mutation, DeleteVm.Variables>(
        DeleteVm.Document,
        {
          variables: {
            uuid: id
          },
          refetchQueries : [{ query: VmStateForButtonToolbar.Document }]

        }
      );
      execute();
    }
  };


  return(
    <React.Fragment>
       <ButtonToolbar>
        <ButtonGroup size="lg">
          <StartButton
            onClick={onStartVm}
            disabled={!vmSelectedReadyFor.start}/>

          <StopButton
            onClick={onStopVm}
            disabled={!vmSelectedReadyFor.stop}/>

        </ButtonGroup>
        <ButtonGroup className="ml-auto">
          <RecycleBinButton
            onClick={onDeleteVm}
            disabled={!vmSelectedReadyFor.trash}/>
        </ButtonGroup>
      </ButtonToolbar>
      <StatefulTable
        keyField="uuid"
        refetchQueriesOnSelect={
          [
            {
              query: VmStateForButtonToolbar.Document
            }
          ]
        }
        data={vms}
        tableSelectOne={VmTableSelect.Document}
        tableSelectMany={VmTableSelectAll.Document}
        tableSelectionQuery={VmTableSelection.Document}
        columns={columns}

        props={
          {
            filter: filterFactory(),
            style: tableStyle,
            noDataIndication: "No VMs available... create something new!",
            striped: true,
            hover: true,
            rowClasses,
                                }
        }
      onDoubleClick={(row) => {console.log("double clicked on row!")}}/>
    </React.Fragment>)




}
