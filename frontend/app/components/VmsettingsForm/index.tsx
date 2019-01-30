/**
*
* VmsettingsForm
*
*/

import React from 'react';
import {VmInfo} from "../../generated-models";
import Power from './subforms/power';
//import Storage from './subforms/storage';
//import Network from './subforms/network';
// import styled from 'styled-components';

import { FormattedMessage } from 'react-intl';
import messages from './messages';
import { Nav, NavItem, Badge, NavLink, TabContent, TabPane, Row, Col, Card, CardTitle, CardText, Button} from 'reactstrap';
import classnames from 'classnames';

import T from 'prop-types';
import Vncview from '../../containers/Vncview/Loadable';
import Vm = VmInfo.Vm;


interface Props{
  vm: Vm;
  update: () => void;
}

enum Tab {
  Power = 'power',
  VNC = 'vnc',
  Storage = 'storage',
  Network = 'network',

}

interface  State{
  activeTab : Tab,
  vncActivated : boolean
}

class VmsettingsForm extends React.PureComponent<Props, State> { // eslint-disable-line react/prefer-stateless-function
  constructor(props) {
    super(props);
    this.toggle = this.toggle.bind(this);
    this.state = {
      activeTab: Tab.Power,
      vncActivated: false,
    }
  }

  componentDidMount(): void {
    this.props.update();

  }

  toggle(tab) {
    console.log("Toggled tab", tab);
    if (this.state.activeTab !== tab) {
      this.setState({
        activeTab: tab
      });
      if (tab === Tab.VNC && !this.state.vncActivated) {
        this.setState({
          vncActivated: true,
        });
      }
    }

  }

  render() {
    const {vm} = this.props;
    console.log("Current tab:", this.state.activeTab);
    return (
      <div>
        <h3 className="text-center">{vm.nameLabel} <Badge color="primary">{vm.powerState}</Badge>
          {vm.osVersion &&
          (<Badge color="success">{vm.osVersion.name}</Badge>)}
        </h3>

        <Nav tabs>
          <NavItem>
            <NavLink
              className={classnames({active: this.state.activeTab === Tab.Power})}
              onClick={() => {
                this.toggle(Tab.Power);
              }}
            >
              Power
            </NavLink>
          </NavItem>

          <NavItem>
            <NavLink
              className={classnames({active: this.state.activeTab === Tab.VNC})}
              onClick={() => {
                console.log("CLOCK");
                this.toggle(Tab.VNC);
              }}
            >
              VNC
            </NavLink>
          </NavItem>


          <NavItem>
            <NavLink
              className={classnames({active: this.state.activeTab === Tab.Storage})}
              onClick={() => {
                this.toggle(Tab.Storage);
              }}
            >
              Storage
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink
              className={classnames({active: this.state.activeTab === Tab.Network})}
              onClick={() => {
                this.toggle(Tab.Network);
              }}
            >
              Network
            </NavLink>
          </NavItem>
        </Nav>
        <TabContent activeTab={this.state.activeTab}>
          <TabPane tabId="power">
            <Row>
              <Col sm="12">
                <Power vm={vm}/>
                />
              </Col>
            </Row>
          </TabPane>
          <TabPane tabId="storage">
            <Row>
              <Col sm="12">
                {/*<Storage
                  vm={vm}/> */}
              </Col>
            </Row>
          </TabPane>
          <TabPane tabId="vnc">
            {/*
              this.state.vncActivated && (
                <Vncview uuid={this.props.data.uuid}/>
              ) || (<h1>NO VNC HERE</h1>)
            */}
          </TabPane>
          <TabPane tabId="network">
            <Row>
              <Col sm="12">
                {/*<Network
                  data={vm}
                />*/}
              </Col>
            </Row>
          </TabPane>
          <TabPane tabId="2">
            <Row>
              <Col sm="6">
                <Card body>
                  <CardTitle>Special Title Treatment</CardTitle>
                  <CardText>With supporting text below as a natural lead-in to additional content.</CardText>
                  <Button>Go somewhere</Button>
                </Card>
              </Col>
              <Col sm="6">
                <Card body>
                  <CardTitle>Special Title Treatment</CardTitle>
                  <CardText>With supporting text below as a natural lead-in to additional content.</CardText>
                  <Button>Go somewhere</Button>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </TabContent>
      </div>
    )
  }
}

export default VmsettingsForm;
