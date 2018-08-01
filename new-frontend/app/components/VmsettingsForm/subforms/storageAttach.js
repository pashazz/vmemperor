import T from 'prop-types';
import TableWithPagination from 'components/TableWithPagination';

import {vdilist} from "../../../api/vdi";
import {vminfo} from 'api/vm';

import React, {PureComponent } from 'react';
import {sizeFormatter} from "../../../utils/sizeFormatter";
import Promise from 'bluebird';

const myFetcher = async(page, sizePerPage) =>
{
  const list = await vdilist(page, sizePerPage);
  return await Promise.map(list.data, async(record) => {
    const {VMs, ...rest} = record;
    rest.VMs = await Promise.map(VMs, async(uuid) =>
    {
      return await vminfo(uuid).data;

    });
    return rest;
  } );
};


function vmFormatter(cell, row)
{
  return (
    <div>
      {cell.map(vm => {return <p>{vm.name_label}</p>})}
    </div>
  );
}

const columns = [
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
  {
    dataField: 'VMs',
    text: 'Connected to',
    formatter: vmFormatter
  },

];

class StorageAttach extends PureComponent
{
  static propTypes = {
    uuid: T.string.isRequired,
    caption: T.string.isRequired,
  };

  constructor(props)
  {
    super(props);
    this.rowFilter = this.rowFilter.bind(this);

  }

  rowFilter(row)
  {
    try {
      return row.VMs.filter(vm => vm.uuid === uuid).length > 0;
    }
    catch (e) {
      console.warn("Exception in rowFilter:", e);
      return false;
    }
  }



  render()
  {
    return (<TableWithPagination
      fetcher={myFetcher}
      sizePerPage={10}
      columns={columns}
      rowFilter={this.rowFilter}
      noData={() =>  "No disks available for attaching"}
      />)
  }

}

export default StorageAttach;
