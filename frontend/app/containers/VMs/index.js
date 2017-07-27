import React, { PropTypes as T } from 'react';
import { connect } from 'react-redux';
import ItemedTable from 'components/ItemedTable';
import VMTableItem from 'components/VMTableItem';
import VMMessages from 'components/VMTableItem/messages';
import { selectVMList, selectVMFilters, selectVMSort } from './selectors';
import { setVMFilter, runVMAction, setVMSort } from './actions';

class VMs extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    list: T.any.isRequired,
    filters: T.object.isRequired,
    sort: T.object.isRequired,
    setVMFilter: T.func.isRequired,
    runVMAction: T.func.isRequired,
    setVMSort: T.func.isRequired,
  }

  render() {
    const actions = {
      start: vm => this.props.runVMAction('start', vm),
      shutdown: vm => this.props.runVMAction('shutdown', vm),
    };

    return (
      <ItemedTable
        list={this.props.list}
        filters={this.props.filters}
        sort={this.props.sort}
        onFilter={this.props.setVMFilter}
        onSort={this.props.setVMSort}
        itemActions={actions}
        itemMessages={VMMessages}
        ItemComponent={VMTableItem}
      />
    );
  }
}

function mapStateToProps(state) {
  return {
    list: selectVMList()(state),
    filters: selectVMFilters()(state),
    sort: selectVMSort()(state),
  };
}

const mapDispatchToProps = {
  setVMFilter,
  runVMAction,
  setVMSort,
};

export default connect(mapStateToProps, mapDispatchToProps)(VMs);
