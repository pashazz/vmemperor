import { take, call, put, select, takeEvery } from 'redux-saga/effects';
import {startStopVm } from 'api/vm';
import {VM_HALT, VM_RUN, VM_RUN_ERROR} from "./constants";
import {vm_run_error} from "./actions";
import React from 'react';
import { Map } from 'immutable';

import ErrorCard from '../../components/ErrorCard';
import { actions } from 'react-redux-toastr';

const actionHandlers = Map({
    [VM_RUN]: {
      onError: vm_run_error,
      handler: function* (action) {
        const data = yield  call(startStopVm, action.uuid, true);
        console.log('vmRun: data:', data);
      }
    },
  [VM_HALT]: {
      onError: vm_run_error,
    handler: function* (action) {
      const data = yield  call(startStopVm, action.uuid, false);
      console.log('vmHalt: data:', data);
    }
  }
  });

function* handleActions (action){
  const handler = actionHandlers.get(action.type);
  try {
    yield handler.handler(action);
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
          yield put(handler.onError(e.response.data.details));
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

function* handleErrors(action)
{
  let errorHeader = null;
  if (action.type === VM_RUN_ERROR)
  {
    // select VM name from store by ref
    const selector = (state) => state.get('app').get('vm_data');
    const vm_data_map = yield select(selector);
    const vm_array = vm_data_map.valueSeq().toArray();
    let vmName = null;
    for (let value of vm_array)
    {
      console.log(value);
      if (value.ref === action.ref)
      {
        vmName = value.name_label;
        break;
      }
    }
    errorHeader = "Sorry, we couldn't launch VM " + vmName;
  }
  const {errorType, errorDetailedText} = action;
  yield put(actions.add(
    {
      id: action.ref,
      type: 'error',
      title: errorHeader,
      message: errorType + ": " + errorDetailedText
    }));
}

export default function* rootSaga() {
  yield takeEvery(VM_RUN, handleActions);
  yield takeEvery(VM_HALT, handleActions);
  yield takeEvery(VM_RUN_ERROR, handleErrors);
  //VM_HALT_ERROR: todo!

};
