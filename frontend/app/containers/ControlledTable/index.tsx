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
import messages from './messages';
import {
  Query,
  Mutation,
  MutationFn,
  graphql,
  ChildDataProps,
  NamedProps,
  QueryProps,
  MutationProps
} from 'react-apollo';
import {VmTableSelection} from "../../generated-models";



//import filterFactory from 'react-bootstrap-table2-filter'

interface HeaderFormatterComponents {
  sortElement?: JSX.Element;
  filterElement?: JSX.Element;

}
export interface ColumnType<T> {
  dataField: keyof T,
  text: string;
  sort?: boolean;
  formatter?: (cell: T[keyof T], row: T) => JSX.Element | string;
  headerFormatter?: (column : ColumnType<T>, colIndex: number, components: HeaderFormatterComponents) => JSX.Element | string;
  filter?: object;
  headerClasses: ((column: ColumnType<T>, colIndex: number) => string) | string;
}




export interface SelectOneVariablesArgs {
  item: string,
  isSelect: boolean
}
export interface SelectManyVariablesArgs {
  items: string[],
  isSelect: boolean
}

export interface SelectionResponse  {
  items: string[],
}


type ChildProps = ChildDataProps<{}, SelectionResponse>

export type TableSelectOneMutation = MutationFn<any,SelectOneVariablesArgs>;
export type TableSelectManyMutation = MutationFn<any, SelectManyVariablesArgs>;

const defaultProps = {
  props: {} as {[name: string]: any},
  onDoubleClick: null as  (key : any) => any, //What to do on double click
};

type DefaultProps = typeof defaultProps;



  interface IProps<KeyType, T>  {
    keyField : keyof T; //what field to use as key. Key of type KeyType
    data: T[]; //Data provided to table
    tableSelectOne: TableSelectOneMutation;
    tableSelectMany: TableSelectManyMutation;
    tableSelection: KeyType[];
    columns: ColumnType<T>[];

  }

  type Props<T> = IProps<string, T> & Partial<DefaultProps>;


  class ControlledTable<T> extends React.Component<Props<T>> { // eslint-disable-line react/prefer-stateless-function
    static readonly defaultProps = defaultProps;
    constructor(props) {
      super(props);
      this.onDoubleClick = this.onDoubleClick.bind(this);
      this.onSelect = this.onSelect.bind(this);
      this.onSelectAll = this.onSelectAll.bind(this);
    }

    onDoubleClick(e, row, rowIndex)
    {
      if (this.props.onDoubleClick)
      {
        const {keyField} = this.props;
        this.props.onDoubleClick(row[keyField]);

      }
    }

    onSelect(row, isSelect) {
      this.props.tableSelectOne({
        variables: {
          isSelect,
          item: row[this.props.keyField]
        }
      });
    }

    onSelectAll(isSelect, rows) {
      this.props.tableSelectMany( {
        variables: {
          isSelect,
          items: rows.map(row=> row[this.props.keyField])
        }
      });
    }

    componentDidMount()
    { //Deselect all deleted items
      this.props.tableSelection.filter(key => !this.props.data.filter(
        item => key === item[this.props.keyField]).length).forEach(key =>
        {
          //this.props.tableSelectOne(key);
          this.props.tableSelectOne({
            variables: {
              isSelect: false,
              item: key,
            }
          });
        }
      );
    }

    render() {
      const selectRow = {
      mode: 'checkbox',
      clickToSelect: false,
      bgColor: 'aqua',
      selected: this.props.tableSelection,
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
            {...this.props.props}
          />
        </div>
      );
    }
  }



  //const withSaga = injectSaga({key: key, saga});
export default ControlledTable;
