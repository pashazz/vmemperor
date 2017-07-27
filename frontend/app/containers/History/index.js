import React, { PropTypes as T } from 'react';
import { connect } from 'react-redux';
import { getVMList } from './selectors';
import { stopTracking } from './actions';
import ItemedTable from 'components/ItemedTable';
import HistoryTableItem from 'components/HistoryTableItem';
import HistoryMessages from 'components/HistoryTableItem/messages';

class History extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    list: T.any.isRequired,
    stopTracking: T.func.isRequired,
  }

  render() {
    const filters = {
      name: '',
      status: '',
      details: '',
    };

    const actions = {
      stop: vm => this.props.stopTracking(vm.id),
    };

    return (
      <ItemedTable
        list={this.props.list}
        filters={filters}
        itemActions={actions}
        itemMessages={HistoryMessages}
        ItemComponent={HistoryTableItem}
      />
    );
  }
}

function mapStateToProps(state) {
  return {
    list: getVMList()(state),
  };
}

const mapDispatchToProps = {
  stopTracking,
};

export default connect(mapStateToProps, mapDispatchToProps)(History);
