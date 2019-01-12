import { call, put, select, all } from 'redux-saga/effects';
import { setPools } from './actions';
import { makeSelectPools } from './selectors';
import list_pools from 'api/list_pools';

// Individual exports for testing
export function* getData() {
  const currentPools = yield select(makeSelectPools());
  if (currentPools.length === 0) {
    const response = yield call(list_pools);
    if (response.data) {
      console.log('loginPage: saga: got data: ', response.data);
      yield put(setPools(response.data));
    }
  }
}

// All sagas to be loaded
export default function* rootSaga () {
  yield all([
    getData(),
  ])
}
