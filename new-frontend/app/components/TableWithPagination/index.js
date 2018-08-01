import React, {PureComponent} from 'react';
import  NextTable from 'react-bootstrap-table-next';
import paginationFactory from 'react-bootstrap-table2-paginator';
import T from 'prop-types';


export default class TableWithPagination extends PureComponent
{
  static propTypes =
    {
      fetcher: T.func.isRequired,
      noData: T.func,
      sizePerPage: T.number.isRequired,
      columns: T.arrayOf(
        T.shape({
          dataField: T.string.isRequired,
          text: T.string.isRequired,
          formatter: T.func,
        })
      ),
      rowFilter: T.func,
      caption: T.any,
    };
  constructor(props)
  {
    super(props);
    this.state =
      {
        items: [],
        page: 1,
      };
    this.fetch = this.fetch.bind(this);
    this.handlePageChange = this.handlePageChange.bind(this);
    this.handleSizePerPageChange = this.handleSizePerPageChange.bind(this);
  }

  fetch(page = this.state.page, sizePerPage = this.props.sizePerPage)
  {
    this.props.fetcher(page, sizePerPage).then(
      data => {
        this.setState({items:
            this.props.rowFilter ? data.filter(this.props.rowFilter) : data,
          page, sizePerPage});
      });


  }

  componentDidMount()
  {
    this.fetch();
  }

  handlePageChange(type, {page, sizePerPage}) {
    this.fetch(page,sizePerPage);
  }

  handleSizePerPageChange(sizePerPage) {
    // When changing the size per page always navigating to the first page
    this.fetch(1, sizePerPage);
  }

  render() {
    const { page } = this.state;
    const { sizePerPage } = this.props;
    const totalSize = this.state.items.length;
    return (
      <NextTable
        remote
        keyField="uuid"
        data={this.state.items}
        columns={this.props.columns}
        pagination={paginationFactory(page, sizePerPage, totalSize)}
        onTableChange={this.handlePageChange}
        caption={this.props.caption}
        noDataIndication={this.props.noData}
        />
    );
  }
}
