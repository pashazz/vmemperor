var React = require('react'),
    Reflux = require('reflux'),
    _ = require('lodash');

var VMStore = require('../flux/vm-store'),
    VMActions = require('../flux/vm-actions');

var CONFIG = {
  sort: { column: "name", order: "asc" },
  columns: {
    name: { name: "Name", filterText: "", defaultSortOrder: "desc"},
    pool: { name: "Pool", filterText: "", defaultSortOrder: "desc"},
    ip: { name: "IP", filterText: "", defaultSortOrder: "desc"},
    state: { name: "State", filterText: "", defaultSortOrder: "desc"}
  }
};

var operators = {
  "<": function(x, y) { return x < y; },
  "<=": function(x, y) { return x <= y; },
  ">": function(x, y) { return x > y; },
  ">=": function(x, y) { return x >= y; },
  "==": function(x, y) { return x == y; }
};

var VMItem = React.createClass({
  _start: function(e) {
    e.preventDefault();
    VMActions.start(this.props.vm);
  },

  _shutdown: function(e) {
    e.preventDefault();
    VMActions.shutdown(this.props.vm);
  },

  render: function() {
    var actions = null;
    switch(this.props.vm.state) {
      case 'Halted': actions = <a className="btn btn-primary btn-xs" onClick={this._start}>start</a>; break;
      case 'Running': actions = <a className="btn btn-danger btn-xs" onClick={this._shutdown}>shutdown</a>; break;
    };

    var stateLabel = (this.props.vm.state == 'Halted' ?
      <span className="label label-warning">Halted</span> :
      <span className="label label-success">Running</span>);

    var info = <div>{this.props.vm.description}</div>;

    return (
      <tr>
        <td><strong>{this.props.vm.name}</strong> <i>{this.props.vm.description}</i></td>
        <td>{this.props.vm.pool}</td>
        <td>{this.props.vm.ip}</td>
        <td>{stateLabel}</td>
        <td>{actions}</td>
      </tr>
    );
  }

});

var VMTable = React.createClass({

  getInitialState: function() {
    return {
      items: this.props.items || [],
      sort: this.props.config.sort || { column: "", order: "" },
      columns: this.props.config.columns
    };
  },

  componentWillReceiveProps: function(nextProps) {
    if (nextProps.items != this.props.items) {
      this.setState({items: nextProps.items});
    }
  },

  handleFilterTextChange: function(column) {
    return function(newValue) {
      var obj = this.state.columns;
      obj[column].filterText = newValue;

      // Since we have already mutated the state, just call forceUpdate().
      // Ideally we'd copy and setState or use an immutable data structure.
      this.forceUpdate();
    }.bind(this);
  },

  columnNames: function() {
     return Object.keys(this.state.columns);
  },

  sortColumn: function(column) {
    return function(event) {
      var newSortOrder = (this.state.sort.order == "asc") ? "desc" : "asc";

      if (this.state.sort.column != column) {
          newSortOrder = this.state.columns[column].defaultSortOrder;
      }

      this.setState({sort: { column: column, order: newSortOrder }});
    }.bind(this);
  },

  sortClass: function(column) {
    var ascOrDesc = (this.state.sort.order == "asc") ? "headerSortAsc" : "headerSortDesc";
    return (this.state.sort.column == column) ? ascOrDesc : "";
  },

  render: function() {
    var rows = [];

    var columnNames = this.columnNames();
    var filters = {};

    var operandRegex = /^((?:(?:[<>]=?)|==))\s?([-]?\d+(?:\.\d+)?)$/;

    columnNames.forEach(function(column) {
      var filterText = this.state.columns[column].filterText;
      filters[column] = null;

      if (filterText.length > 0) {
        operandMatch = operandRegex.exec(filterText);
        if (operandMatch && operandMatch.length == 3) {
          //filters[column] = Function.apply(null, ["x", "return x " + operandMatch[1] + " " + operandMatch[2]]);
          filters[column] = function(match) { return function(x) { return operators[match[1]](x, match[2]); }; }(operandMatch);
        } else {
          filters[column] = function(x) {
            return (x.toString().toLowerCase().indexOf(filterText.toLowerCase()) > -1);
          };
        }
      }
    }, this);

    var filteredItems = _.filter(this.state.items, function(item) {
      return _.every(columnNames, function(c) {
        return (!filters[c] || filters[c](item[c]));
      }, this);
    }, this);

    var sortedItems = _.sortBy(filteredItems, this.state.sort.column);
    if (this.state.sort.order === "desc") sortedItems.reverse();

    sortedItems.forEach(function(item, idx) {
      rows.push(
        <VMItem key={idx} vm={item} />
      );
    }.bind(this));

    var filterLink = function(column) {
      return {
        value: this.state.columns[column].filterText,
        requestChange: this.handleFilterTextChange(column)
      };
    }.bind(this);

    var header = columnNames.map(function(c) {
      return <th key={c} onClick={this.sortColumn(c)} className={"header " + this.sortClass(c)}>{this.state.columns[c].name}</th>;
    }, this);

    var filterInputs = columnNames.map(function(c) {
      return <td key={c}><input type="text" valueLink={filterLink(c)} /></td>;
    }, this);

    return (
      <table className="table table-hover">
        <thead>
          <tr>
            { header }
            <th>Actions</th>
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
});

var VMList = React.createClass({
  mixins: [Reflux.ListenerMixin],

  onVMChange: function() {
    this.setState({
      status: VMStore.status,
      vms: VMStore.vms
    });
  },

  componentDidMount: function() {
    this.listenTo(VMStore, this.onVMChange);
    VMActions.list();
  },

  getInitialState: function() {
    return {
      status: VMStore.status,
      vms: VMStore.vms
    };
  },

  render: function () {
    return (
      <div>
        <VMTable items={this.state.vms} config={CONFIG} />
      </div>
    );
  }

});

module.exports = VMList;
