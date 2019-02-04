import React from 'react';
import {useQuery2} from "../../hooks/subscription";
import {Change, VmList, VmListUpdate, VmTableSelect, VmTableSelectAll, VmTableSelection} from '../../generated-models';
import StatefulTable, {ColumnType} from "../StatefulTable";
import {RouteComponentProps} from "react-router";
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter'
import tableStyle from "./table.css";
import {useQuery} from "react-apollo-hooks";

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


function  rowClasses(row, rowIndex)
{
  switch (row.power_state)
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

  /*useSubscribeToMore<VmListUpdate.Subscription>(VmListUpdate.Document, {
    updateQuery: (previousQueryResult, { subscriptionData}) => {
      console.log("Updating query! ", subscriptionData.data.vms);
      const change = subscriptionData.data.vms;
      switch (change.changeType) {
        case Change.Remove:
              return {...previousQueryResult,
              vms: previousQueryResult.vms.filter(vm => vm.uuid !== change.value.uuid)
              };

        case Change.Add:
              return {...previousQueryResult,
                vms: [...previousQueryResult.vms, change.value]
              };
        case Change.Change:
              return {...previousQueryResult,
              vms: previousQueryResult.vms.map(vm =>
              {
                if (vm.uuid === change.value.uuid)
                {
                  return change.value;
                }
                else
                {
                  return vm;
                }
              })};
        default:
          return previousQueryResult;
      }
    }

  });

*/
  return(
    <React.Fragment>
      {/*<ButtonToolbar>
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
            disabled={this.props.trash_button_disabled}/>
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
      */}
    </React.Fragment>)




}
