/*
 *
 * Templates
 *
 */

import React, { PropTypes as T } from 'react';
import { connect } from 'react-redux';
import { FormattedHTMLMessage } from 'react-intl';
import messages from './messages';
import ItemedTable from 'components/ItemedTable';
import TemplateTableItem from 'components/TemplateTableItem';
import TemplateMessages from 'components/TemplateTableItem/messages';
import { selectTemplateList, selectTemplateFilters, selectTemplateSort } from './selectors';
import { setTemplateFilter, setTemplateSort, runTemplateAction } from './actions';

export class Templates extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    list: T.any.isRequired,
    filters: T.object.isRequired,
    sort: T.object.isRequired,
    setTemplateFilter: T.func.isRequired,
    setTemplateSort: T.func.isRequired,
    runTemplateAction: T.func.isRequired,
  }

  render() {
    const actions = {
      update: template => this.props.runTemplateAction('update', template),
      enable: template => this.props.runTemplateAction('enable', template),
      disable: template => this.props.runTemplateAction('disable', template),
    };

    return (
      <div>
        <ItemedTable
          list={this.props.list}
          filters={this.props.filters}
          sort={this.props.sort}
          onFilter={this.props.setTemplateFilter}
          onSort={this.props.setTemplateSort}
          itemActions={actions}
          itemMessages={TemplateMessages}
          ItemComponent={TemplateTableItem}
        />

        <div className="container-fluid">
          <h1>
            <FormattedHTMLMessage {...messages.notUsable} />
          </h1>
          <p className="lead">
            <FormattedHTMLMessage {...messages.generators} />
          </p>
          <p className="text-muted">
            <FormattedHTMLMessage {...messages.todo} />
          </p>
        </div>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    list: selectTemplateList()(state),
    filters: selectTemplateFilters()(state),
    sort: selectTemplateSort()(state),
  };
}

const mapDispatchToProps = {
  setTemplateFilter,
  setTemplateSort,
  runTemplateAction,
};

export default connect(mapStateToProps, mapDispatchToProps)(Templates);
