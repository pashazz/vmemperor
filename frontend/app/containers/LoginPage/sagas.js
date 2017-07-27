import { call, put, select } from 'redux-saga/effects';
import { setPools } from './actions';
import { selectPools } from './selectors';
import vmempAPI from 'api/vmemp-api';

// Individual exports for testing
export function* getData() {
  const currentPools = yield select(selectPools());
  if (currentPools.length === 0) {
    const response = yield call(vmempAPI.pool.index);
    if (response.data) {
      yield put(setPools(response.data));
    }
  }
}

// All sagas to be loaded
export default [
  getData,
];
