import _ from 'lodash';
import React from 'react';
import Reflux from 'reflux';

import Multiselect  from 'react-bootstrap-multiselect';

import TemplateStore from '../flux/template-store';
import TemplateActions from '../flux/template-actions';



const handleEnable = (template) =>
  (e) => {
    TemplateActions.enable(template);
    e.preventDefault();
  };

const handleDisable = (template) =>
  (e) => {
    TemplateActions.disable(template);
    e.preventDefault();
  };

const Hooks = React.createClass({
  handleChange: function(e, newValue) {

    this.props.onChange(e[0].label, newValue);
  },
  render: function () {
    return (
      <Multiselect data={this.props.hooks} onChange={this.handleChange} multiple />
    );
  }
});


var MirrorUrl = React.createClass({
  getInitialState: function() {
    return { value: this.props.defaultValue };
  },
  handleChange: function(event) {
    this.setState({value: event.target.value});
    this.props.onChange(event.target.value);
  },
  render: function() {
    return (
      <input
        type="text"
        className="form-control"
        value={this.state.value}
        onChange={this.handleChange}
      />
    );
  }
});



class TemplateInfo extends React.Component {
  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(this);
    this.renderActions = this.renderActions.bind(this);
    this.handleUpdateHooks = this.handleUpdateHooks.bind(this);
    this.onMirrorUrlChange = this.onMirrorUrlChange.bind(this);
  }

  handleSubmit(e, template) {
    if (this.state.mirrorUrl) {
      template['default_mirror'] = this.state.mirrorUrl;
    }
    TemplateActions.update(template);
    e.preventDefault();
  }

  handleUpdateHooks(key, value, template) {
    template.other_config.vmemperor_hooks[key] = value;
  }

  onMirrorUrlChange(url) {
    this.setState({mirrorUrl: url});
  }

  renderActions(template) {
    const urlValue = (template['other_config']['install_repository'] === undefined) ? template['other_config']['default_mirror'] : template['other_config']['install_repository'];
    const hooks = Object.keys(template.other_config.vmemperor_hooks).map((key, value) => ({value: key, selected: value }));
    const enabled = template['tags'].indexOf('vmemperor') >= 0;
    var enableButton;
    if (enabled) {
        enableButton = <button onClick={handleDisable(template)} value="disable" className="btn btn-sm btn-danger">Disable</button>;
    } else {
        enableButton = <button onClick={handleEnable(template)} value="enable" className="btn btn-sm btn-primary">Enable</button>;
    }

    return (
      <form onSubmit={this.handleSubmit}>
        <div className="form-group">
          <label>Select installation mirror.</label>
          <MirrorUrl defaultValue={ urlValue } onChange={(mirrorUrlValue) => this.onMirrorUrlChange(mirrorUrlValue, urlValue) } />
        </div>
        <div className="form-group">
          <label>Select reverse-proxy config style</label>
          <Hooks hooks={hooks} onChange={(key, value) => this.handleUpdateHooks(key, value, template) } />
        </div>
        <div className="btn btn-group">
          {enableButton}
          <button onClick={(e) => this.handleSubmit(e, template)} value="update" className="btn btn-sm btn-info">Update</button>
        </div>
      </form>
    );
  }

  render() {
    const template = this.props.template;
    return (
      <tr>
        <td>
          <blockquote>
              <p>{template.endpoint_description}</p>
              <footer>{template.endpoint_url}</footer>
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
};

class TemplateTable extends React.Component {
  render() {
    var templates = this.props.templates.map((template, id) => {
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
};

const Templates = React.createClass({
  mixins: [Reflux.ListenerMixin],

  onTemplatesChange() {
    this.setState({
      status: TemplateStore.status,
      templates: TemplateStore.templates
    });
  },

  componentDidMount() {
    this.listenTo(TemplateStore, this.onTemplatesChange);
    TemplateActions.list();
  },

  getInitialState() {
    return {
      status: TemplateStore.status,
      templates: TemplateStore.templates
    };
  },

  render() {
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





export default Templates;
