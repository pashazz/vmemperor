/**
*
* Vmform
*
*/
import React from 'react';


import * as Yup from "yup";
import {boolean, number, object, string} from "yup";

import {AvForm} from 'availity-reactstrap-validation';
import {Formik, FormikProps} from "formik";
import {HDD_SIZE_GB_MAX, RAM_MB_MAX, RAM_MB_MIN, VCPU_MAX} from "../../utils/constants";
import {Option, OptionShape} from "../../hooks/form";
import VMForm from "./form";
import {Values} from "./props";

/*
export interface SelectionProps {
  selected: string;
  onChange: (e: ChangeEvent) => any;
}



interface State {
  pool: PoolListFragment.Fragment;
  template: TemplateListFragment.Fragment;
  storage: StorageListFragment.Fragment;
  network: NetworkListFragment.Fragment;
  fullname: string;
  username: string;
  password: string;
  password2: string;
  hostname: string;
  nameLabel: string;
  nameDescription: string;
  vcpus: number;
  ram: number; //MB
  hdd: number; //GB
  ip: string;
  netmask: string;
  gateway: string;
  dns0: string;
  dns1: string;
  iso: string;
}

interface Action {
  fieldName: string;
  fieldData: string;

}

type VMFormReducer = Reducer<State, Action>;

const VMFormContainer : React.FunctionComponent = () => {
  const formRef = useRef(null);
  const reducer : VMFormReducer = (state, action) => {
    return state;
  };

  const initialState : State = {
    pool: null,
    template: null,
    storage: null,
    network: null,
    fullname: '',
    username: '',
    hostname: '',
    password: '',
    password2: '',
    nameDescription: '',
    nameLabel: '',
    vcpus: 1,
    ram: 1024,
    hdd: 9,
    ip: '',
    netmask: '',
    gateway: '',
    dns0: '',
    dns1: '',
    iso: '',
  };


  const [state, dispatch ] = useReducer<VMFormReducer>(reducer, initialState);

  const onInputChange = (e : ChangeEvent<HTMLSelectElement>) =>
  {
    dispatch({
      fieldName: e.target.id,
      fieldData: e.target.value,
    });
  }

  const onOptionChange  = (optionName : string ) => (option: string) => {

  };
  return (
    <AvForm ref={formRef}  className={styles.vmForm} onValidSubmit={this.handleSubmit}>
      <h4 style={{ margin: '20px'}}><FormattedMessage {...messages.infrastructure} /></h4>
      <Pool selected={state.pool} onChange={onInputChange} pools={pools.}/>
      {state.pool && (
        <React.Fragment>
          <VMInput.Template  onChange={onOptionChange("template")}/>
          <VMInput.Storage  selected={state.storage} onChange={onInputChange} />
          <VMInput.Network
            onChange={onInputChange}
            required={state.template && !state.iso }
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


      <input type="submit" className="btn btn-lg btn-primary btn-block" />
    </AvForm>
  );
};
*/


const initialValues : Values = {
  pool: null,
  template: null,
  storage: null,
  network: null,
  fullname: '',
  username: '',
  hostname: '',
  password: '',
  password2: '',
  nameDescription: '',
  nameLabel: '',
  vcpus: 1,
  ram: 1024,
  hdd: 9,
  ip: '',
  netmask: '',
  gateway: '',
  dns0: '',
  dns1: '',
  iso: null,
  networkType: null,
  autoMode: false,
};
const IP_REGEX = RegExp('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$');
const HOSTNAME_REGEX = RegExp('^[a-zA-Z0-9]([a-zA-Z0-9-])*$');
const USERNAME_REGEX = RegExp('^[a-z_][a-z0-9_]$');
const PASSWORD_REGEX = RegExp('^[\x00-\x7F]*$');


const VMFormContainer: React.FunctionComponent = () =>
{
  const requiredIpWhenNetwork = (message : string, required = true) => string().when(['autoMode','network', 'networkType'], {
    is: (autoMode, network, networkType) => !network || !networkType || networkType !== 'static',
    then: string().notRequired().nullable(true),
    otherwise: required ? string().matches(IP_REGEX, message).required(): string().matches(IP_REGEX, message)
  });

  const autoModeRequired =  (t) => ({
    is : true,
    then: t().required(),
    otherwise: t().notRequired().nullable(true),
  });

  const networkTypeOptions : Option[] = [
    {
      value: 'dhcp',
      label: 'DHCP'
    },
    {
      value : 'static',
      label: 'Static IP'
    }
  ];
  //Yup.addMethod()
  return (
  <Formik initialValues={initialValues}
          onSubmit={(values: Values) => console.log(values)}
          validationSchema={object().shape<Values>({
            pool: OptionShape().required(),
            autoMode: boolean().required(),
            template: OptionShape().required(),
            storage: OptionShape().required(),
            network: OptionShape().when('autoMode', autoModeRequired(object)),
            networkType: OptionShape().oneOf(networkTypeOptions).when('autoMode', autoModeRequired(object)),
            fullname: string(),
            hostname: string().min(1).max(255).matches(HOSTNAME_REGEX).when('autoMode', autoModeRequired(string)),
            username: string().min(1).max(31).matches(USERNAME_REGEX).when('autoMode', autoModeRequired(string)),
            password: string().min(1).matches(PASSWORD_REGEX).when('autoMode', autoModeRequired(string)),
            password2: string().oneOf([Yup.ref('password'), '']).when('autoMode', autoModeRequired(string)),
            nameDescription: string(),
            nameLabel: string().required(),
            vcpus: number().integer().min(1).max(VCPU_MAX).required(),
            ram: number().integer().min(RAM_MB_MIN).max(RAM_MB_MAX).required(),
            ip: requiredIpWhenNetwork("Enter valid IP"),
            netmask: requiredIpWhenNetwork("Enter valid netmask)"),
            gateway: requiredIpWhenNetwork("Enter valid gateway"),
            dns0: requiredIpWhenNetwork("Enter valid DNS server"),
            dns1: requiredIpWhenNetwork("Enter valid DNS server", false),
            iso: OptionShape().when('autoMode',
              {
                is: false,
                then: object().required(),
                otherwise: object().nullable(true)
              }),
            hdd: number().integer().positive().required().max(HDD_SIZE_GB_MAX),

          })}
          component={VMForm}
  />
  );
};

export default VMFormContainer;
