/**
 *
 * StatefulTable
 *
 */

import React, {Key} from 'react';
import { FormattedMessage } from 'react-intl';
import BootstrapTable from 'react-bootstrap-table-next';

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

export type SelectOneVariablesArgs = {
  item: string;
  isSelect: boolean;
}
export type SelectManyVariablesArgs = {
  items: string[];
  isSelect: boolean;
}

export type SelectionResponse = {
  items: string[];
}



export type TableSelectOneMutation = React.ComponentType<Partial<MutationProps<SelectionResponse, SelectOneVariablesArgs>>>;

export type TableSelectManyMutation = React.ComponentType<Partial<MutationProps<SelectionResponse, SelectManyVariablesArgs>>>


interface Props<T>{
  keyField : keyof T; //what field to use as key. Key of type KeyType
  data: T[]; //Data provided to table
  tableSelectOne: TableSelectOneMutation;
  tableSelectMany: TableSelectManyMutation;
  tableSelection: KeyType[];
  columns: ColumnType<T>[];
  props: any;
  onDoubleClick: (key: string) => any;
}



  class StatefulTable<T> extends React.Component<Props<T>> {
    static readonly defaultProps = {
      props: {},
      onDoubleClick: null,
    };
    deselect : (key) => any = null;
    constructor(props) {
      super(props);
      this.onDoubleClick = this.onDoubleClick.bind(this);
      this.deselect = null;
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
      if (!this.deselect)
        return;

      this.props.tableSelection.filter(key => !this.props.data.filter(
        //@ts-ignore
        item => key === item[this.props.keyField]).length).forEach(key =>
        {
          this.deselect(key);
        }
      );
    }

    render() {
      const rowEvents = {
      onDoubleClick: this.onDoubleClick,
    };
      const SelectOne = this.props.tableSelectOne;
      const SelectMany = this.props.tableSelectMany;

      return (
        <div>
          <SelectOne>
            { selectOne => (
               <SelectMany>
                  {selectMany => {
                    this.deselect = (item) => { //For componentDidMount deletion
                      selectOne({
                        variables: {
                          isSelect: false,
                          item
                        }
                      });
                    };
                    const onSelect = (row, isSelect) => {
                      selectOne({ variables:
                          {
                            isSelect,
                            item: row[this.props.keyField],
                          }
                      });
                    };

                    const onSelectAll = (isSelect, rows) => {
                      selectMany( {
                        variables: {
                          isSelect,
                          items: rows.map(row=> row[this.props.keyField])
                        }
                      });
                    };
                    const selectRow = {
                      mode: 'checkbox',
                      clickToSelect: false,
                      bgColor: 'aqua',
                      selected: this.props.tableSelection,
                      onSelect,
                      onSelectAll,
                    };
                    return (<BootstrapTable
                        bootstrap4
                        columns={this.props.columns}
                        data={this.props.data}
                        rowEvents={rowEvents}
                        selectRow={selectRow}
                        keyField={this.props.keyField}
                        {...this.props.props}
                      />
                    )
                  }
                  }
              </SelectMany>
              )
            }
              </SelectOne>
        </div>
      );
    }
  }
export default StatefulTable;
