 import { takeEvery, call, put, select } from 'redux-saga/effects';

// Individual exports for testing
import {VNC_REQUESTED} from "./constants";
import { vnc } from 'api/vm';
 import {vncAcquire, vncError} from "./actions";

function* onVncRequested(action)
{
  try {
    const url = yield call(vnc, action.uuid);
    yield put(vncAcquire(url.data, action.uuid));
  }
  catch (e)
  {
    yield put(vncError(e.response.data));
  }

}

export default function* rootSaga() {
  yield takeEvery(VNC_REQUESTED, onVncRequested);
}
