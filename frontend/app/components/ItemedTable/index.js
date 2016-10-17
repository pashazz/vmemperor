import React, { PropTypes as T } from 'react';
import { FormattedMessage } from 'react-intl';
import { filterItems } from 'utils/filter';
import styles from './styles.css';
import SortImg from './components/SortImg';

const clickWrapper = func => column => {
  if (func) {
    return event => {
      event.preventDefault();
      event.stopPropagation();
      func(column, event.target.value);
    };
  }
  return null;
};

function sortClass(column, sort) {
  const ascOrDesc = sort.order === 'asc' ? styles.headerSortAsc : styles.headerSortDesc;
  return sort.column === column ? ascOrDesc : '';
}

function sortFunction(first, second, { order, column }) {
  const multiplier = order === 'asc' ? 1 : -1;
  const firstVal = (first[column]() || '').toLowerCase();
  const secondVal = (second[column]() || '').toLowerCase();
  if (firstVal === secondVal) {
    return 0;
  }
  return firstVal < secondVal ? multiplier * -1 : multiplier;
}

class ItemedTable extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    list: T.any.isRequired,
    filters: T.any.isRequired,
    sort: T.any,
    onFilter: T.oneOfType([
      T.func, T.bool,
    ]).isRequired,
    onSort: T.oneOfType([
      T.func, T.bool,
    ]).isRequired,
    itemActions: T.object.isRequired,
    itemMessages: T.object.isRequired,
    ItemComponent: T.any.isRequired,
  }

  static defaultProps = {
    onFilter: false,
    onSort: false,
    sort: false,
  }

  render() {
    const columnNames = Object.keys(this.props.filters);
    const wrappedOnFilter = clickWrapper(this.props.onFilter);
    const wrappedOnSort = clickWrapper(this.props.onSort);
    const { ItemComponent, itemMessages } = this.props;

    const header = columnNames.map(column =>
      <th key={column} className={`header ${sortClass(column, this.props.sort)}`} onClick={wrappedOnSort(column)}>
        <FormattedMessage {...itemMessages[column]} />
        {
          this.props.sort ?
            <SortImg className={styles.sortImg} isCurrent={this.props.sort.column === column} order={this.props.sort.order} /> :
            null
        }
      </th>
    );

    const filterInputs = this.props.onFilter ?
      columnNames.map(column =>
        <td key={column}>
          <input className={styles.filterInput} type="text" value={this.props.filters[column]} onChange={wrappedOnFilter(column)} />
        </td>
      ) : null;

    const sortedRows = this.props.sort ?
      filterItems(this.props.list, this.props.filters).sort((a, b) => sortFunction(a, b, this.props.sort)) :
      filterItems(this.props.list, this.props.filters);
    const rows = sortedRows.map((item, idx) =>
      <ItemComponent key={item.key ? item.key() : idx} item={item} actions={this.props.itemActions} />);

    return (
      <table className="table table-hover">
        <thead>
          <tr>
            { header }
            <th><FormattedMessage {...itemMessages.actions} /></th>
          </tr>
          <tr>
            { filterInputs }
          </tr>
        </thead>
        <tbody>
          { rows }
        </tbody>
      </table>
    );
  }
}

export default ItemedTable;
