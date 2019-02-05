import React from 'react';
import {useSubscription} from "../../hooks/subscription";
import {
  Change,
  VmList,
  VmListFragment,
  VmListUpdate, VmSelectedReadyFor,
  VmTableSelect,
  VmTableSelectAll,
  VmTableSelection
} from '../../generated-models';
import StatefulTable, {ColumnType} from "../StatefulTable";
import {RouteComponentProps} from "react-router";
import filterFactory, {textFilter} from 'react-bootstrap-table2-filter'
import tableStyle from "./table.css";
import {useQuery} from "react-apollo-hooks";
import ButtonToolbar from "reactstrap/lib/ButtonToolbar";
import {ButtonGroup} from "reactstrap";
import {dataIdFromObject} from "../../../cacheUtils";
import query from "apollo-cache-inmemory/lib/fragmentMatcherIntrospectionQuery";
import VmSelectedReadyFor = VmSelectedReadyFor.VmSelectedReadyFor;

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

  const d = useQuery<VmSelectedReadyFor.Query,


  return(
    <React.Fragment>
      <ButtonToolbar>
        <ButtonGroup size="lg">
          <StartButton
            onClick={this.onTableRun}
            disabled={this.props.start_button_disabled}/>

          <StopButton
            onClick={this.onTableHalt}
            disabled={this.props.stop_button_disabled}/>

        </ButtonGroup>
        <ButtonGroup className="ml-auto">
          <RecycleBinButton
            onClick={this.onTableDelete}
            disabled={this.props.trash_button_disabled}/> */}
        </ButtonGroup>
      </ButtonToolbar>
      <StatefulTable
        keyField="uuid"
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
