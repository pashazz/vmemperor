var React = require('react'),
    Reflux = require('reflux'),
    _ = require('lodash');

var TemplateStore = require('../flux/template-store'),
    TemplateActions = require('../flux/template-actions');

var TemplateInfo = React.createClass({

  handleSubmit: function(e) {
    e.preventDefault();
    console.log(e.target.value);
  },

  renderActions: function(template) {
    var urlValue = (template['tags']['install_repository'] === undefined) ? template['install_repository'] : template['default_mirror'];
    var proxies = null;

    return (
      <form onSubmit={this.handleSubmit}>
        <div className="form-group">
          <label>Select installation mirror.</label>
          <input type="url" className="form-control" value={ urlValue } />
        </div>
        <div className="form-group">
          <label>Select reverse-proxy config style</label>
          <select className="form-control proxy-select">
            <option value={ null }>{"I don't need it at all"}</option>
            {proxies}
          </select>
        </div>
        <div className="btn btn-group">
          <button onClick={this.handleSubmit} value="enable" className="btn btn-sm btn-primary">Enable</button>
          <button onClick={this.handleSubmit} value="disable" className="btn btn-sm btn-danger">Disable</button>
          <button onClick={this.handleSubmit} value="update" className="btn btn-sm btn-info">Update</button>
        </div>
      </form>
    );
  },

  render: function() {
    var template = this.props.template;
    return (
      <tr>
        <td>
          <blockquote>
              <p>{template['endpoint']['description']}</p>
              <footer>{template['endpoint']['url']}</footer>
          </blockquote>
          <td>
            <blockquote>
                <p className="lead">{ template['name_label'] }</p>
                <footer>{ template['name_description'] }</footer>
            </blockquote>
          </td>
          <td>
            {this.renderActions(template)}
          </td>
        </td>
      </tr>
    );
  }
});

var TemplateTable = React.createClass({
    
    render: function () {
      var templates = this.props.templates.map(function(template, id) {
        return <TemplateInfo key={id} template={template} />;
      });

      return (
        <div className="table-responsive">
          <table className="table table-hover table-vcenter">
            <thead>
              <tr>
                <th className="col-sm-2">Location</th>
                <th className="col-sm-6">Template name</th>
                <th className="col-sm-4">Tags</th>
              </tr>
            </thead>
            <tbody>
              {templates}
            </tbody>
          </table>
        </div>
      );
    }
});

var Templates = React.createClass({
  mixins: [Reflux.ListenerMixin],

  onTemplatesChange: function() {
    this.setState({
      status: TemplateStore.status,
      templates: TemplateStore.templates
    });
  },

  componentDidMount: function() {
    this.listenTo(TemplateStore, this.onTemplatesChange);
    TemplateActions.list();
  },

  getInitialState: function() {
    return {
      status: TemplateStore.status,
      templates: TemplateStore.templates
    };
  },

  render: function () {
    
    return (
      <div>
        <TemplateTable templates={this.state.templates} />

        <div className="container-fluid">
          <h1>The templates you can not use <i>yet</i></h1>
          <p className="lead">The following list of templates is able to work with VM emperor system but no one has implemented automatic installer instructions generator. For this moment only <a href="http://en.wikipedia.org/wiki/Preseed">preseed-generator</a> is available, commits are welcome.</p>
          <p className="text-muted">TODO</p>
        </div>
      </div>
    );
  }
  
});

module.exports = Templates;