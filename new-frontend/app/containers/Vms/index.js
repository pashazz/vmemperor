/**
 *
 * Vms
 *
 */

import NextTable from 'react-bootstrap-table-next';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter'
import React from 'react';
import uuid from 'uuid/v4';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector } from 'reselect';
import { compose } from 'redux';
import { actions as toastrActions} from 'react-redux-toastr';
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


import {vm_delete, run, halt, vm_select, vm_deselect, vm_select_all, vm_deselect_all} from "./actions";


export class Vms extends React.Component { // eslint-disable-line react/prefer-stateless-function
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
      message: names.join('\n')
    }
  }
  onTableRun()
  {
    const names = this.props.table_selection_halted.map(uuid => this.props.vm_data_names.get(uuid));
  //  this.doTableAction(this.state.selectedHalted, run);
    const options = this.notificationOptions('Starting VMs', names);
    this.props.addToastr(options);
    this.props.table_selection_halted.forEach(uuid => this.props.run(uuid, options.id));

  }

  onTableHalt()
  {
    const names = this.props.table_selection_running.map(uuid => this.props.vm_data_names.get(uuid));
    const options = this.notificationOptions('Stopping VMs', names);
    this.props.addToastr(options);
    this.props.table_selection_running.forEach(uuid => this.props.halt(uuid, options.id));
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
          style={tableStyle}
          striped
          hover/>
      </React.Fragment>);

  }



}


Vms.propTypes = {
  vm_data_table: PropTypes.array.isRequired, //Data for VM table
  vm_data_names: ITypes.mapOf( //Key-valued data about VMs taken directly from store
    PropTypes.string,
    PropTypes.string,
  ),
  table_selection: PropTypes.array.isRequired,
  table_selection_halted: PropTypes.array.isRequired,
  table_selection_running: PropTypes.array.isRequired,
  run: PropTypes.func.isRequired,
  halt: PropTypes.func.isRequired,
  vm_delete: PropTypes.func.isRequired,
  vm_select: PropTypes.func.isRequired,
  vm_deselect: PropTypes.func.isRequired,
  vm_select_all: PropTypes.func.isRequired,
  vm_deselect_all: PropTypes.func.isRequired,
  start_button_disabled: PropTypes.bool.isRequired,
  stop_button_disabled: PropTypes.bool.isRequired,
  trash_button_disabled: PropTypes.bool.isRequired,
  addToastr: PropTypes.func.isRequired,
  removeToastr: PropTypes.func.isRequired,
};

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
   withReducer,
   withSaga,
  withConnect,
)(Vms);
