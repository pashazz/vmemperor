import React, { PureComponent, Fragment } from 'react';
import T from 'prop-types';

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

import ControlledTable from 'containers/ControlledTable';

const columns = [
  {
    dataField: 'key',
    text: '#'
  },
  {
    dataField: 'name_label',
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

class Network extends PureComponent {
  constructor(props){
  super(props);

  this.state = {
    networkAttach: false,
    refreshWidgets: false,
  };
}

  render()
  {
    const NetworkTable = ControlledTable("networks");
    return (<Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <CardBody>
              <CardTitle>Networks</CardTitle>
              <CardText>
                <NetworkTable
                  columns={columns}
                  data={this.props.networks}
                  keyField="key"
                  />
              </CardText>
            </CardBody>

          </Card>
        </Col>
      </Row>
    </Fragment>);
  }

  static VMNetworkShape = T.shape( //Network information for this component
    {
      //uuid: T.string.isRequired,
      key: T.string.isRequired,
      name_label: T.string.isRequired,
      attached: T.bool.isRequired,
      ip: T.string,
      MAC: T.string,

    });
    static propTypes = {
      networks: T.arrayOf(Network.VMNetworkShape).isRequired,
    }

}



export default Network;

