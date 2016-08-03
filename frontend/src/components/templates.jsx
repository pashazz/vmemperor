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

class TemplateInfo extends React.Component {
  constructor(props) {
    super(props);

    this.handleSubmit = this.handleSubmit.bind(this);
    this.renderOptions = this.renderOptions.bind(this);
    this.renderActions = this.renderActions.bind(this);
    this.handleUpdateHooks = this.handleUpdateHooks.bind(this);
    this.onMirrorUrlChange = this.onMirrorUrlChange.bind(this);

    this.state = this.getStateFromProps(props)
  }

  getStateFromProps(props) {
    const { install_repository, vmemperor_hooks, default_mirror } = props.template.other_config;

    return {
      mirrorUrl: install_repository ? install_repository : default_mirror,
      hooks: vmemperor_hooks
    };
  }

  componentWillReceiveProps(newProps) {
    this.setState(this.getStateFromProps(newProps));
  }

  handleSubmit(e) {
    TemplateActions.update({
      ...this.props.template,
      default_mirror: this.state.mirrorUrl,
      vmemperor_hooks: this.state.hooks
    });
    e.preventDefault();
  }

  handleUpdateHooks(option, isSelected) {
    this.setState({
      hooks: { [option[0].value]: isSelected }
    });
  }

  onMirrorUrlChange(e) {
    this.setState({mirrorUrl: e.target.value});
  }

  renderOptions() {
    const preparedData = _.map(this.state.hooks, (selected, name) => ({value: name, selected: selected}));

    return (
      <form onSubmit={this.handleSubmit}>
        <div className="form-group">
          <label>Select installation mirror.</label>
          <input
            type="text"
            className="form-control"
            value={this.state.mirrorUrl}
            onChange={this.onMirrorUrlChange} />
        </div>
        <div className="form-group">
          <Multiselect
            className="form-control"
            buttonText={options => `Hooks (${options.length} Selected)`}
            data={preparedData}
            onChange={this.handleUpdateHooks}
            multiple />
          <input type="submit" value="update" className="btn btn-info" />
        </div>

      </form>
    );
  }

  renderActions() {
    const { template } = this.props;

    return template.tags.indexOf('vmemperor') >= 0 ?
      <button onClick={handleDisable(template)} value="disable" className="btn btn-danger">Disable</button> :
      <button onClick={handleEnable(template)} value="enable" className="btn btn-primary">Enable</button>;
  }

  render() {
    const { template } = this.props;
    return (
      <tr>
        <td>
          <blockquote>
              <p>{template.endpoint_description}</p>
              <footer>{template.endpoint_url}</footer>
          </blockquote>
          <td>
            <blockquote>
                <p className="lead">{ template.name_label }</p>
                <footer>{ template.name_description }</footer>
            </blockquote>
          </td>
          <td>
            {this.renderOptions()}
          </td>
          <td style={{verticalAlign: 'middle'}}>
            {this.renderActions()}
          </td>
        </td>
      </tr>
    );
  }
}

class TemplateTable extends React.Component {
  render() {
    const templates = this.props.templates.map((template, id) => {
      return <TemplateInfo key={id} template={template} />;
    });

    return (
      <div className="table-responsive">
        <table className="table table-hover table-vcenter">
          <thead>
            <tr>
              <th className="col-sm-2">Location</th>
              <th className="col-sm-5">Template name</th>
              <th className="col-sm-4">Tags</th>
              <th className="col-sm-1">Actions</th>
            </tr>
          </thead>
          <tbody>
            {templates}
          </tbody>
        </table>
      </div>
    );
  }
}

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
