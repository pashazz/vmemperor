import React, {PureComponent, useMemo} from 'react';
import NextTable from 'react-bootstrap-table-next';
import {useMutation, useQuery} from "react-apollo-hooks";
import {NetAttach, NetworkList, NetworkListFragment, VmInfoFragment} from "../../../generated-models";
import {ColumnType} from "../../../containers/StatefulTable";

const columns: ColumnType<NetworkListFragment.Fragment>[] = [
  {
    dataField: 'nameLabel',
    text: 'Name',
  },
  {
    dataField: 'nameDescription',
    text: 'Description',
  },

];

interface Props {
  vm: VmInfoFragment.Fragment,
}

const NetworkAttach = ({vm: {uuid, interfaces}}: Props) => {
  const onAttach = useMutation<NetAttach.Mutation, NetAttach.Variables>(NetAttach.Document);
  const {data: {networks}} = useQuery<NetworkList.Query, NetworkList.Variables>(NetworkList.Document);
  const notYetConnectedList = useMemo(() => (
      networks.filter(network =>
        interfaces.every(item => item.network.uuid !== network.uuid))),
    [interfaces, networks]);
  const onDoubleClick = async (e, row: NetworkListFragment.Fragment, rowIndex) => {
    const taskId = await onAttach({
      variables: {
        vmUuid: uuid,
        netUuid: row.uuid,
      }
    });
    console.log(`Network connection... taskId: ${taskId.data.netAttach.taskId}`)
  };

  return (
    <div>
      <NextTable
        columns={columns}
        rowEvents={{
          onDoubleClick
        }}
        data={notYetConnectedList}
        keyField="uuid"
      />
    </div>
  )
};

export default NetworkAttach;
