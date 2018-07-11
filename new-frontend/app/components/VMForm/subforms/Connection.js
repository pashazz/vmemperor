import React from 'react';
import T from 'prop-types';
import messages from '../messages';
import InputMask from 'react-input-mask';
import { InputGroup, InputGroupAddon, InputGroupText, Input, FormGroup,Label,Col } from 'reactstrap';

const IPInput = (props) => (
  <InputMask mask="999.999.999.999" value={props.value} onChange={props.onChange}>
    {(inputProps) => <Input {...inputProps}  />}
  </InputMask>
);

function Connection({networkType, ip, gateway, netmask, dns0, dns1, onChange}) {
  return (
    <div style={{paddingLeft: 25}}>
      <FormGroup row>
        <Col>
    <Input type="select"
           id="networkType"
           name="networkType"
           onChange={onChange}
           value={networkType}>
      <option key="dhcp" value="dhcp">DHCP</option>
      <option key="static" value="static">Static IP</option>
    </Input>
        </Col>
      </FormGroup>
      {
        networkType !== 'dhcp' && (
          <React.Fragment>
            <FormGroup row ml-auto>
              <Label for="ip">IP</Label>
              <Col>
                <IPInput
                  id="ip"
                  name="ip"
                  onChange={onChange}
                  value={ip}/>
              </Col>
            </FormGroup>
            <FormGroup row ml-auto>
              <Label for="gateway">Gateway</Label>
              <Col>
                <IPInput
                  id="gateway"
                  name="gateway"
                  onChange={onChange}
                  value={gateway}/>
              </Col>
            </FormGroup>
            <FormGroup row>
              <Label for="netmask">Netmask</Label>
              <Col ml-auto>
                <IPInput
                  id="netmask"
                  name="netmask"
                  onChange={onChange}
                  value={netmask}/>
              </Col>
            </FormGroup>
            <FormGroup row>
              <Label for="dns0">DNS 1</Label>
              <Col>
                <IPInput
                  id="dns0"
                  name="dns0"
                  onChange={onChange}
                  value={dns0}/>
              </Col>
            </FormGroup>
            <FormGroup row>
              <Label for="dns1">DNS 2</Label>
              <Col>
                <IPInput
                  id="dns1"
                  name="dns1"
                  onChange={onChange}
                  value={dns0}/>
              </Col>
            </FormGroup>
          </React.Fragment>



        )
      }
    </div>
  );
}

Connection.propTypes = {
  networkType: T.any,
  ip: T.string,
  gateway: T.string,
  netmask: T.string,
  dns0: T.string,
  dns1: T.string,
  onChange: T.func.isRequired,
};

export default Connection;
