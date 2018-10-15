import { all, call, put, select, spawn, fork, takeEvery, cancel } from 'redux-saga/effects';
import { LOCATION_CHANGE } from 'react-router-redux';
import {CREATE_VM} from './constants';
import { setPools, setIsos, setNetworks, setTemplates } from './actions';
import {makeSelectPools, makeSelectIsos, makeSelectNetworks, makeSelectTemplates} from './selectors';
import { info, suc, err } from 'containers/App/actions';
import localStorage from 'store';
import poollist from 'api/poollist';
import isolist from 'api/isolist';
import createvm from 'api/createvm';
import {netlist} from 'api/net';
import tmpllist from 'api/tmpllist';

export function* getPoolList() {
  const currentPools = yield select(makeSelectPools());
  if (currentPools.size === 0) {
    const response = yield call(poollist);
    if (response.data) {
      yield put(setPools(response.data));
    }
  }
}

export function* getIsoList() {
  const currentIsos = yield select(makeSelectIsos());
  if (currentIsos.size === 0) {
    const response = yield call(isolist);
    if (response.data) {
      yield put(setIsos(response.data));
    }
  }
}

export function* getTmplList() {
  const currentTmpls = yield select(makeSelectTemplates());
  if (currentTmpls.size === 0) {
    const response = yield call(tmpllist);
    if (response.data) {
      yield put(setTemplates(response.data));
    }
  }
}

export function* getNetworkList() {
  const currentNetworks = yield select(makeSelectNetworks());
  if (currentNetworks.size === 0) {
    const response = yield call(netlist);
    if (response.data) {
      yield put(setNetworks(response.data));
    }
  }
}



function updateStorage({ uuid = false }) {
  if (uuid) {
    const vms = localStorage.get('vm-history') || {};
    localStorage.set('vm-history', { ...vms, [uuid]: {} });
  }
}

export function* runCreateVM(action) {
  const { form } =  action;
  console.log(`Trying to create ${form.hostname}`);
  try {
    let req_data = {};
    req_data['template'] = form.template;
    req_data['name_label'] = form.name_label;
    req_data['name_description'] = form.name_description;
    req_data['storage'] = form['storage-select'];
    req_data['network'] = form['network'];
    req_data['hostname'] = form['hostname'];
    req_data['username'] = form['username'];
    req_data['password'] = form['password'];
    req_data['fullname'] = form['fullname'];
    req_data['iso'] = form['iso'];
    req_data['vdi_size'] = form['hdd'] * 1024; //Disk size in megabytes
    req_data['partition'] = "/-" +  req_data['vdi_size'] + "-";
    req_data['ram_size'] = form['ram'];
    req_data['vcpus'] = form['vcpus'];

    if (form.networkType === 'static') {
      req_data.ip = form.ip;
      req_data.netmask = form.netmask;
      req_data.gateway = form.gateway;
      req_data.dns0 = form.dns0;
      req_data.dns1 = form.dns1;
    }


    const response = yield call(createvm, req_data);
    if (response.data) {
      console.log(`For ${form.hostname}: ${response.data.details}`);
      updateStorage(response.data);
    }
  }
  catch (e)
  {
    console.log("CreateVM error: ", e)
  }

  yield spawn(getPoolList);
}

export default function* rootSaga() {
  yield all ([getPoolList(), getIsoList(), getNetworkList(), getTmplList()]);
  yield takeEvery(CREATE_VM, runCreateVM);

}

