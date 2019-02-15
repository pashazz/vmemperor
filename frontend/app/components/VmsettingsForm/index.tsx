/**
 *
 * VmsettingsForm
 *
 */

import React, {useCallback, useState} from 'react';
import {VmInfo} from "../../generated-models";
import Power from './subforms/power';
//import Storage from './subforms/storage';
//import Network from './subforms/network';
// import styled from 'styled-components';

import {FormattedMessage} from 'react-intl';
import messages from './messages';
import {
  Nav,
  NavItem,
  Badge,
  NavLink,
  TabContent,
  TabPane,
  Row,
  Col,
  Card,
  CardTitle,
  CardText,
  Button
} from 'reactstrap';
import classnames from 'classnames';

import T from 'prop-types';
import Vncview from '../../containers/Vncview/Loadable';
import Vm = VmInfo.Vm;


interface Props {
  vm: Vm;
}

enum Tab {
  Power = 'power',
  VNC = 'vnc',
  Storage = 'storage',
  Network = 'network',

}


const VmsettingsForm = ({vm}: Props) => {
  const [activeTab, setActiveTab] = useState(Tab.Power);
  const [vncActivated, setVncActivated] = useState(false);

  const toggleTab = useCallback((tab: Tab) => {
    if (activeTab !== tab) {
      setActiveTab(tab);
    }
    if (tab === Tab.VNC && !vncActivated) {
      setVncActivated(true);
    }
  }, [activeTab, vncActivated]);


  return (
    <div>
      <h3 className="text-center">{vm.nameLabel} <Badge color="primary">{vm.powerState}</Badge>
        {vm.osVersion &&
        (<Badge color="success">{vm.osVersion.name}</Badge>)}
      </h3>

      <Nav tabs>
        <NavItem>
          <NavLink
            className={classnames({active: activeTab === Tab.Power})}
            onClick={() => {
              toggleTab(Tab.Power);
            }}
          >
            Power
          </NavLink>
        </NavItem>

        <NavItem>
          <NavLink
            className={classnames({active: activeTab === Tab.VNC})}
            onClick={() => {
              toggleTab(Tab.VNC);
            }}
          >
            VNC
          </NavLink>
        </NavItem>


        <NavItem>
          <NavLink
            className={classnames({active: activeTab === Tab.Storage})}
            onClick={() => {
              toggleTab(Tab.Storage);
            }}
          >
            Storage
          </NavLink>
        </NavItem>
        <NavItem>
          <NavLink
            className={classnames({active: activeTab === Tab.Network})}
            onClick={() => {
              toggleTab(Tab.Network);
            }}
          >
            Network
          </NavLink>
        </NavItem>
      </Nav>
      <TabContent activeTab={activeTab}>
        <TabPane tabId={Tab.Power}>
          <Row>
            <Col sm="12">
              <Power vm={vm}/>
            </Col>
          </Row>
        </TabPane>
        <TabPane tabId={Tab.Storage}>
          <Row>
            <Col sm="12">
              {/*<Storage
                  vm={vm}/>*/}
            </Col>
          </Row>
        </TabPane>
        <TabPane tabId={Tab.VNC}>
          {/*
            vncActivated && (
              <Vncview uuid={uuid}/>
            ) || (<h1>NO VNC HERE</h1>)
*/}
        </TabPane>
        <TabPane tabId={Tab.Network}>
          <Row>
            <Col sm="12">
              {/*<Network
                  data={vm}
                />*/}
            </Col>
          </Row>
        </TabPane>
      </TabContent>
    </div>
  )
};

export default VmsettingsForm;
