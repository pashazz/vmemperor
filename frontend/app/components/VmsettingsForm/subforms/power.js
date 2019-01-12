import React, {PureComponent} from 'react';
import T from 'prop-types';
import {Button, Card, CardTitle, CardText, Col, Row, CardFooter,CardBody, CardSubtitle, ButtonGroup} from 'reactstrap';
import FullHeightCard from 'components/FullHeightCard';
import {VM_STATE_RUNNING} from "../../../containers/App/constants";

//import DateDiff from 'utils/datediff';
import  VM from 'models/VM';

import { FormattedMessage } from 'react-intl';
import messages from  '../messages';
import Playbooks from "../../../containers/Playbooks";
import { Label } from 'reactstrap';
class Power extends PureComponent {
  static propTypes = {
    onReboot: T.func.isRequired,
    onHalt: T.func.isRequired,
    onConvertVm: T.func.isRequired,
    data: T.instanceOf(VM),
  };
  render()
  {
    const { data } = this.props;

    const current_date = new Date();
    const start_date = new Date(data.start_time);

    let uptime_text = null;

    switch (data.power_state)
    {
      case VM_STATE_RUNNING:
        uptime_text = "I'm up since " +  start_date.toLocaleString() + ".";
        break;
      default:
        uptime_text = "I'm " + data.power_state.toLowerCase() + ".";
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
          { data.power_state === 'Running' && (
        <Button size="lg" color="danger" onClick={this.props.onReboot}>Reboot  </Button>)}
          {' '}
        <Button size="lg" color="primary" onClick={this.props.onHalt}>{ (data.power_state === 'Halted') ?
          <FormattedMessage {...messages.turnon}/> :
          <FormattedMessage {...messages.halt}/>
        } </Button>
        </div>
        </CardFooter>
      </FullHeightCard>
        </Col>
        <Col sm={6}>
          {data.networks && (
            <React.Fragment>
                {
                  data.networks.map((value, key) => {
                    const ip = value.get('ip');
                    const ipv6 = value.get('ipv6');
                    return (<Card key={key}>
                      <CardBody>
                        <CardTitle>Network{" " + key}</CardTitle>
                        <CardText>
                        {ip && (<React.Fragment>
                            <Label> IP: {ip}</Label><br/>
                        </React.Fragment>)}
                        {ipv6 && (<Label> IPv6: {ipv6}</Label>)}
                        {(!ip && !ipv6) && (<Label>No data</Label>)}
                        </CardText>
                      </CardBody>
                    </Card>)

                  }).valueSeq().toArray()
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
                {data.power_state !== 'Halted' && (
                <CardSubtitle>Halt to switch mode</CardSubtitle>)}

                <CardText><h4>{data.domain_type.toUpperCase()}</h4></CardText>
              </CardBody>
              <CardFooter>
                <Button
                  disabled={data.power_state !== 'Halted'}
                  size="lg"
                  color="info"
                  onClick={this.props.onConvertVm}
                >Switch to
                  {data.domain_type === 'pv' ? ' HVM' : ' PV'}
                </Button>
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
            vmData={this.props.data}/>
          </Col>
        </Row>
      </React.Fragment>

    );
  }
}

export default Power;
