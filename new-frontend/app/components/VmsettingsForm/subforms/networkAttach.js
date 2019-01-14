import React, { PureComponent } from 'react';
import T from 'prop-types';
import TableWithPagination from 'components/TableWithPagination';

const columns = [
  {
    dataField: 'name_label',
    text: 'Name',
  },
  {
    dataField: 'name_description',
    text: 'Description',
  },

];

class NetworkAttach extends PureComponent
{
  static propTypes = {
    fetch: T.func.isRequired,
    onAttach: T.func.isRequired,
    data: T.array.isRequired,
  };
  constructor(props)
  {
    super(props);
    this.onDoubleClick = this.onDoubleClick.bind(this);
  }



  onDoubleClick(row)
  {
    this.props.onAttach(row.uuid);
  }

  render()
  {
    return(
      <div>
        <TableWithPagination
          fetcher={this.props.fetch}
          data={this.props.data}
          sizePerPage={10}
          columns={columns}
          onDoubleClick={this.onDoubleClick}
          />
      </div>
    )
  }
}

export default NetworkAttach;
