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
  const response = yield call(createvm, form);
  if (response.data) {
    console.log(`For ${form.hostname}: ${response.data.details}`);
    updateStorage(response.data);
  }
  if (response.err) {
    yield put(err(`Creation failed for ${form.hostname}`));
  }
  yield spawn(getPoolList);
}

export default function* rootSaga() {
  yield all ([getPoolList()]);
  yield takeEvery(CREATE_VM, runCreateVM);

}

