import BluePromise from "bluebird";
import {vminfo} from 'api/vm';
const myFetcher = (fillVms) => (fetchFunc) => async (page, sizePerPage) => {
  const list = await fetchFunc(page, sizePerPage);
  return await BluePromise.map(list.data, async (record) => {
    const {VMs, ...rest} = record;
    if (fillVms) {
      rest.VMs = await BluePromise.map(VMs, async (uuid) => {
          try {
            const ret = await vminfo(uuid);
            return ret.data;
          }
          catch (e) {
            return {
              uuid,
              name_label: "Unknown VM"
            }
          }


        }
      );
    }
    else {
      rest.VMs = VMs.map(vm => {
        return {uuid: vm, name_label: ""}
      });
    }
    console.log("Rest: ", rest);
    return rest;
  });
};

export default myFetcher;
