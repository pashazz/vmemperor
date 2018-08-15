import T from 'prop-types';
import TableWithPagination from 'components/TableWithPagination';
import {Button, ButtonGroup} from 'reactstrap';


import {vminfo} from 'api/vm';

import React, {PureComponent } from 'react';
import {sizeFormatter} from "../../../utils/formatters";


function vmFormatter(cell, row)
{
  return (
    <div>
      {cell.map(vm => {return <div>{vm.name_label}</div>})}
    </div>
  );
}

class StorageAttach extends PureComponent
{
  static propTypes = {
    uuid: T.string,
    caption: T.string.isRequired,
    fetch: T.func.isRequired,
    onAttach: T.func.isRequired,
    showConnectedTo: T.bool.isRequired
  };

  constructor(props)
  {
    super(props);
   // this.rowFilter = this.rowFilter.bind(this);
    this.render = this.render.bind(this);
    this.onDoubleClick = this.onDoubleClick.bind(this);

    this.state = {
      columns: [],

    }

  }

  onDoubleClick(row)
  {
    this.props.onAttach(row.uuid);
    this.props.fetch();
  }

  static  getDerivedStateFromProps(props, state)
  {
    let newState = {
      columns: [
        {
          dataField: 'name_label',
          text: 'Name',

        },
        {
          dataField: 'name_description',
          text: 'Description'
        },
        {
          dataField: 'virtual_size',
          text: 'Size',
          formatter: sizeFormatter,
        },

      ],
    };
    if (props.showConnectedTo)
    {
      newState.columns = [...newState.columns, {
        dataField: 'VMs',
        text: 'Connected to',
        formatter: vmFormatter,
    }]
    }
    return newState;
  }
/*
  rowFilter(row)
  {
    const {uuid} = this.props;
    if (!uuid)
      return true;
    try {
      return row.VMs.filter(vm => vm.uuid === uuid).length === 0;
    }
    catch (e) {
      console.warn("Exception in rowFilter:", e);
      return false;
    }
  }
*/




  render()
  {
    return (
      <div>
      <TableWithPagination
      fetcher={this.props.fetch}
      data={this.props.data}
      sizePerPage={10}
      columns={this.state.columns}
      noData={() =>  "No disks available for attaching"}
      actions={this.props.actions}
      onDoubleClick={this.onDoubleClick}
      refresh={this.props.refresh}
      />
      </div>)
  }

}

export default StorageAttach;
