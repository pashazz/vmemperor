import _ from 'lodash';
import React from 'react';
import Reflux from 'reflux';
import serialize from 'form-serialize';

import Modal from './modal.jsx';

import VMActions from '../flux/vm-actions';
import PoolActions from '../flux/pool-actions';
import AlertActions from '../flux/alert-actions';
import PoolStore from '../flux/pool-store';

import Switch from 'react-bootstrap-switch';

class VMHookOptions extends React.Component {
  render() {
    return (
      <div>
        {this.props.options.map((option, idx) => <div key={idx}>
            <label className="control-label" htmlFor={option.field}>{option.legend}</label>
            <div className="input-group">
              <span className="input-group-addon"><i className="icon-cog"></i></span>
              <input type="text" className="form-control" id={option.field} name={`hooks[${this.props.name}][${option.field}]`}
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
      enabled: false
    }
  }

  onEnabledChange(e) {
    this.setState({enabled: e});
  }

  render() {
    return (
      <div>
        <input type="hidden" name={`hooks[${this.props.hookName}][enabled]`} value={this.state.enabled} />
        <h5>{this.props.hook.header} <Switch onChange={this.onEnabledChange} state={this.state.enabled}/></h5>
        <h6>{this.props.hook.help}</h6>
        { this.state.enabled ? <VMHookOptions {...this.props.hook} name={this.props.hookName} /> : null }
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
      selectedPool: null,
      selectedTemplate: null
    };
  }

  handleSubmit(e) {
    e.preventDefault();
    var req = serialize(e.target, {hash: true});
    if (req["storage-select"] === "--") {
      AlertActions.err('123123');
    } else {
      VMActions.create(req)
          .then(this.props.close)
          .then(() => this.context.router.transitionTo('history'));
    }

  }

  getTemplates({selectedPool = null}) {
    return selectedPool ?
      selectedPool.templates_enabled.map(template => ({
        id: template.uuid,
        description: template.name_label
      })) : [];
  }

  getStorageResources({selectedPool = null}) {
    return selectedPool ?
        selectedPool.storage_resources.map(storage => ({
          id: storage.uuid,
          description: storage.name_label
        })) : [];
  }

  getNetworks({selectedPool = null}) {
    return selectedPool ?
        selectedPool.networks.map(network => ({
          id: network.uuid,
          description: network.name_label
        })) : [];
  }

  getHooks({selectedTemplate = null}) {
    return selectedTemplate ?
      _.map(selectedTemplate.other_config.vmemperor_hooks_meta, (hook, hookName) => ({
          hookName: hookName,
          hook: hook,
          enabled: !!selectedTemplate.other_config.vmemperor_hooks[hookName]
        }))
        .filter(hook => hook.enabled)
      : [];
  }

  onPoolChange(e) {
    this.setState({
      selectedPool: this.props.pools.find(pool => pool.id === e.target.value),
      selectedTemplate: null
    });
  }

  onTemplateChange(e) {
    const selectedPool = this.state.selectedPool;
    if(selectedPool) {
      this.setState({
        selectedTemplate: selectedPool.templates_enabled.find(template => template.uuid === e.target.value)
      });
    }
  }

  render() {
    return (
      <form role="form" id="create-vm-form" ref="form" data-toggle="validator" onSubmit={this.handleSubmit}>
        <h4>Infrastructure settings</h4>
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-servers"></i></span>
          <select className="form-control input" id="pool-select" name="pool-select" onChange={this.onPoolChange}>
            <option value="--">Select where to deploy instance</option>
            {this.props.pools.map(pool =>
              <option key={pool.id} value={pool.id}>{pool.description}</option>)}
          </select>
        </div>
        <br />
        <div className="input-group">
          <span className="input-group-addon"><i className="icon-ubuntu"></i></span>
          <select className="form-control" id="template-select" name="template-select" enabled
                  onChange={this.onTemplateChange}>
            <option value="--">Select OS template for your virtual machine</option>
            {this.getTemplates(this.state).map(template =>
              <option key={template.id} value={template.id}>{template.description}</option>)}
          </select>

        </div>
        <br />
        {
            this.state.selectedPool ?
                <div className="input-group">
                  <span className="input-group-addon"><i className="icon-database"></i></span>
                  <select required className="form-control" id="storage-select" name="storage-select" enabled>
                    <option value="--">Select storage backend for your virtual machine</option>
                    {this.getStorageResources(this.state).map(storage =>
                        <option key={storage.id} value={storage.id}>{storage.description}</option>)}
                  </select>
                </div> : null
        }
        <br />
        {
          this.state.selectedPool ?
              <div className="input-group">
                <span className="input-group-addon"><i className="icon-network"></i></span>
                <select required className="form-control" id="network-select" name="network-select" enabled>
                  <option value="--">Select physical network for your virtual machine</option>
                  {this.getNetworks(this.state).map(network =>
                      <option key={network.id} value={network.id}>{network.description}</option>)}
                </select>
              </div> : null
        }

        <hr />
        <h4>Account settings</h4>
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
                 data-minlength="6"
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
                 data-match="#password" data-match-error="Whoops, these don't match"
                 enabled/>
                 <div className="help-block with-errors"></div>
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
        <hr />
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

        <hr />
        <br />
        <h4>Post-creation hooks settings</h4>

        { this.getHooks(this.state).map((e, idx) =>
          <VMHook key={idx} hook={e.hook} hookName={e.hookName}/>)}

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
