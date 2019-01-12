/**
 *
 * ControlledTable
 *
 */

import React from 'react';
import T from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector, createSelector } from 'reselect';
import { compose } from 'redux';
import { Set } from 'immutable';
import BootstrapTable from 'react-bootstrap-table-next';
import injectSaga from 'utils/injectSaga';
import injectReducer from 'utils/injectReducer';
import messages from './messages';
//import filterFactory from 'react-bootstrap-table2-filter'
export function constants (key)
{
  return {
    //Constants
  TABLE_SELECT: key + "_SELECT",
  TABLE_DESELECT: key + "_DESELECT",
  TABLE_SELECT_ALL: key + "_SELECT_ALL",
  TABLE_DESELECT_ALL: key + "_DESELECT_ALL"
  }
}

export function actions(key)
{
  const {TABLE_SELECT, TABLE_DESELECT, TABLE_SELECT_ALL, TABLE_DESELECT_ALL} = constants(key);
  return {
    select: (row) => ({
      type: TABLE_SELECT,
        row
    }),
    deselect: (row) => ({
      type: TABLE_DESELECT,
      row
    }),
    select_all: (rows) => ({
      type: TABLE_SELECT_ALL,
        rows,
    }),
    deselect_all: (rows) => ({
      type: TABLE_DESELECT_ALL,
        rows,
    }),
  }
}

//Selectors
export function selectors (key){
  const selectTableData = (state) => state.get(key);
  return {
    makeSelectionSelector: () => createSelector(
      selectTableData,
      (substate) =>
      {
        if (substate) {
          return substate.toSeq().toArray();
        }
        else {
          return []
        }

      }),

  }
}



export default function (key) {
const {TABLE_SELECT, TABLE_DESELECT, TABLE_SELECT_ALL, TABLE_DESELECT_ALL} = constants(key);
//Reducer
  const reducer = (state = Set(), action) =>
  {
    switch (action.type)
    {

      case TABLE_SELECT:
        return state.add(action.row);
      case TABLE_DESELECT:
        return state.delete(action.row);
      case TABLE_SELECT_ALL:
        return Set(action.row);
      case TABLE_DESELECT_ALL:
        return Set();
      default:
        return state;
    }

  };




  class ControlledTable extends React.Component { // eslint-disable-line react/prefer-stateless-function
    constructor(props) {
      super(props);
      this.onSelect = this.onSelect.bind(this);
      this.onSelectAll = this.onSelectAll.bind(this);
      this.onDoubleClick = this.onDoubleClick.bind(this);
    }

    onSelect(row, isSelect)
    {
      const {keyField, select, deselect} = this.props;
      if (isSelect) {
        select(row[keyField]);
      }
      else {
        deselect(row[keyField]);   
      }

    }

    onSelectAll(isSelect, rows)
    {
      const {keyField, select_all, deselect_all} = this.props;
      if (isSelect) {
        select_all(rows.map(row => row[keyField]))
      }
      else {
        deselect_all(rows.map(row => row[keyField]))
      }

    }

    onDoubleClick(e, row, rowIndex)
    {
      if (this.props.onDoubleClick)
      {
        this.props.onDoubleClick(row[keyField]);
      }
    }
/*
    getSnapshotBeforeUpdate(prevProps, prevState){
      console.log("GetSnapshotBeforeUpdate");
    }

    componentDidUpdate(prevProps, prevState)
    {
      console.log("Component did update");
      const {data, keyField} = this.props;
      if (data === prevProps.data)
        return;
      for (const oldItem of prevProps.data)
      {
        if (!data.filter(item => item[keyField] === oldItem[keyField]))
        {
          this.props.deselect(oldItem[keyField]);
        }
      }
    }
    */
    componentDidMount()
    { //Deselect all deleted items
      this.props.table_selection.filter(key => !this.props.data.filter(item => key === item[this.props.keyField]).length).forEach(key =>
        {
          this.props.deselect(key);
        }
      );
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
        <div>
          <BootstrapTable
            columns={this.props.columns}
            data={this.props.data}
            rowEvents={rowEvents}
            selectRow={selectRow}
            keyField={this.props.keyField}
          />
        </div>
      );
    }
  }

  ControlledTable.propTypes = {
//    dispatch: PropTypes.func.isRequired,
    columns: T.array.isRequired,
    data: T.array.isRequired,
    keyField: T.string.isRequired,
    select: T.func.isRequired,
    deselect: T.func.isRequired,
    select_all: T.func.isRequired

  };

  const mapStateToProps = createStructuredSelector({
    table_selection: selectors(key).makeSelectionSelector()
  });

  function mapDispatchToProps(dispatch) {
    const _actions = actions(key);
    return {
      select: (row) => dispatch(_actions.select(row)),
      deselect: (row) => dispatch(_actions.deselect(row)),
      select_all: (rows) => dispatch(_actions.select_all(rows)),
      deselect_all: (rows) => dispatch(_actions.deselect_all(rows)),
    };
  }


  const withConnect = connect(mapStateToProps, mapDispatchToProps);

  const withReducer = injectReducer({key: key, reducer});
  //const withSaga = injectSaga({key: key, saga});
  return compose(
    withReducer,
//    withSaga,
    withConnect,
  )(ControlledTable);
}

