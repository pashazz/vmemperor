import { take, call, put, select, takeEvery } from 'redux-saga/effects';
import {startStopVm } from 'api/vm';
import {VM_RUN} from "./constants";
import {vm_run_error} from "./actions";

function* vmRun (action){
  try {
    const data = yield  call(startStopVm, action.uuid, true);
    console.log('vmRun: data:', data);
  }
  catch (e)
  {
    if (e.response)
    {
      console.log(e.response);
      if (e.response.status === 400)
      {
        //Handle error
        if (e.response.data.details)
        {
          yield put(vm_run_error(e.response.data.details));
        }
        else {
          console.error("Unhandled Response Error: ", e.response)
        }
      }
    }
    else {
      console.error(e);
    }
  }

}

export default function* rootSaga() {
  yield takeEvery(VM_RUN, vmRun);
};
