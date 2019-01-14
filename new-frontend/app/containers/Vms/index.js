/**
 *
 * Vms
 *
 */

import NextTable from 'react-bootstrap-table-next';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter'
import React from 'react';
import uuid from 'uuid/v4';
import T from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';
import { actions as toastrActions} from 'react-redux-toastr';
import { withRouter } from 'react-router-dom';



import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import {
  makeSelectVmDataForTable, makeSelectSelection, makeSelectSelectionRunning, makeSelectSelectionHalted,
  makeStartButtonDisabled, makeStopButtonDisabled, makeTrashButtonDisabled, makeSelectVmDataNames
} from "./selectors";
import reducer from './reducer';
import saga from './saga';
import messages from './messages';
import { Server } from 'mock-socket';
import axios from 'axios';
import {ButtonGroup, Button, ButtonToolbar} from 'reactstrap';
import StartButton from 'components/StartButton';
import StopButton from 'components/StopButton';
import RecycleBinButton from 'components/RecycleBinButton';
import ITypes from 'react-immutable-proptypes';
import { css } from 'emotion';
import styled from 'styled-components';
import tableStyle from "./table.css";
import {VMRecord} from "./type";



import {vm_select, vm_deselect, vm_select_all, vm_deselect_all} from "./actions";
import {vm_delete, run, halt } from 'containers/App/actions';


export class Vms extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    vm_data_table: T.arrayOf(T.shape(
      {
        power_state: T.string.isRequired,
        name_label: T.string.isRequired,
        start_time: T.any.isRequired,
        uuid: T.string.isRequired.isRequired
      })),
    vm_data_names: ITypes.mapOf( //Key-valued data about VMs taken directly from store
      T.string,
      T.string,
    ),
    table_selection: T.array.isRequired,
    table_selection_halted: T.array.isRequired,
    table_selection_running: T.array.isRequired,
    run: T.func.isRequired,
    halt: T.func.isRequired,
    vm_delete: T.func.isRequired,
    vm_select: T.func.isRequired,
    vm_deselect: T.func.isRequired,
    vm_select_all: T.func.isRequired,
    vm_deselect_all: T.func.isRequired,
    start_button_disabled: T.bool.isRequired,
    stop_button_disabled: T.bool.isRequired,
    trash_button_disabled: T.bool.isRequired,
    addToastr: T.func.isRequired,
    removeToastr: T.func.isRequired,
    history: T.shape(
      {
        push : T.func.isRequired,
      }).isRequired,

  };

  constructor(props) {
    super(props);
    this.render = this.render.bind(this);
    this.nameFormatter = this.nameFormatter.bind(this);
    this.plainFormatter = this.plainFormatter.bind(this);
    this.rowClasses = this.rowClasses.bind(this);
    this.onSelect = this.onSelect.bind(this);
    this.onSelectAll = this.onSelectAll.bind(this);
    this.onTableRun = this.onTableRun.bind(this);
    this.onTableHalt = this.onTableHalt.bind(this);
    this.onTableDelete = this.onTableDelete.bind(this);
    this.onDoubleClick = this.onDoubleClick.bind(this);
  }


  columns = [
    {
      dataField: 'name_label',
      text: 'Name',
      filter: textFilter(),
      headerFormatter: this.nameFormatter,
      headerClasses: 'align-self-baseline'

    },
    {
      dataField: "power_state",
      text: 'Status',
      headerFormatter: this.plainFormatter,
      headerClasses: 'align-self-baseline'

    }
  ];



  nameFormatter(column, colIndex, {sortElement, filterElement })
  {
    return (
      <div style={ { display: 'flex', flexDirection: 'column' } }>
        { column.text }
        { filterElement }
        { sortElement }
      </div>
    );
  }
  plainFormatter(column, colIndex, {sortElement, filterElement})
  {
    return (
    <div style={ { display: 'flex', flexDirection: 'column' } }>
      { column.text }
      { filterElement }
      { sortElement }
    </div>
  );
  }

  rowClasses(row, rowIndex)
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



  onSelect(row, isSelect)
  {
    if (isSelect) {
      this.props.vm_select(row.uuid);
    }
    else {
      this.props.vm_deselect(row.uuid);
    }

  }

  onSelectAll(isSelect, rows)
  {
    if (isSelect)
    {
      this.props.vm_select_all(rows.map(row => row.uuid));
    }
    else
    {
      this.props.vm_deselect_all(rows.map(row => row.uuid));
    }
  }

  notificationOptions(title, names)
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
    const { history } = this.props;
    const { uuid } = this.props.vm_data_table.filter(item => item.uuid === row.uuid)[0];
    history.push('/vmsettings/' + uuid);
  }

  render() {
    const selectRow = {
      mode: 'checkbox',
      clickToSelect: true,
      bgColor: 'aqua',
      selected: this.props.table_selection,
      onSelect: this.onSelect,
      onSelectAll: this.onSelectAll

    };

    const rowEvents = {
      onDoubleClick: this.onDoubleClick,
    };
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
        <NextTable
          columns={this.columns}
          filter={filterFactory()}
          data = {this.props.vm_data_table}
          keyField='uuid'
          selectRow={selectRow}
          rowClasses={this.rowClasses}
          rowEvents={rowEvents}
          style={tableStyle}
          noDataIndication="No VMs available... create something new!"
          striped
          hover/>
      </React.Fragment>);

  }
}




const mapStateToProps = createStructuredSelector({
  vm_data_table: makeSelectVmDataForTable(),
  vm_data_names: makeSelectVmDataNames(),
  table_selection: makeSelectSelection(),
  table_selection_running: makeSelectSelectionRunning(),
  table_selection_halted: makeSelectSelectionHalted(),
  start_button_disabled: makeStartButtonDisabled(),
  stop_button_disabled: makeStopButtonDisabled(),
  trash_button_disabled: makeTrashButtonDisabled(),

});

const mapDispatchToProps = {
  run,
  halt,
  vm_delete,
  vm_select,
  vm_deselect,
  vm_select_all,
  vm_deselect_all,
  addToastr: toastrActions.add,
  removeToastr: toastrActions.remove,
};

const withConnect = connect(mapStateToProps, mapDispatchToProps);

const withSaga = injectSaga({ key: 'vms', saga });
const withReducer = injectReducer({key: 'vms', reducer});

export default compose(
   withRouter,
   withReducer,
   withSaga,
  withConnect,
)(Vms);
