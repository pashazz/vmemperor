import React, {PureComponent} from 'react';
import {Button, Card, CardBody, CardFooter, CardText, CardTitle, Col, Row, Table, Collapse, UncontrolledAlert, ButtonGroup} from 'reactstrap';
import NextTable from 'react-bootstrap-table-next';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import faCheck from '@fortawesome/fontawesome-free-solid/faCheck';
import {sizeFormatter} from "../../../utils/sizeFormatter";
import StorageAttach from "./storageAttach";
import {vdilist} from "../../../api/vdi";
import isolist from "../../../api/isolist";

const checkBoxFormatter = (cell, row) =>
{
  if (cell)
  {
    return (
      <span>
        { cell && (<FontAwesomeIcon icon={faCheck}/>)}
      </span>
    )
  }
};


const columns = [
  {
    dataField: 'device',
    text: 'Name'

  },
  {
    dataField: 'type',
    text: 'Type',

  },
  {
    dataField: 'name_label',
    text: 'Disk name',

  },

  {
    dataField: 'virtual_size',
    text: 'Size',
    formatter: sizeFormatter,
  },
  {
    dataField: 'attached',
    text: 'Attached',
    formatter: checkBoxFormatter,
  },

  {
    dataField: 'bootable',
    text: 'Bootable',
    formatter: checkBoxFormatter,
  },


];


class Storage extends PureComponent {
  constructor(props)
  {
    super(props);
    this.state = {
      vdiAttach: false,
      isoAttach: false,
    };
    this.toggleVdiAttach = this.toggleVdiAttach.bind(this);
    this.toggleIsoAttach = this.toggleIsoAttach.bind(this);
  }

  toggleIsoAttach()
  {
    let set = {
      isoAttach: !this.state.isoAttach,
    };
    if (set.isoAttach)
      set.vdiAttach = false;
    this.setState(
      set
    );
  }
  toggleVdiAttach()
  {
    let set = {
      vdiAttach: !this.state.vdiAttach,
    };
    if (set.vdiAttach)
      set.isoAttach = false;
    this.setState(
      set
    );
  }
  render()
  {
    return (
      <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <CardBody>
              <CardTitle>Virtual disks</CardTitle>
              <CardText>
                <NextTable
                  columns={columns}
                  data={this.props.diskInfo}
                  keyField="key"

                  />
              </CardText>
            </CardBody>
            <CardFooter>
              <Button size="lg" color="success" onClick={this.toggleVdiAttach} active={this.state.vdiAttach} aria-pressed="true"> Attach virtual hard disk </Button>
              <Button size="lg" color="success" onClick={this.toggleIsoAttach} active={this.state.isoAttach} aria-pressed="true"> Attach ISO image </Button>
              <Button size="lg" color="danger"> Detach </Button>
              <Collapse id="collVdi"
                isOpen={this.state.vdiAttach}>
                <UncontrolledAlert color='info'>Double-click to attach a disk</UncontrolledAlert>
              <StorageAttach
                  uuid={this.props.data.get('uuid')}
                  caption="Hard disks"
                  fetch={vdilist}
                  showConnectedTo
                  />

                <ButtonGroup>
                  <Button>Create new disk</Button>
                  <Button>Delete</Button>
                </ButtonGroup>
              </Collapse>
              <Collapse id="collIso"
                        isOpen={this.state.isoAttach}>
                <UncontrolledAlert color='info'>Double-click to attach an ISO</UncontrolledAlert>
                <StorageAttach
                  uuid={this.props.data.get('uuid')}
                  caption="ISO images"
                  fetch={isolist}
                  showConnectedTo={false}
                />
              </Collapse>

            </CardFooter>
          </Card>

        </Col>
      </Row>
      </React.Fragment>
    );
  }
}
export default Storage;
