import React, {PureComponent} from 'react';
import T, {string} from 'prop-types';
import {Button, Card, CardTitle, CardText, Col, Row, CardFooter,CardBody, CardSubtitle, ButtonGroup} from 'reactstrap';
import FullHeightCard from '../../../components/FullHeightCard';
import {VM_STATE_RUNNING} from "../../../containers/App/constants";

//import DateDiff from 'utils/datediff';

import { FormattedMessage } from 'react-intl';
import messages from  '../messages';
import Playbooks from "../../../containers/Playbooks";
import { Label } from 'reactstrap';
import {VmInfo, VmInput} from "../../../generated-models";
import {RebootVm} from "../../../generated-models";
import {ShutdownVm} from "../../../generated-models";
import {StartVm} from "../../../generated-models";
import {VmEditOptions} from "../../../generated-models";
import Vm = VmInfo.Vm;



interface Props {
  vm : Vm
}
interface State {

}
class Power extends PureComponent<Props, State> {
  render()
  {
    const { vm } = this.props;

    const current_date = new Date();
    const start_date = new Date(vm.startTime);

    let uptime_text : string;

    switch (vm.powerState)
    {
      case VM_STATE_RUNNING:
        uptime_text = "I'm up since " +  start_date.toLocaleString() + ".";
        break;
      default:
        uptime_text = "I'm " + vm.powerState.toLowerCase() + ".";
    }


    return(
      <React.Fragment>
      <Row>
        <Col sm={6}>
      <FullHeightCard>
        <CardBody>
          <CardTitle>Power status</CardTitle>
        <CardText>{ uptime_text} (X days Y hours Z minutes W seconds)
        <br/>
        </CardText>
        </CardBody>
        <CardFooter>
        <div>
          { vm.powerState !== 'Halted' && (
            <RebootVm.Component>
              { vmReboot => (
                <Button size="lg" color="danger" onClick={() => vmReboot({variables:
                    {
                      uuid: vm.uuid
                    }})}>
                  Reboot
                </Button>
              )
              }
            </RebootVm.Component>)
              }
          {' '}
          {(vm.powerState !== 'Halted') ? (
            <ShutdownVm.Component>
              { vmShutdown => (
                <Button size="lg" color="primary" onClick={() => vmShutdown({variables: {uuid: vm.uuid}})}>
                  <FormattedMessage {...messages.halt}/>
                </Button>
              )
              }
            </ShutdownVm.Component>
            ):(
              <StartVm.Component>
                { vmStart => (
                  <Button size="lg" color="primary" onClick={() => vmStart({variables: {uuid: vm.uuid}})}>
                  <FormattedMessage {...messages.halt}/>
                  </Button>
                )
                }
              </StartVm.Component>
            )}
        </div>
        </CardFooter>
      </FullHeightCard>
        </Col>
        <Col sm={6}>
          {vm.interfaces.length > 0 && (
            <React.Fragment>
                {
                  vm.interfaces.map((value, index) => {
                    const ip = value.ip;
                    const ipv6 = value.ipv6;
                    return (<Card key={index}>
                      <CardBody>
                        <CardTitle>Network{" " + index}</CardTitle>
                        <CardText>
                        {ip && (<React.Fragment>
                            <Label> IP: {ip}</Label><br/>
                        </React.Fragment>)}
                        {ipv6 && (<Label> IPv6: {ipv6}</Label>)}
                        {(!ip && !ipv6) && (<Label>No data</Label>)}
                        </CardText>
                      </CardBody>
                    </Card>)

                  })
                }
            </React.Fragment>
          ) || (
            <h3>Connect your VM to a network to access it </h3>)
          }
        </Col>
      </Row>
        <Row>
          <Col sm={6}>
            <FullHeightCard>
              <CardBody>
                <CardTitle>Virtualization mode</CardTitle>
                {vm.powerState !== 'Halted' && (
                <CardSubtitle>Halt to switch mode</CardSubtitle>)}

                <CardText><h4>{vm.domainType.toUpperCase()}</h4></CardText>
              </CardBody>
              <CardFooter>
                <VmEditOptions.Component>
                  {
                    trigger => {
                      let buttonText : string;
                      let domain : string;

                      if (vm.domainType === 'hvm')
                      {
                        domain = 'pv';
                        buttonText = ' PV';
                      }
                      else
                      {
                        domain = 'hvm';
                        buttonText = ' HVM';
                      }
                      const inputObject : VmInput = {
                        uuid: vm.uuid,
                        domainType: domain
                      };

                    return (
                      <Button
                        disabled={vm.powerState !== 'Halted'}
                        size="lg"
                        color="info"
                        onClick={() => trigger({variables : {vm: inputObject}})}
                      >Switch to
                        {buttonText}
                      </Button>);
                    }
                  }
                </VmEditOptions.Component>
              </CardFooter>
            </FullHeightCard>
          </Col>
        </Row>
        <Row>
          <Col>
            <Card>
             <CardBody>
               <CardTitle>
                 Boot parameters
               </CardTitle>
               <CardText>

               </CardText>
             </CardBody>
            </Card>
          </Col>
        </Row>
        <Row>
          <Col>
            <Playbooks
            vms={[vm.uuid]}/>
          </Col>
        </Row>
      </React.Fragment>

    );
  }
}

export default Power;
