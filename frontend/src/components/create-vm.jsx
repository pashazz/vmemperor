import _ from 'lodash';
import React from 'react';
import Reflux from 'reflux';
import serialize from 'form-serialize';

import Modal from './modal.jsx';

import VMActions from '../flux/vm-actions';
import PoolActions from '../flux/pool-actions';
import PoolStore from '../flux/pool-store';

var Switch = require('react-bootstrap-switch');

class VMHookOptions extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (<div>
        {this.props.options.map((option, idx) => <div key={idx}>
            <label class="control-label" for={option.field}>{option.legend}</label>
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-network"></i></span>
              <input type="number" pattern="\d*" className="form-control" id={option.field} name={option.field} min="9"
                     defaultValue={option.default_value} enabled/>
            </div>
          </div>
        )}
      </div>
    );
  }
}

class VMHook extends React.Component {
  constructor(props) {
    super(props);

    this.onEnabledChange = this.onEnabledChange.bind(this);

    this.state ={
      enabled: true
    }
  }

  onEnabledChange(e) {
    this.setState({enabled: e});
  }

  render() {
    return (
      <div>
        <input type="hidden" name={this.props.hookName} value={this.state.enabled} />
        <h4>{this.props.hook.header}<Switch onChange={this.onEnabledChange}/></h4>
        <h5>{this.props.hook.help}</h5>
        { this.state.enabled ? <VMHookOptions options={this.props.hook.options}/> : null }
      </div>
    );
  }
}


class VMForm extends React.Component {
  constructor(props) {
    super(props);

    this.handleSubmit = this.handleSubmit.bind(this);
    this.onPoolChange = this.onPoolChange.bind(this);
    this.onTemplateChange = this.onTemplateChange.bind(this);

    this.state = {
      templates: [],
      hooks: []
    };
  }

  handleSubmit(e) {
    e.preventDefault();
    VMActions.create(serialize(e.target, {hash: true}))
      .then(this.props.close)
      .then(_ => this.context.router.transitionTo('history'));
  }

  onPoolChange(e) {
    const selectedPool = this.props.pools.find(pool => pool.id === e.target.value);
    this.setState({
      selectedPoolId: selectedPool.id,
      templates: selectedPool ? _.map(selectedPool.templates_enabled, (template) => ({
        id: template.uuid,
        description: template.name_label
      })) : []
    });
  }

  onTemplateChange(e) {
    if (this.state.selectedPoolId) {
      const selectedPool = this.props.pools.find(pool => pool.id === this.state.selectedPoolId);
      const selectedTemplate = selectedPool.templates_enabled.find(template => template.uuid === e.target.value);

      const hooks = _.map(selectedTemplate.other_config.vmemperor_hooks_meta, (hook, hookName) => {
        const hookEnabled = !!selectedTemplate.other_config.vmemperor_hooks[hookName];
        return {
          hookName: hookName,
          hook: hook,
          enabled: hookEnabled
        };
      });

      if (selectedTemplate) {
        this.setState({
          hooks: _.filter(hooks, hook => hook.enabled)
        });
      } else {
        this.setState({
          hooks: []
        });
      }
    }
  }

  render() {
    return (
      <form role="form" id="create-vm-form" ref="form" onSubmit={this.handleSubmit}>
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-servers"></i></span>
          <select className="form-control input" id="pool-select" name="pool-select" onChange={this.onPoolChange}>
            <option value="--">Select where to deploy instance</option>
            {this.props.pools.map((pool, idx) =>
              <option key={idx} value={pool.id}>{pool.description}</option>)}
          </select>
        </div>
        <br />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-ubuntu"></i></span>
          <select className="form-control" id="template-select" name="template-select" enabled
                  onChange={this.onTemplateChange}>
            <option value="--">Select OS template for your virtual machine</option>
            {this.state.templates.map((template, idx) =>
              <option key={idx} value={template.id}>{template.description}</option>)}
          </select>
        </div>
        <hr />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-address"></i></span>
          <input type="text"
                 className="form-control"
                 placeholder="Your full name (e.g. John Smith)"
                 id="user-fullname"
                 name="user-fullname"
                 required="true"
                 enabled/>
        </div>
        <br />
        <div className="row">
          <div className="col-sm-12 col-lg-12">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-user"></i></span>
              <input type="text"
                     className="form-control"
                     placeholder="Your login for new VM"
                     id="username"
                     name="username"
                     enabled/>
              <span className="input-group-addon"><i className="icon-at"></i></span>
              <input type="text"
                     className="form-control"
                     placeholder="Choose hostname for your VM"
                     id="hostname"
                     name="hostname"
                     required="true"
                     enabled/>
              <span className="input-group-addon">.at.ispras.ru</span>
            </div>
          </div>
        </div>
        <br />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-password"></i></span>
          <input type="password"
                 className="form-control input"
                 placeholder="Choose password for your VM"
                 id="password"
                 name="password"
                 required="true"
                 enabled/>
          <span className="input-group-addon"><i className="icon-password"></i></span>
          <input type="password"
                 className="form-control input"
                 placeholder="Confirm password"
                 id="password2"
                 name="password2"
                 required="true"
                 enabled/>
        </div>
        <br />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-noteslist" style={{ fontSize: '28px' }}></i></span>
          <textarea
            type="text"
            className="form-control input"
            placeholder="What do you want to do with this virtual machine?"
            id="vm-description"
            name="vm-description"
            required="true"
            style={{resize: 'vertical'}}
            enabled/>
        </div>
        <br />
        <h4>Resources settings</h4>
        <div className="row">

          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-processorthree"></i></span>
              <input type="number" pattern="\d*"
                     className="form-control" id="vcpus" name="vcpus" min="1" defaultValue="1" enabled/>
              <span className="input-group-addon">cores</span>
            </div>
          </div>

          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-ram"></i></span>
              <input type="number" pattern="\d*"
                     className="form-control" id="ram" name="ram" min="256" defaultValue="256" enabled/>
              <span className="input-group-addon">MB</span>
            </div>
          </div>

          <div className="col-sm-4 col-lg-4">
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-hdd"></i></span>
              <input type="number" pattern="\d*"
                     className="form-control" id="hdd" name="hdd" min="9" defaultValue="9" enabled/>
              <span className="input-group-addon">GB</span>
            </div>
          </div>
        </div>

        <br />
        <br />

        { this.state.hooks.map((e, idx) => {
          return <VMHook key={idx} hook={e.hook} hookName={e.hookName}/>
        })
        }

        <br />

        <br />
        <input type="submit" className="btn btn-lg btn-primary btn-block" id="create-button" enabled/>
      </form>
    );
  }
}

VMForm.contextTypes = {
  router: React.PropTypes.func
};

class HostInfo extends React.Component {
  render() {
    const entry = this.props;
    return (
      <div className="col-md-4">
        <div className="panel panel-default">
          <div className="panel-heading">
            Host: {entry['name_label']}
          </div>
          <div className="panel-body">
            <dl className="dl-horizontal">
              <dt>Memory total</dt>
              <dd>{ entry['memory_total'] }MB</dd>
              <small>
                <dt>available</dt>
                <dd>{entry['memory_available']}MB</dd>
                <dt>physically free</dt>
                <dd>{ entry['memory_free'] }MB</dd>
                <hr style={{margin: '6px 0'}}/>
                <dt>Running VMs now</dt>
                <dd><span className='badge'>{ entry['resident_VMs'].length }</span></dd>
                <dt>Software installed</dt>
                <dd>{ entry['software_version']['product_brand'] }</dd>
                <dt>Software version</dt>
                <dd>{ entry['software_version']['product_version'] }</dd>
                <dt>Xen version</dt>
                <dd>{ entry['software_version']['xen'] }</dd>
                <hr style={{margin: '6px 0'}}/>
                <dt>Processor model</dt>
                <dd>
                  <details>
                    <summary>Click to show</summary>
                    { entry['cpu_info']['modelname'] }
                  </details>
                </dd>
                <dt>frequency</dt>
                <dd>{ entry['cpu_info']['speed'] }MHz</dd>
                <dt>cores</dt>
                <dd>{ entry['cpu_info']['cpu_count'] }</dd>
              </small>
            </dl>
          </div>
        </div>
      </div>
    );
  }
}

class PoolInfo extends React.Component {
  render() {
    const {description, hdd_available, host_list} = this.props;
    return (
      <div className="panel panel-default">
        <div className="panel-heading">
          <h3 className="panel-title">{description}</h3>
        </div>
        <div className="panel-body">
          <div className="row">
            { host_list.map((host, idx) => <HostInfo key={idx} {...host} />) }
          </div>
          <p>
            <dl className="dl-horizontal">
              <dt>HDD available</dt>
              <dd>{hdd_available} GB</dd>
            </dl>
          </p>
        </div>
      </div>
    );
  }
}

const CreateVM = React.createClass({
  mixins: [Reflux.ListenerMixin],

  onPoolsChange() {
    this.setState({
      pools: PoolStore.pools
    });
  },

  componentDidMount() {
    this.listenTo(PoolStore, this.onPoolsChange);
    PoolActions.list();
  },

  getInitialState() {
    return {
      modalShow: false,
      pools: []
    };
  },

  showModal() {
    this.setState({modalShow: true});
  },

  hideModal() {
    this.setState({modalShow: false});
  },

  renderModal() {
    return this.state.modalShow ?
      <Modal title="Virtual machine options" show lg close={this.hideModal}>
        <VMForm
          pools={this.state.pools}
          close={this.hideModal}/>
      </Modal> :
      null;
  },

  render() {
    return (
      <div>
        <p>
          <button className="btn btn-lg btn-primary" onClick={this.showModal}>CreateVM</button>
        </p>
        <div className="row">
          { this.state.pools.map((pool, idx) => <PoolInfo key={idx} {...pool} />) }
        </div>
        {this.renderModal()}
      </div>
    );
  }
});

export default CreateVM;
