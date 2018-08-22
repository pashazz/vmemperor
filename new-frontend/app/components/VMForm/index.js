/**
*
* Vmform
*
*/
import React from 'react';
import T from 'prop-types';
import autofill from  'react-autofill-innerref';
import { FormattedMessage } from 'react-intl';
import messages from './messages';
import styles from './styles.css';
import VMInput from './helpers';
import IPT from 'react-immutable-proptypes';
import Pool from 'models/Pool';
import BasicRecord from 'models/BasicRecord';
import ISO from 'models/ISO';
import Network, { NetworkShape } from 'models/Network';
import Template from 'models/Template';
import { AvForm } from 'availity-reactstrap-validation';

function getTemplates(pool = null) {
  return pool ?
    pool.templates_enabled.map(template => ({
      id: template.uuid,
      description: template.name_label,
    })) : [];
}

function getStorageResources(pool = null) {
  return pool ?
    pool.storage_resources.map(storage => ({
      id: storage.uuid,
      description: storage.name_label,
    })) : [];
}

function getNetworks(pool = null) {
  return pool ?
    pool.networks.map(network => ({
      id: network.uuid,
      description: network.name_label,
    })) : [];
}

/*
function getHooks(template = null) {
  if (!template) {
    return {};
  }

  const meta = template.other_config.vmemperor_hooks_meta;

  return Object.keys(meta)
    .filter(key => !!template.other_config.vmemperor_hooks[key])
    .reduce(
    (ac, key) => ({
      ...ac,
      [key]: {
        ...meta[key],
        enabled: false,
      },
    }),
    {}
  );
}
*/

class VMForm extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    pools: IPT.listOf(T.instanceOf(Pool)).isRequired,
    networks: IPT.listOf(NetworkShape).isRequired,
    isos: IPT.listOf(T.instanceOf(ISO)).isRequired,
    templates: IPT.listOf(T.instanceOf(Template)).isRequired,
    onSubmit: T.func.isRequired,
  };

  constructor(props) {
    super(props);
    console.log("VMForm constructor");
    this.handleSubmit = this.handleSubmit.bind(this);
    this.getPool = this.getPool.bind(this);
    this.onInputTextChange = this.onInputTextChange.bind(this);
    this.onInputNumberChange = this.onInputNumberChange.bind(this);
    this.onISOOptionChange = this.onISOOptionChange.bind(this);
    this.onNetworkOptionChange = this.onNetworkOptionChange.bind(this);
 //   this.onHookChange = this.onHookChange.bind(this);
    this.onTemplateOptionChange = this.onTemplateOptionChange.bind(this);

    this.state = {
      'pool-select': '',
      template: null,
      'storage-select': '',
      network: '',
      fullname: '',
      username: '',
      hostname: '',
      password: '',
      password2: '',
      name_description: '',
      name_label: '',
      vcpus: 1,
      ram: 256,
      hdd: 9,
      networkType: null,
      ip: '',
      netmask: '',
      gateway: '',
      dns0: '',
      dns1: '',
      iso: '',
      hooks: {},

    };
  }




  onInputTextChange(e) {
    console.log("Text change: ",e.target.name,  e.target.value);
    const form = this.state;
    form[e.target.name] = e.target.value;
    this.setState(form);
  }

  onInputNumberChange(e) {
    const form = this.state;
    const newVal = e.target.value.trim();
    form[e.target.name] = newVal !== '' ? parseInt(newVal, 10) : '';
    this.setState(form);
  }

  onISOOptionChange(option)
  {
    const form = this.state;
    form['iso'] = option;
    this.setState(form)
  }

  onNetworkOptionChange(option)
  {
    const form = this.state;
    form.network = option;
    const currentNetwork = this.props.networks.find(network => network.uuid === form.network);
    if (!form.networkType) { //Guess network type from metadata
      if (currentNetwork && currentNetwork.other_config) {
        const {other_config} = currentNetwork;
        form.networkType = (other_config.gateway ? 'static' : 'dhcp');
        if (form.networkType === 'static') {
          form.gateway = other_config.gateway;
          if (other_config.netmask) {
            form.netmask = other_config.netmask;
          }
          if (other_config.ip_begin) {
            form.ip = other_config.ip_begin;
          }
        }
      }
    }
    this.setState(form);
  }

  onTemplateOptionChange(option)
  {
    console.log("Template option change: ", option);
    const form = this.state;
    form.template = option;
    if (!form.name_label)
      form.name_label = this.props.templates.filter(row =>
        row.get('uuid') === option)
        .first().get('name_label');

    this.setState(form);

  }
/*

  onHookChange(name, option) {
    return event => {
      const hooks = this.state.hooks;
      if (typeof option === 'boolean') {
        if (option) {
          hooks[name] = hooks[name] || {};
          getHooks(this.getTemplate())[name].options
            .forEach(op => {
              hooks[name][op.field] = hooks[name][op.field] || op.default_value;
            });
          hooks[name].enabled = true;
        } else {
          hooks[name].enabled = false;
        }
      } else {
        hooks[name][option] = event.target.value;
      }
      this.setState({ hooks });
    };
  }
*/
  getPool() {
    return this.props.pools.find(pool => pool.uuid === this.state['pool-select']);
  }

  handleSubmit(e) {
    e.preventDefault();
    this.props.onSubmit(this.state);

  }

  render() {
    const form = this.state;

    const currentPool = this.getPool();
    const currentTemplate = this.props.templates.find(tmpl => tmpl.uuid === this.state.template);
    const currentNetwork = this.props.networks.find(net => net.uuid === this.state.network);
  //  const currentHooks = getHooks(currentTemplate);
    console.log(form);
    return (
      <AvForm ref={(ref) => {this.formRef = ref}}  className={styles.vmForm} onValidSubmit={this.handleSubmit}>
        <h4 style={{ margin: '20px'}}><FormattedMessage {...messages.infrastructure} /></h4>
        <VMInput.Pool pools={this.props.pools} selected={form['pool-select']} onChange={this.onInputTextChange} />
        {form['pool-select'] && (
          <React.Fragment>
            <VMInput.Template templates={this.props.templates} onChange={this.onTemplateOptionChange}/>
            <VMInput.Storage storages={getStorageResources(currentPool)} selected={form['storage-select']} onChange={this.onInputTextChange} />
            <VMInput.Network
              networks={this.props.networks}
              onChange={this.onNetworkOptionChange}
              required={currentTemplate && currentTemplate.os_kind}
            />
            <VMInput.Name name={form.name_label} onChange={this.onInputTextChange}/>
            <VMInput.Description description={form.name_description} onChange={this.onInputTextChange} />
          </React.Fragment>
          )}
        {(currentTemplate && currentTemplate.os_kind) &&  (
          <div>
        <h4 style={{margin: '20px'}}><FormattedMessage {...messages.account} /></h4>
        <VMInput.Fullname fullname={form.fullname} onChange={this.onInputTextChange} />
        <VMInput.Link username={form.username} hostname={form.hostname} onChange={this.onInputTextChange} />
        <VMInput.Passwords password={form.password} password2={form.password2} onChange={this.onInputTextChange} formRef={this.formRef} />

          </div>)}
        {(currentTemplate && !currentTemplate.os_kind) && (
            <div>
              <VMInput.ISO isos={this.props.isos} onChange={this.onISOOptionChange} />
            </div>)}



        <h4><FormattedMessage {...messages.resources} /></h4>
        <div className="form-inline" style={{ paddingLeft: '20px' }}>
          <div className="col-sm-12 form-group">
          <VMInput.CPU className="col-sm-4 col-lg-4" vcpus={form.vcpus} onChange={this.onInputNumberChange} />
          <VMInput.RAM className="col-sm-4 col-lg-4" ram={form.ram} onChange={this.onInputNumberChange} />
          <VMInput.HDD className="col-sm-4 col-lg-4" hdd={form.hdd} onChange={this.onInputNumberChange} />
          </div>
        </div>
        {currentTemplate && currentTemplate.os_kind && currentNetwork &&  (
          <div>
            <h4><FormattedMessage {...messages.network} /></h4>
            <VMInput.Connection networkType={form.networkType}
                                ip={form.ip}
                                gateway={form.gateway}
                                netmask={form.netmask}
                                dns0={form.dns0}
                                dns1={form.dns1}
                                onChange={this.onInputTextChange}
            />
          </div>
          )}

        {/*
        <h4><FormattedMessage {...messages.hooks} /></h4>
        {
          Object.keys(currentHooks)
            .map(hookName => ({ ...currentHooks[hookName], hookName }))
            .map(hook =>
              <VMInput.Hook key={hook.hookName} {...hook} selected={form.hooks[hook.hookName]} onChange={this.onHookChange} />)
        }
        <br />
         */}
        <input type="submit" className="btn btn-lg btn-primary btn-block" />
      </AvForm>
    );
  }
}

export default VMForm;
