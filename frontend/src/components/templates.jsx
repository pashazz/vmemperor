import _ from 'lodash';
import React from 'react';
import Reflux from 'reflux';

import TemplateStore from '../flux/template-store';
import TemplateActions from '../flux/template-actions';

class TemplateInfo extends React.Component {
  constructor() {
    super();
    this.handleSubmit = this.handleSubmit.bind(handleSubmit);
    this.renderActions = this.renderActions.bind(renderActions);
  }

  handleSubmit(e) {
    e.preventDefault();
    console.log(e.target.value);
  }

  renderActions(template) {
    const urlValue = (template['tags']['install_repository'] === undefined) ? template['install_repository'] : template['default_mirror'];
    const proxies = null;

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
  }

  render() {
    const template = this.props.template;
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
