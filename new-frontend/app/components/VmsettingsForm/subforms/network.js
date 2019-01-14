import React, { PureComponent, Fragment } from 'react';
import T from 'prop-types';

import {connect} from 'react-redux';
import {compose} from 'redux';
import {createStructuredSelector} from 'reselect';

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

import ControlledTable, {selectors} from 'containers/ControlledTable';
import NetworkAttach from './networkAttach';

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
    onAttach: T.func.isRequired,
    onDetach: T.func.isRequired,
    requestNet: T.func.isRequired,
    netList: T.array.isRequired,
  };

  constructor(props){
  super(props);

  this.state = {
    netAttach: false,
    detachDisabled: false,
  };
    this.toggleAttach = this.toggleAttach.bind(this);
    this.onDetach = this.onDetach.bind(this);
}

  onDetach()
  {
    for (const ref of this.props.table_selection)
    {
      console.log("ref: ", ref);
      const net = this.props.networks.filter(row => {console.log("row.key=", row.key, "ref=", ref);
      return  row.key === ref})[0]['network'];
      this.props.onDetach(net);
    }
  }
  toggleAttach()
  {

    this.setState(
      {netAttach: !this.state.netAttach}
    );
  }
  static getDerivedStateFromProps(props, state)
  {
    if (!props.table_selection)
      return state;
    return {
      ...state,
      detachDisabled: props.table_selection.length === 0
    }
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
            <CardFooter>
              <Button size="lg" color="success" onClick={this.toggleAttach} active={this.state.netAttach} aria-pressed="true">
                Attach network
              </Button>
              <Button size="lg" color="danger" disabled={this.state.detachDisabled} onClick={this.onDetach}>
                Detach
              </Button>
               <Collapse id="collNet"
                isOpen={this.state.netAttach}>
                <UncontrolledAlert color='info'>Double-click to attach a network</UncontrolledAlert>
                 {<NetworkAttach
                  fetch={this.props.requestNet}
                  data={this.props.netList}
                  onAttach={(uuid) => {
                    this.props.onAttach(uuid);
                  }}
                  />}
              </Collapse>

            </CardFooter>
          </Card>
        </Col>
      </Row>
    </Fragment>);
  }


}

const mapStateToProps = createStructuredSelector({
  table_selection: selectors("networks").makeSelectionSelector()
});
const mapDispatchToProps = {};
const withConnect = connect(mapStateToProps, mapDispatchToProps);

export default compose(withConnect)(Network);




