 import { takeEvery, take,  call, put, select } from 'redux-saga/effects';

// Individual exports for testing


import {VDI_ATTACH, VDI_DETACH, VM_CONVERT, VM_REQUEST_DISKINFO, VM_WATCH} from "./constants";
import {VM_RUN_ERROR, VMLIST_MESSAGE} from "../App/constants";
 import {convert} from "../../api/vm";
 import {vm_run_error} from "../App/actions";
 import {handleVMErrors} from '../App/saga';
 import {diskInfo} from "../../api/vm";
 import { attachdetachvdi} from "../../api/vdi";
 import {setDiskInfo, requestDiskInfo as actRequestDiskInfo} from "./actions";

 const actionHandlers = {
  [VM_CONVERT]: {
    onError: vm_run_error,
    handler: function* (args)
    {
      const data = yield call(convert, args.uuid, args.mode);
      console.log("convert: data:", data);
    }
  },
   [VDI_DETACH]: {
    onError: vm_run_error,
     handler: function* (args)
     {
       const data = yield call(attachdetachvdi, args.vm, args.vdi, 'detach');
       console.log("detach: data", data);
     }
   },

   [VDI_ATTACH]: {
   onError: vm_run_error,
     handler: function* (args)
   {
     console.log("handle attach");
     const data = yield call(attachdetachvdi, args.vm, args.vdi, 'attach');
     console.log("attach: data", data);
   }
 }
};


 function* handleActions(action) {
   const {type, ...rest} = action;
   const handler = actionHandlers[type];
   console.log("vmsettings: handle " + type);
   try {
     yield handler.handler(rest);
   }
   catch (e) {
     if (e.response) {
       console.log(e.response);
       if (e.response.status === 400) {
         //Handle error
         if (e.response.data.details) {
           yield put(handler.onError(e.response.data.details));
         }
         else {
           console.error("Unhandled Response Error: ", e.response)
         }
       }
     }
   }


 }


 function* requestDiskInfo(action) {
   const { uuid } = action;
   const response = yield call(diskInfo, uuid);
   console.log("Disk info:", response.data);
   yield put(setDiskInfo(response.data));


 }

 function* vmWatch(action)
 {
   const {uuid} = action;
   let disks = true;
   while(true)
   {
     const action = yield take(VMLIST_MESSAGE);
     const {message} = action;
     let value = null;
     switch(message.type)
     {
       case 'change':
         value = message.new_val;
         break;
       default:
         continue;
     }
     if (value.uuid !== uuid)
       continue;

     if (value.disks !== disks)
     {
       yield put(actRequestDiskInfo(uuid, true));
     }

   }
 }


export default function* rootSaga() {
  // See example in containers/HomePage/saga.js
  yield takeEvery(VM_CONVERT, handleActions);
  yield takeEvery(VDI_DETACH, handleActions);
  yield takeEvery(VDI_ATTACH, handleActions);
  yield takeEvery(VM_REQUEST_DISKINFO, requestDiskInfo);
  yield takeEvery(VM_WATCH, vmWatch);
}
