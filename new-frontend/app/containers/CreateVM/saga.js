import { all, call, put, select, spawn, fork, takeEvery, cancel } from 'redux-saga/effects';
import { LOCATION_CHANGE } from 'react-router-redux';
import { CREATE_VM } from './constants';
import { setPools } from './actions';
import { makeSelectPools } from './selectors';
import { info, suc, err } from 'containers/App/actions';
import localStorage from 'store';
import poollist from 'api/poollist';
import createvm from 'api/createvm';

export function* getPoolList() {
  const currentPools = yield select(makeSelectPools());
  if (currentPools.size === 0) {
    const response = yield call(poollist);
    if (response.data) {
      yield put(setPools(response.data));
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
    req_data['template'] = form['template-select'];
    req_data['storage'] = form['storage-select'];
    req_data['network'] = form['network-select'];
    req_data['hostname'] = form['hostname'];
    req_data['username'] = form['username'];
    req_data['password'] = form['password'];
    req_data['fullname'] = form['fullname'];
    req_data['os_kind'] = 'ubuntu xenial'; //Temporary
    req_data['mode'] = 'pv'; //ORLY
    req_data['vdi_size'] = form['hdd'] * 1024; //Disk size in megabytes
    req_data['partition'] = "/-" +  req_data['vdi_size'] + "-";
    req_data['name_label'] = form['vm-description'];
    req_data['ram_size'] = form['ram'];
    req_data['mirror_url'] = 'http://mirror.corbina.net/ubuntu';


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
  yield all ([getPoolList()]);
  yield takeEvery(CREATE_VM, runCreateVM);

}

