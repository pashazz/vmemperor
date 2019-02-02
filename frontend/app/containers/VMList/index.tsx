/**
 *
 * VMList
 *
 */

import filterFactory, { textFilter } from 'react-bootstrap-table2-filter'
import React from 'react';
import uuid from 'uuid/v4';
import { withRouter } from 'react-router-dom';


import messages from './messages';
import { Server } from 'mock-socket';
import {ButtonGroup, Button, ButtonToolbar, Label} from 'reactstrap';
import StartButton from '../../components/StartButton';
import StopButton from '../../components/StopButton';
import RecycleBinButton from '../../components/RecycleBinButton';
import tableStyle from "./table.css";
import {VMRecord} from "./type";




import {VmList, VmTableSelect, VmTableSelectAll, VmTableSelection} from "../../generated-models";
import StatefulTable, {ColumnType} from "../StatefulTable";

type VmColumnType = ColumnType<VmList.Vms>;

const columns : VmColumnType[] = [
  {
    dataField: 'nameLabel' ,
    text: 'Name',
    filter: textFilter(),
    headerFormatter: this.nameFormatter,
    headerClasses: 'align-self-baseline'

  },
  {
    dataField: "powerState",
    text: 'Status',
    headerFormatter: this.plainFormatter,
    headerClasses: 'align-self-baseline'

  }
];



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


function  notificationOptions(title, names)
{
  return {
    id: uuid(),
    type: 'info',
    timeOut: 0,
    title,
    message: names.join('\n'),
    options : {
      showCloseButton: true,

    }
  }
}

export class VMList extends React.Component<RouterP> { // eslint-disable-line react/prefer-stateless-function

  constructor(props) {
    super(props);
    this.render = this.render.bind(this);
    this.onTableRun = this.onTableRun.bind(this);
    this.onTableHalt = this.onTableHalt.bind(this);
    this.onTableDelete = this.onTableDelete.bind(this);
    this.onDoubleClick = this.onDoubleClick.bind(this);
  }


  onTableRun()
  {
    this.props.run(this.props.table_selection_halted);
  }

  onTableHalt()
  {
    this.props.halt(this.props.table_selection_running);
    //forEach(uuid => this.props.halt(uuid, options.id));
  }

  onTableDelete()
  {
    this.props.vm_delete(this.props.table_selection);
  }

  onDoubleClick(e, row, rowIndex)
  {

    e.preventDefault();
    const { history } = this.props;
    const { uuid } = this.props.vm_data_table.filter(item => item.uuid === row.uuid)[0];
    history.push('/vmsettings/' + uuid);
  }


  render() {
    return (

      <React.Fragment>

          {({data, error, loading}) => {
            if (error)
              return (<h1>{error.message}</h1>);
            if (loading)
            {
              return '...';
            }
            return (
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
                      disabled={this.props.trash_button_disabled}/>
                  </ButtonGroup>
                </ButtonToolbar>



                    return (
                              <StatefulTable<VmList.Vms>
                                keyField="uuid"
                                columns={columns}
                                tableSelectOne={vmSelect}
                                tableSelectMany={vmSelectAll}
                                props={{
                                  filter: filterFactory(),
                                  style: tableStyle,
                                  noDataIndication: "No VMs available... create something new!",
                                  striped: true,
                                  hover: true,
                                  rowClasses,
                                }}
                                data={result.data.vms}
                              />
                  }}
                </VmList.Component>
              </React.Fragment>
            );
          }

          }
        </VmTableSelection.Component>
      </React.Fragment>
    );

  }
}


export default withRouter(VMList);
