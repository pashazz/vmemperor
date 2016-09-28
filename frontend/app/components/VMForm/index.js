/**
*
* Vmform
*
*/
import React, { PropTypes as T } from 'react';

import { FormattedMessage } from 'react-intl';
import messages from './messages';
import styles from './styles.css';
import VMInput from './helpers';

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

class VMForm extends React.Component { // eslint-disable-line react/prefer-stateless-function
  static propTypes = {
    pools: T.any.isRequired,
    onSubmit: T.func.isRequired,
  }

  constructor(props) {
    super(props);

    this.handleSubmit = this.handleSubmit.bind(this);
    this.getPool = this.getPool.bind(this);
    this.getTemplate = this.getTemplate.bind(this);
    this.onInputTextChange = this.onInputTextChange.bind(this);
    this.onInputNumberChange = this.onInputNumberChange.bind(this);
    this.onHookChange = this.onHookChange.bind(this);

    this.state = {
      'pool-select': '',
      'template-select': '',
      'storage-select': '',
      'network-select': '',
      fullname: '',
      username: '',
      hostname: '',
      password: '',
      password2: '',
      'vm-description': '',
      vcpus: 1,
      ram: 256,
      hdd: 9,
      hooks: {},
    };
  }

  onInputTextChange(e) {
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

  getPool() {
    return this.props.pools.find(pool => pool.id === this.state['pool-select']);
  }

  getTemplate() {
    const selectedPool = this.getPool();
    if (!selectedPool) {
      return null;
    }
    return selectedPool.templates_enabled.find(template => template.uuid === this.state['template-select']);
  }

  handleSubmit(e) {
    e.preventDefault();
    this.props.onSubmit(this.state);
  }

  render() {
    const form = this.state;

    const currentPool = this.getPool();
    const currentTemplate = this.getTemplate();
    const currentHooks = getHooks(currentTemplate);

    return (
      <form role="form" className={styles.vmForm} onSubmit={this.handleSubmit}>
        <h4><FormattedMessage {...messages.infrastructure} /></h4>
        <VMInput.Pool pools={this.props.pools} selected={form['pool-select']} onChange={this.onInputTextChange} />
        <VMInput.Template templates={getTemplates(currentPool)} selected={form['template-select']} onChange={this.onInputTextChange} />
        <VMInput.Storage storages={getStorageResources(currentPool)} selected={form['storage-select']} onChange={this.onInputTextChange} />
        <VMInput.Network networks={getNetworks(currentPool)} selected={form['network-select']} onChange={this.onInputTextChange} />

        <h4><FormattedMessage {...messages.account} /></h4>
        <VMInput.Fullname fullname={form.fullname} onChange={this.onInputTextChange} />
        <VMInput.Link username={form.username} hostname={form.hostname} onChange={this.onInputTextChange} />
        <VMInput.Passwords password={form.password} password2={form.password2} onChange={this.onInputTextChange} />
        <VMInput.Description description={form['vm-description']} onChange={this.onInputTextChange} />

        <h4><FormattedMessage {...messages.resources} /></h4>
        <div className="row" style={{ paddingBottom: '10px' }}>
          <VMInput.CPU className="col-sm-4 col-lg-4" vcpus={form.vcpus} onChange={this.onInputNumberChange} />
          <VMInput.RAM className="col-sm-4 col-lg-4" ram={form.ram} onChange={this.onInputNumberChange} />
          <VMInput.HDD className="col-sm-4 col-lg-4" hdd={form.hdd} onChange={this.onInputNumberChange} />
        </div>

        <h4><FormattedMessage {...messages.hooks} /></h4>
        {
          Object.keys(currentHooks)
            .map(hookName => ({ ...currentHooks[hookName], hookName }))
            .map(hook =>
              <VMInput.Hook key={hook.hookName} {...hook} selected={form.hooks[hook.hookName]} onChange={this.onHookChange} />)
        }
        <br />
        <input type="submit" className="btn btn-lg btn-primary btn-block" />
      </form>
    );
  }
}

export default VMForm;
