import React, {PureComponent} from 'react';
import T from 'prop-types';
import {Button, Card, CardTitle, CardText, Col, Row, CardFooter,CardBody, CardSubtitle, ButtonGroup} from 'reactstrap';
import FullHeightCard from 'components/FullHeightCard';
import {VM_STATE_RUNNING} from "../../../containers/App/constants";

class Power extends PureComponent {
  static propTypes = {
    onReboot: T.func.isRequired,
    onHalt: T.func.isRequired,
    data: T.any.isRequired
  };
  render()
  {
    const { data } = this.props;
    let uptime_text = null;
    switch (data.power_state)
    {
      case VM_STATE_RUNNING:
        uptime_text = "I'm up since " + data.start_time + ".";
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
        <Button size="lg" color="danger">Reboot</Button>{' '}
        <Button size="lg" color="primary">Halt</Button>
        </div>
        </CardFooter>
      </FullHeightCard>
        </Col>
        <Col sm={6}>
          <FullHeightCard>

            <CardBody>
              <CardTitle>Access</CardTitle>
              <CardSubtitle>IP addresses</CardSubtitle>
            <CardText>

             XXX.XXX.XXX.XXX (Network 1)<br/>

             XXX.XXX.XXX.YYY (Network 2)<br/>

            </CardText>
            </CardBody>
            <CardFooter>
              <div>
                <Button size="lg" color="success">Go to Desktop</Button>
              </div>
            </CardFooter>
          </FullHeightCard>

        </Col>
      </Row>
        <Row>
          <Col sm={6}>
            <FullHeightCard>
              <CardBody>
                <CardTitle>Virtualization mode</CardTitle>
                <CardSubtitle>Halt to switch mode</CardSubtitle>

                <CardText><h4>PV</h4></CardText>
              </CardBody>
              <CardFooter>
                <Button size="lg" color="info">Switch to HVM</Button>
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
      </React.Fragment>

    );
  }
}

export default Power;
