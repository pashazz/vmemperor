/**
 *
 * ControlledTable
 *
 */

import React, {Key} from 'react';
import T from 'prop-types';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { createStructuredSelector, createSelector } from 'reselect';
import { compose } from 'redux';
import { Set } from 'immutable';
import BootstrapTable from 'react-bootstrap-table-next';
//import injectSaga from 'utils/injectSaga';
import injectReducer from '../../utils/injectReducer';
import messages from './messages';
//import filterFactory from 'react-bootstrap-table2-filter'

export interface ColumnType<T> {
  dataField: string;
  text: string;
  sort?: boolean;
  formatter: (cell: any, row: T) => JSX.Element;
}


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

  interface InjectedProps<KeyType>{
    select : (arg0: KeyType) => any;
    deselect: (arg0 : KeyType) => any;
    select_all : (arg0 : KeyType[]) => any;
    deselect_all: (arg0: KeyType[]) => any;

  }


  interface Props<KeyType, T> extends InjectedProps<KeyType>{
    keyField : string; //what field to use as key. Key of type KeyType
    onDoubleClick? : (key : KeyType) => any; //What to do on double click
    data: T[]; //Data provided to table
    table_selection: KeyType[];
    columns: ColumnType<T>[];

  }


  class ControlledTable<T> extends React.Component<Props<string, T>> { // eslint-disable-line react/prefer-stateless-function
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
        const {keyField} = this.props;
        this.props.onDoubleClick(row[keyField]);
      }
    }

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
            bootstrap4
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

