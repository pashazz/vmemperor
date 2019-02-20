import React, {Fragment, useState, useMemo, useCallback} from 'react';


import {checkBoxFormatter} from "../../../utils/formatters";
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardText,
  CardTitle,
  Col,
  Collapse,
  Row,
  UncontrolledAlert
} from 'reactstrap';

import StatefulTable, {ColumnType} from '../../../containers/StatefulTable';
import NetworkAttach from './networkAttach';
import {
  NetAttach,
  NetAttachTableSelect,
  NetAttachTableSelectAll, NetAttachTableSelection, NetDetach,
  VmInfoFragment,
  VmInterfaceFragment
} from "../../../generated-models";
import {useMutation, useQuery} from "react-apollo-hooks";
import {Data} from "popper.js";
import Variables = NetAttach.Variables;

interface DataType {
  id: string;
  nameLabel: string;
  attached: boolean;
  ip?: string;
  MAC: string;
  netUuid: string;
};

type NetColumnType = ColumnType<DataType>;
const columns: NetColumnType[] = [
  {
    dataField: 'id',
    text: '#'
  },
  {
    dataField: 'nameLabel',
    text: 'Name'
  },
  {
    dataField: 'attached',
    text: 'Attached',
    formatter: checkBoxFormatter,
  },
  {
    dataField: 'ip',
    text: 'IP',
  },
  {
    dataField: 'MAC',
    text: 'MAC'
  }

];

interface Props {
  vm: VmInfoFragment.Fragment;

}

const Network: React.FunctionComponent<Props> = ({vm}) => {
  const [netAttach, setNetAttach] = useState(false);

  const tableData: DataType[] = useMemo(() => {
    return vm.interfaces.map(({ip, id, ipv6, network: {nameLabel, uuid}, MAC, attached}: VmInterfaceFragment.Fragment): DataType => {
      return {
        id,
        ip,
        nameLabel,
        MAC,
        attached,
        netUuid: uuid
      }
    })
  }, [vm.interfaces]);

  const onDetach = useMutation<NetDetach.Mutation, NetDetach.Variables>(NetDetach.Document);
  const tableSelection = useQuery<NetAttachTableSelection.Query, NetAttachTableSelection.Variables>(NetAttachTableSelection.Document);
  const selectedData = useMemo(() => tableData.filter(item => tableSelection.data.selectedItems.includes(item.id)), [tableData, tableSelection]);
  const onDetachDoubleClick = useCallback(async () => {
    for (const row of selectedData)
      await onDetach({
        variables: {
          vmUuid: vm.uuid,
          netUuid: row.netUuid,
        }
      })
  }, [selectedData, vm.uuid, tableData]);

  return (<Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <CardBody>
              <CardTitle>Networks</CardTitle>
              <CardText>
                <StatefulTable
                  columns={columns}
                  data={tableData}
                  keyField="id"
                  tableSelectMany={NetAttachTableSelectAll.Document}
                  tableSelectOne={NetAttachTableSelect.Document}
                  tableSelectionQuery={NetAttachTableSelection.Document}
                />
              </CardText>
            </CardBody>
            <CardFooter>
              <Button size="lg" color="success" onClick={() => setNetAttach(!netAttach)} active={netAttach}
                      aria-pressed="true">
                Attach network
              </Button>
              <Button id={'detach-vif'} size="lg" color="danger" disabled={selectedData.length === 0}
                      onClick={onDetachDoubleClick}>
                Detach
              </Button>
              <Collapse id="collNet"
                        isOpen={netAttach}>
                <UncontrolledAlert color='info'>Double-click to attach a network</UncontrolledAlert>
                <NetworkAttach vm={vm}

                />
              </Collapse>

            </CardFooter>
          </Card>
        </Col>
      </Row>
    </Fragment>
  );
};

export default Network;




