import React, {PureComponent} from 'react';
import {Button, Card, CardBody, CardFooter, CardText, CardTitle, Col, Row, Table} from 'reactstrap';
import NextTable from 'react-bootstrap-table-next';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import faCheck from '@fortawesome/fontawesome-free-solid/faCheck';
import {sizeFormatter} from "../../../utils/sizeFormatter";
import StorageAttach from "./storageAttach";

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
    };
    this.toggleVdiAttach = this.toggleVdiAttach.bind(this);
  }

  toggleVdiAttach()
  {
    this.setState(
      {
        vdiAttach: !this.state.vdiAttach,
      }
    )
  }
  render()
  {
    return (
      <React.Fragment>
      <Row>
        <Col sm={12}>
          <Card>
            <CardBody>
              <CardTitle>Virtual hard disks</CardTitle>
              <CardText>
                <NextTable
                  columns={columns}
                  data={this.props.diskInfo}
                  keyField="key"

                  />
              </CardText>
            </CardBody>
            <CardFooter>
              <Button size="lg" color="success" onClick={this.toggleVdiAttach}> Attach </Button>
              <Button size="lg" color="danger"> Detach </Button>
              {
                this.state.vdiAttach && (
                  <StorageAttach
                  uuid={this.props.data.get('uuid')}
                  caption="Hard disks"
                  />
                )
              }
            </CardFooter>
          </Card>

        </Col>
      </Row>
      <Row>
        <Col>
      <Card>
        <CardBody>
          <CardTitle>CDROM drives</CardTitle>
          <Table>
            <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Size</th>
            </tr>
            </thead>
            <tbody>
            <th scope="row">1</th>
            <td>0</td>
            <td>2 GB</td>
            </tbody>
          </Table>
        </CardBody>
      </Card>
        </Col>
      </Row>
      </React.Fragment>
    );
  }
}
export default Storage;
